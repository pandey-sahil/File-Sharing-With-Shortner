import base64
import re
import asyncio
import logging
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

logger = logging.getLogger(__name__)

async def is_subscribed(filter, client, update):
    """Check if the user is subscribed to the specified channel."""
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]

async def encode(string):
    """Encode a string using URL-safe Base64 encoding."""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string):
    """Decode a URL-safe Base64 encoded string."""
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    return base64.urlsafe_b64decode(base64_bytes).decode("ascii")

async def get_messages(client, message_ids):
    """Retrieve messages from the specified chat using their IDs."""
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temp_ids = message_ids[total_messages:total_messages + 200]
        try:
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=temp_ids)
            messages.extend(msgs)
        except FloodWait as e:
            logger.warning(f"Flood wait encountered, sleeping for {e.x} seconds.")
            await asyncio.sleep(e.x)
            continue  # Retry fetching messages after waiting
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
        total_messages += len(temp_ids)
    return messages

async def get_message_id(client, message):
    """Extract message ID from a message, if applicable."""
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = re.compile(r"https://t.me/(?:c/)?(.*?)/(\d+)")
        matches = pattern.match(message.text)
        if matches:
            channel_id = matches.group(1)
            msg_id = int(matches.group(2))
            if (channel_id.isdigit() and f"-100{channel_id}" == str(client.db_channel.id)) or \
                    (channel_id == client.db_channel.username):
                return msg_id
    return 0

def get_readable_time(seconds: int) -> str:
    """Convert seconds into a human-readable time format."""
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(map(str, time_list))
    return up_time

# Create a custom filter for checking subscription
subscribed = filters.create(is_subscribed)
