import aiohttp
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import PUBLIC_EARN_API_KEY, ADMINS
from bot import Bot
from helper_func import encode, get_message_id

# Logger setup
logger = logging.getLogger(__name__)

# Function to get total clicks (Placeholder function, you can adjust this)
async def get_total_clicks(short_url):
    return 208  # Example click count (Replace with actual API call or database logic)

# Batch Command
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    # Loop for getting the first message from DB Channel
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes) or Send the DB Channel Post Link.",
                chat_id=message.from_user.id, 
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)), 
                timeout=60
            )
        except asyncio.TimeoutError:
            await message.reply("❌ Timeout. You took too long to respond.")
            return
        except Exception as e:
            await message.reply(f"❌ Error occurred: {str(e)}")
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error: This forwarded post is not from my DB Channel or the link is invalid.", quote=True)
            continue

    # Loop for getting the second message from DB Channel
    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes) or Send the DB Channel Post Link.",
                chat_id=message.from_user.id, 
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)), 
                timeout=60
            )
        except asyncio.TimeoutError:
            await message.reply("❌ Timeout. You took too long to respond.")
            return
        except Exception as e:
            await message.reply(f"❌ Error occurred: {str(e)}")
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error: This forwarded post is not from my DB Channel or the link is invalid.", quote=True)
            continue

    # Construct the link
    try:
        string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
        base64_string = await encode(string)
        link = f"https://telegram.me/{client.username}?start={base64_string}"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
        )
        await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
    except Exception as e:
        await message.reply(f"❌ Failed to generate link: {str(e)}")

# Genlink Command
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes) or Send the DB Channel Post Link.",
                chat_id=message.from_user.id, 
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)), 
                timeout=60
            )
        except asyncio.TimeoutError:
            await message.reply("❌ Timeout. You took too long to respond.")
            return
        except Exception as e:
            await message.reply(f"❌ Error occurred: {str(e)}")
            return

        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error: This forwarded post is not from my DB Channel or the link is invalid.", quote=True)
            continue

    # Construct the link
    try:
        base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
        link = f"https://telegram.me/{client.username}?start={base64_string}"
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
        )
        await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
    except Exception as e:
        await message.reply(f"❌ Failed to generate link: {str(e)}")

# Addlink Command (Admin-only)
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('addlink'))
async def add_link_handler(client: Client, message: Message):
    try:
        # Step 1: Ask for the channel message or URL from the user
        link_message = await client.ask(
            text="Forward Message from the DB Channel (with Quotes) or Send the DB Channel Post Link.",
            chat_id=message.from_user.id,
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        msg_id = await get_message_id(client, link_message)

        if not msg_id:
            await link_message.reply("❌ Error: This forwarded post is not from my DB Channel or the link is invalid.", quote=True)
            return

        # Step 2: Shorten the URL using PublicEarn API
        original_url = f"https://t.me/{client.username}?start={await encode(f'get-{msg_id * abs(client.db_channel.id)}')}"
        short_url = await shorten_link(original_url)

        if not short_url:
            await message.reply("❌ Failed to shorten the link. Please try again later.", quote=True)
            return

        # Step 3: Get total clicks on the shortened link
        total_clicks = await get_total_clicks(short_url)

        # Step 4: Send the message with the two buttons (Original and Shortened URL)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔗 Open Channel Link", url=original_url)],
                [InlineKeyboardButton("🔗 Open Shortened URL", url=short_url)],
                [InlineKeyboardButton("Total Clicks", url=short_url)]  # For demonstration
            ]
        )

        await link_message.reply_text(
            f"✅ **Link Added Successfully!**\n\n"
            f"**Original Link:** {original_url}\n"
            f"**Shortened Link:** {short_url}\n"
            f"**Total Clicks:** {total_clicks}",
            reply_markup=reply_markup,
            quote=True
        )

    except Exception as e:
        logger.error(f"Error in add_link_handler: {e}")
        await message.reply("❌ An error occurred while processing your request. Please try again.", quote=True)


# Function to shorten link using PublicEarn API
async def shorten_link(long_url):
    """
    Uses the PublicEarn API to shorten a given URL.
    """
    try:
        api_url = f"https://publicearn.in/api?api={PUBLIC_EARN_API_KEY}&url={long_url}&format=text"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short_url = await response.text()
                    return short_url.strip()
                else:
                    logger.error(f"Failed to shorten URL. Response Status: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error while shortening link: {e}")
        return None
