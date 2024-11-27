import logging
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS, PUBLIC_EARN_API_KEY, CHANNEL_ID  # Change DB_CHANNEL_ID to CHANNEL_ID

# Logger setup
logger = logging.getLogger(__name__)

# Helper function to encode
async def encode(data):
    # Implement your encoding logic here (base64 encoding or other)
    return data

# Function to get total clicks (Placeholder function, replace it with actual logic)
async def get_total_clicks(short_url):
    return 208  # Example click count

# Shorten URL using PublicEarn API
async def shorten_link(long_url):
    try:
        api_url = f"https://publicearn.in/api?api={PUBLIC_EARN_API_KEY}&url={long_url}&format=text"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Failed to shorten URL. Response Status: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error while shortening link: {e}")
        return None

@Client.on_message(filters.command("addlink") & filters.private & filters.user(ADMINS))
async def add_link_handler(client: Client, message: Message):
    try:
        # Ask for the channel message or URL from the user
        link_message = await client.ask(
            text="Forward Message from the Channel (with Quotes) or Send the Channel Post Link.",
            chat_id=message.from_user.id,
            filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
            timeout=60
        )
        msg_id = await get_message_id(client, link_message)

        if not msg_id:
            await link_message.reply("❌ Error: This forwarded post is not from my Channel or the link is invalid.", quote=True)
            return

        # Step 2: Shorten the URL
        original_url = f"https://t.me/{client.username}?start={await encode(f'get-{msg_id * abs(CHANNEL_ID)}')}"
        short_url = await shorten_link(original_url)

        if not short_url:
            await message.reply("❌ Failed to shorten the link. Please try again later.", quote=True)
            return

        # Step 3: Get total clicks on the shortened link
        total_clicks = await get_total_clicks(short_url)

        # Step 4: Send the message with buttons (Original and Shortened URL)
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
