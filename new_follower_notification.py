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
        # Check if your pubkey is in the list of "p" tags
        your_pubkey_in_list = any(tag[0] == "p" and tag[1] == your_pubkey for tag in follow_list_event["tags"])
        
        if your_pubkey_in_list:
            # If your pubkey is in the list, print the author as a follower
            author_pubkey = follow_list_event.get("pubkey", "")
            if author_pubkey:
                print(f"{author_pubkey} is a new follower!")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(listen_to_relay())
    
    #TODO Fix for intended effect
## Right now, this prints when someone that has you in thier follow list, follows someone.
# It was intended to show when someone follows you, and that works but it's looking for 
# kind 3 events and If I'm in it, I get a print out. So this also print if someone follows me 
# already follows anyone else. 