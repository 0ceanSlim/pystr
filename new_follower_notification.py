import json
import asyncio
import websockets

def load_config(file_path):
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file not found at {file_path}.")
        return None

async def listen_to_relay(your_pubkey,your_relay_url):
    uri = f"{your_relay_url}/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all kind 3 events
        subscription_id = "kind_3_events"  # Replace with a unique identifier
        await websocket.send(json.dumps(["REQ", subscription_id, {"kinds": [3]}]))

        while True:
            response = await websocket.recv()
            await handle_event(response, your_pubkey)  # Await the handle_event coroutine

async def handle_event(event_json, your_pubkey):
    event = json.loads(event_json)
    if event[0] == "EVENT":
        event_data = event[2]
        if event_data["kind"] == 3:  # Follow list event
            await handle_follow_list(event_data, your_pubkey)  # Await the handle_follow_list coroutine

async def handle_follow_list(follow_list_event, your_pubkey):
    if "tags" in follow_list_event:
        # Extract the list of "p" tags from the follow list event
        p_tags = [tag for tag in follow_list_event["tags"] if tag[0] == "p"]

        # Check if your pubkey is the last entry in the "p" tags
        if p_tags and p_tags[-1][1] == your_pubkey:
            print(f"You have a new follower: {follow_list_event.get('pubkey', '')}")

if __name__ == "__main__":
    config_path = 'config.json'
    config = load_config(config_path)

    if config:
        asyncio.get_event_loop().run_until_complete(listen_to_relay(config["your_pubkey"], config["your_relay_url"]))
