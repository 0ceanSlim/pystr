import json
import asyncio
import websockets

your_relay_url = "wss://nos.lol"
sender_pubkey = "16f1a0100d4cfffbcc4230e8e0e4290cc5849c1adc64d6653fda07c031b1074b"

async def listen_to_relay(your_pubkey, your_relay_url):
    uri = f"{your_relay_url}/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all kind 1 events
        subscription_id = "kind1"  # Shortened subscription ID
        await websocket.send(json.dumps(["REQ", subscription_id, {"kinds": [1]}]))

        while True:
            response = await websocket.recv()
            await handle_event(response, your_pubkey)

async def handle_event(event_json, your_pubkey):
    event = json.loads(event_json)
    if event[0] == "EVENT" and event[2]["kind"] == 9735:  # Zap receipt event
        await handle_metadata_receipt(event, your_pubkey)

async def handle_metadata_receipt(zap_receipt_event, your_pubkey):
    recipient_pubkey = None
    for tag in zap_receipt_event[2]["tags"]:
        if tag[0] == "p":
            recipient_pubkey = tag[1]

    if recipient_pubkey == your_pubkey:
        sender_pubkey = next((tag[1] for tag in zap_receipt_event[2]["tags"] if tag[0].lower() == "p"), None)
        sender_metadata = await get_metadata(sender_pubkey)
        print(f"Received zap receipt event metadata: {sender_metadata}")

async def get_metadata(pubkey):
    uri = f"{your_relay_url}/ws"
    async with websockets.connect(uri) as websocket:
        subscription_id = f"meta_{pubkey[:8]}"  # Shortened subscription ID
        subscription_payload = json.dumps(["REQ", subscription_id, {"kinds": [0], "authors": [pubkey]}])
        await websocket.send(subscription_payload)
        print(f"Sent metadata request for pubkey: {pubkey}")

        while True:
            response = await websocket.recv()
            print(f"Received response: {response}")
            event = json.loads(response)
            if event[0] == "EVENT" and event[2]["kind"] == 0:
                content = json.loads(event[2]["content"])
                return content  # Return the entire metadata content

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_metadata(sender_pubkey))
