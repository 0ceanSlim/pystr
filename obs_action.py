import json
import asyncio
import websockets
from simpleobsws import obsws, requests

def load_config(file_path):
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file not found at {file_path}.")
        return None

async def listen_to_relay_and_control_obs(config):
    obs = obsws(config["obs_host"], config["obs_port"], config["obs_password"])
    await obs.connect()

    uri = f"{config['your_relay_url']}/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all kind 3 events
        subscription_id = "kind_3_events"  # Replace with a unique identifier
        await websocket.send(json.dumps(["REQ", subscription_id, {"kinds": [3]}]))

        while True:
            response = await websocket.recv()
            await handle_event(response, config, obs)  # Await the handle_event coroutine

async def handle_event(event_json, config, obs):
    event = json.loads(event_json)
    if event[0] == "EVENT":
        event_data = event[2]
        if event_data["kind"] == 3:  # Follow list event
            await handle_follow_list(event_data, config, obs)  # Await the handle_follow_list coroutine

async def handle_follow_list(follow_list_event, config, obs):
    if "tags" in follow_list_event:
        # Extract the list of "p" tags from the follow list event
        p_tags = [tag for tag in follow_list_event["tags"] if tag[0] == "p"]

        # Check if your pubkey is the last entry in the "p" tags
        if p_tags and p_tags[-1][1] == config["your_pubkey"]:
            print(f"You have a new follower: {follow_list_event.get('pubkey', '')}")

            # Now, you can control OBS source group as per your requirement.
            await control_obs_source_group(obs)

async def control_obs_source_group(obs):
    # Replace "YourSourceGroup" with the actual name of your source group in OBS
    source_group_name = "YourSourceGroup"

    # Toggle the visibility of the source group
    await obs.call(requests.SetSourceRender(sourceGroup=source_group_name, render=not obs.is_rendering_source(source_group_name)))

if __name__ == "__main__":
    config_path = 'config.json'
    config = load_config(config_path)

    if config:
        asyncio.get_event_loop().run_until_complete(listen_to_relay_and_control_obs(config))
