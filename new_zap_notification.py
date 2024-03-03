import json
import asyncio
import websockets

# Replace these values with your own Nostr account details
your_pubkey = "16f1a0100d4cfffbcc4230e8e0e4290cc5849c1adc64d6653fda07c031b1074b"
your_relay_url = "wss://nos.lol"

async def listen_to_relay():
    uri = f"{your_relay_url}/ws"
    async with websockets.connect(uri) as websocket:
        print("WebSocket connection established.")

        # Subscribe to "zap receipt" events
        subscription_id = "zap_receipts"  # Replace with a unique identifier
        subscription_payload = json.dumps(["REQ", subscription_id, {"kinds": [9735]}])
        print(f"Subscribing with payload: {subscription_payload}")
        await websocket.send(subscription_payload)

        while True:
            response = await websocket.recv()
            # print(f"Received response: {response}")
            await handle_event(response)

async def handle_event(event_json):
    event = json.loads(event_json)
    # print(f"Received event: {event}")

    if event[0] == "EVENT" and event[2]["kind"] == 9735:  # Zap receipt event
        await handle_zap_receipt(event)

async def handle_zap_receipt(zap_receipt_event):
    recipient_pubkey = None

    for tag in zap_receipt_event[2]["tags"]:
        if tag[0] == "p":
            recipient_pubkey = tag[1]
            # print(f"{recipient_pubkey}")

    if recipient_pubkey == your_pubkey:
        sender_pubkey = next((value for key, value in zap_receipt_event[2]["tags"] if key.lower() == "p"), None)

        bolt11_invoice = next((value for key, value in zap_receipt_event[2]["tags"] if key == "bolt11"), None)
        if bolt11_invoice:
                amount_pos = bolt11_invoice.find("lnbc") + 4  # Position of the amount in the string
                amount_str = ""
                while amount_pos < len(bolt11_invoice) and (bolt11_invoice[amount_pos].isdigit() or bolt11_invoice[amount_pos] in "upm"):
                    amount_str += bolt11_invoice[amount_pos]
                    amount_pos += 1

                amount_multiplier = amount_str[-1]
                amount_value = int(amount_str[:-1]) if amount_str[:-1].isdigit() else 1
                
                if amount_multiplier == "u":
                    amount_sats = amount_value * 100
                elif amount_multiplier == "m":
                    amount_sats = amount_value * 100000
                elif amount_multiplier == "p":
                    amount_sats = amount_value // 1000
                elif amount_multiplier == "n":
                    amount_sats= amount_value // 10
                else:
                    amount_sats = amount_value

        print(f"Received a zap from {sender_pubkey} for {amount_sats} sats") # from {sender_pubkey} to {recipient_pubkey}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen_to_relay())
