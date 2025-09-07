from dotenv import load_dotenv
from datetime import datetime
import time
import discord
import os
import json

# TODO currently loading state.json doesn't preserve state after reboots!ext
load_dotenv()
TOKEN = os.getenv('AGGREGATOR_BOT_TOKEN')
SOURCE_CHANNEL_ID_LIST = {
    1403766917709172889, # arena open / direct
    1399393869854150787, # the channel with threads: 🪐ᴱᴼᴱ PD
}

TARGET_CHANNEL_ID = 1390389351187480606  # the repost channel: current-games

# arena open / direct 1403766917709172889
# 🪐ᴱᴼᴱ PD 1399393869854150787


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True


client = discord.Client(intents=intents)
STATE_FILE = 'mirrorState.json'


def getFormattedTime():
	now = datetime.now()
	# format: 11:05:23am 2025.Sept.7
	return now.strftime("%I:%M:%S%p %Y.%b.%d")


# unsure if this actually works in practice between reboots T_T
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            print("[ STATE LOADED ]")
            print(json.dumps(state, indent=2))
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# this stores the mapping between original messages and reposts
message_map = load_state()


@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}')


# Tracks last used thread ID and timestamps
last_thread_id = None
last_post_times = {}  # {thread_id: unix_timestamp}
THREAD_TIMEOUT = 600  # 10 minutes


@client.event
async def on_message(message):
    global last_thread_id

    if message.author.bot:
        return

    if isinstance(message.channel, discord.Thread):
        parent = message.channel.parent
        if parent and parent.id in SOURCE_CHANNEL_ID_LIST:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                print("Could not find target channel.")
                return

            thread_id = message.channel.id
            current_time = time.time()
            last_time = last_post_times.get(thread_id, 0)
            should_print_header = (thread_id != last_thread_id) or (current_time - last_time > THREAD_TIMEOUT)

            escaped_name = message.channel.name.replace("🥝", "")

            content_lines = []
            if should_print_header:
                content_lines.append(f'`🧵 {escaped_name}`')
                message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                last_post_times[thread_id] = current_time

            content_lines.append(message.content)

            if should_print_header:
                content_lines.append(f"\n`message link:` {message_link}")
            content = "\n".join(content_lines)

            files = [await attachment.to_file() for attachment in message.attachments]

            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, name="Mirror Bot")
            if webhook is None:
                webhook = await target_channel.create_webhook(name="Mirror Bot")

            sent_message = await webhook.send(
                content=content,
                username=message.author.display_name,
                avatar_url=message.author.avatar.url if message.author.avatar else None,
                files=files,
                wait=True
            )

            last_thread_id = thread_id
            message_map[str(message.id)] = {
                "mirrored_id": str(sent_message.id),
                "webhook_id": webhook.id
            }
            save_state(message_map)
            print(f'{getFormattedTime()} [ SEND ] 📫 Sent message ID: {sent_message.id}')


@client.event
async def on_message_edit(before, after):
    print(f"{getFormattedTime()} [ EDIT EVENT ] ✒️ message {after.id} edited")

    if after.author.bot:
        return

    if isinstance(after.channel, discord.Thread):
        parent = after.channel.parent
        if parent and parent.id in SOURCE_CHANNEL_ID_LIST:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                return

            info = message_map.get(str(after.id))
            if not info:
                print(f"No mapping found for edited message ID {after.id}")
                return

            webhook_id = info["webhook_id"]
            mirrored_id = int(info["mirrored_id"])

            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, id=webhook_id)
            if webhook is None:
                print(f"Webhook ID {webhook_id} not found in target channel")
                return

            new_content = after.content
            try:
                await webhook.edit_message(
                    message_id=mirrored_id,
                    content=new_content
                )
                print(f"[ EDITED ] ✒️ Updated mirrored message ID: {mirrored_id}")
            except discord.NotFound:
                print(f"Original mirrored message not found for ID {mirrored_id}")


@client.event
async def on_message_delete(message):
    print(f"{getFormattedTime()} [ DELETE EVENT ] message {message.id} deleted")

    if message.author.bot:
        return

    if isinstance(message.channel, discord.Thread):
        parent = message.channel.parent
        if parent and parent.id in SOURCE_CHANNEL_ID_LIST:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                return

            info = message_map.get(str(message.id))
            if not info:
                print(f"No mapping found for deleted message ID {message.id}")
                return

            webhook_id = info["webhook_id"]
            mirrored_id = int(info["mirrored_id"])

            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, id=webhook_id)
            if webhook is None:
                print(f"Webhook ID {webhook_id} not found in target channel")
                return

            try:
                await webhook.delete_message(mirrored_id)
                print(f"[ DELETED ] 🔍 Removed mirrored message ID: {mirrored_id}")
            except discord.NotFound:
                print(f"[ FAIL ] Message {mirrored_id} not found in target channel")


client.run(TOKEN)