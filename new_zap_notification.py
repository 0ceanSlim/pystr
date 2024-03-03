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
        #sender_pubkey = next((value for key, value in zap_receipt_event[2]["tags"] if key == "P"), None)
        print(f"Received a zap") # from {sender_pubkey} to {recipient_pubkey}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen_to_relay())
