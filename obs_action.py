import json
import asyncio
import websockets
from obswebsocket import obsws, requests

def load_config(file_path):
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file not found at {file_path}.")
        return None

async def listen_to_relay(your_pubkey, your_relay_url, obs_host, obs_port, obs_password):
    uri = f"{your_relay_url}/ws"

    # Create OBS connection
    obs = obsws(obs_host, obs_port, obs_password)
    obs.connect()

    async with websockets.connect(uri) as websocket:
        # Subscribe to all kind 3 events
        subscription_id = "kind_3_events"  # Replace with a unique identifier
        await websocket.send(json.dumps(["REQ", subscription_id, {"kinds": [3]}]))

        while True:
            response = await websocket.recv()
            await handle_event(response, your_pubkey, obs)  # Pass the OBS connection to handle_event

async def handle_event(event_json, your_pubkey, obs):
    event = json.loads(event_json)
    if event[0] == "EVENT":
        event_data = event[2]
        if event_data["kind"] == 3:  # Follow list event
            await handle_follow_list(event_data, your_pubkey, obs)  # Pass the OBS connection to handle_follow_list


async def handle_follow_list(follow_list_event, your_pubkey, obs):
    if "tags" in follow_list_event:
        # Extract the list of "p" tags from the follow list event
        p_tags = [tag for tag in follow_list_event["tags"] if tag[0] == "p"]

        # Check if your pubkey is the last entry in the "p" tags
        if p_tags and p_tags[-1][1] == your_pubkey:
            print(f"You have a new follower: {follow_list_event.get('pubkey', '')}")

            # Toggle the specified source group in OBS
            source_group_name = "heyguys"  # Replace with the name of your source group
            scene_name = "Escape From Tarkov"  # Replace with the name of your scene
            await toggle_source_group(obs, scene_name, source_group_name)

async def toggle_source_group(obs, scene_name, source_group_name):
    # Get the list of scene items in the specified scene
    scene_items = obs.call(requests.GetSceneItemList(sceneName=scene_name))

    # Find the source group item in the list
    source_group_item = next((item for item in scene_items.getSceneItems() if item["name"] == source_group_name), None)

    if source_group_item:
        # Enable or disable the visibility of the source group item
        obs_response = obs.call(
            requests.SetSceneItemProperties(item=source_group_item["name"], scene=scene_name, visible=not source_group_item["visible"])
        )
        print(f"Toggle Response: {obs_response}")
        print(f"Toggled source group '{source_group_name}' in scene '{scene_name}'.")
    else:
        print(f"Source group '{source_group_name}' not found in scene '{scene_name}'.")

if __name__ == "__main__":
    config_path = 'config.json'
    config = load_config(config_path)

    if config:
        asyncio.get_event_loop().run_until_complete(listen_to_relay(
            config["your_pubkey"], config["your_relay_url"],
            config["obs_host"], config["obs_port"], config["obs_password"]
        ))
