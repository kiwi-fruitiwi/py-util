from dotenv import load_dotenv
import time
import discord
import os
import json

# TODO currently loading state.json doesn't preserve state after reboots

load_dotenv()
TOKEN = os.getenv('AGGREGATOR_BOT_TOKEN')
SOURCE_CHANNEL_ID = 1383875109613207603  # the channel with threads
TARGET_CHANNEL_ID = 1390389351187480606  # the repost channel

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True


client = discord.Client(intents=intents)
STATE_FILE = 'mirrorState.json'


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            print("[STATE LOADED]")
            print(json.dumps(state, indent=2))
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# This stores the mapping between original messages and reposts
# { source_message_id: target_message_id }
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
        if parent and parent.id == SOURCE_CHANNEL_ID:
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
                content_lines.append(f"`🔗` ({message_link})")
                last_post_times[thread_id] = current_time

            content_lines.append(message.content)
            content = "\n".join(content_lines)

            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())

            # Get or create the webhook for the target channel
            webhooks = await target_channel.webhooks()
            webhook = discord.utils.get(webhooks, name="Mirror Bot")
            if webhook is None:
                webhook = await target_channel.create_webhook(name="Mirror Bot")

            # Send the message using the webhook with the user's name and avatar
            sent_message = await webhook.send(
                content=content,
                username=message.author.display_name,
                avatar_url=message.author.avatar.url if message.author.avatar else None,
                files=files,
                wait=True
            )

            # update tracking
            last_thread_id = thread_id
            message_map[str(message.id)] = str(sent_message.id)
            save_state(message_map)
            print(f'[ SEND ] 📫 Sent message ID: {sent_message.id}')



@client.event
async def on_message_edit(before, after):
    print(f"[EDIT EVENT] message {after.id} edited")

    if after.author.bot:
        return

    if isinstance(after.channel, discord.Thread):
        parent = after.channel.parent
        if parent and parent.id == SOURCE_CHANNEL_ID:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                return

            # Find the reposted message ID
            target_message_id = message_map.get(str(after.id))
            if not target_message_id:
                print(f"No mapping found for edited message ID {after.id}")
                return

            try:
                target_message = await target_channel.fetch_message(int(target_message_id))

                escaped_name = after.channel.name.replace("🥝", "`🥝`")
                new_content = f"`{after.author.display_name} in 🧵→thread` {escaped_name} `EDIT`:\n{after.content}"
                await target_message.edit(content=new_content)

            except discord.NotFound:
                print(f"Original reposted message not found for ID {target_message_id}")


@client.event
async def on_message_delete(message):
    print(f"[DELETE EVENT] message {message.id} deleted")
    if message.author.bot:
        return

    if isinstance(message.channel, discord.Thread):
        parent = message.channel.parent
        if parent and parent.id == SOURCE_CHANNEL_ID:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                return

            reposted_id = message_map.get(str(message.id))
            if reposted_id:
                try:
                    reposted = await target_channel.fetch_message(int(reposted_id))
                    await reposted.delete()
                except discord.NotFound:
                    print(f"[FAIL] Message {reposted_id} not found in target channel")
                    pass

client.run(TOKEN)