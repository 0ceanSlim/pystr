import json
import asyncio
import websockets

# Replace these values with your own Nostr account details
your_pubkey = "16f1a0100d4cfffbcc4230e8e0e4290cc5849c1adc64d6653fda07c031b1074b"
your_relay_url = "wss://nos.lol"

async def listen_to_relay():
    uri = f"{your_relay_url}/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all kind 3 events
        subscription_id = "kind_3_events"  # Replace with a unique identifier
        await websocket.send(json.dumps(["REQ", subscription_id, {"kinds": [3]}]))

        while True:
            response = await websocket.recv()
            await handle_event(response)  # Await the handle_event coroutine

async def handle_event(event_json):
    event = json.loads(event_json)
    if event[0] == "EVENT":
        event_data = event[2]
        if event_data["kind"] == 3:  # Follow list event
            await handle_follow_list(event_data)  # Await the handle_follow_list coroutine

async def handle_follow_list(follow_list_event):
    if "tags" in follow_list_event:
        # Extract the list of "p" tags from the follow list event
        p_tags = [tag for tag in follow_list_event["tags"] if tag[0] == "p"]

        # Check if your pubkey is the last entry in the "p" tags
        if p_tags and p_tags[-1][1] == your_pubkey:
            print(f"You have a new follower: {follow_list_event.get('pubkey', '')}")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen_to_relay())
