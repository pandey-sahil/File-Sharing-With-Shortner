import aiohttp
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import PUBLIC_EARN_API_KEY, ADMINS

# Logger setup
logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command('shortlink'))
async def short_link_handler(client: Client, message: Message):
    """
    Command to shorten a given link using the PublicEarn API.
    """
    try:
        # Ask for the link to shorten
        link_message = await client.ask(
            text="Please send the link you want to shorten:",
            chat_id=message.chat.id,
            filters=filters.text,
            timeout=60
        )
        long_url = link_message.text.strip()

        # Validate the API Key
        if not PUBLIC_EARN_API_KEY:
            await message.reply("❌ API Key for PublicEarn is missing! Please configure it in `config.py`.", quote=True)
            return

        # Generate the shortened URL
        short_url = await shorten_link(long_url)

        if short_url:
            await message.reply_text(
                f"✅ Link Shortened Successfully!\n\n**Original Link:** {long_url}\n**Shortened Link:** {short_url}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔗 Open Link", url=short_url)]]
                ),
                quote=True
            )
        else:
            await message.reply("❌ Failed to shorten the link. Please try again later.", quote=True)

    except Exception as e:
        logger.error(f"Error in short_link_handler: {e}")
        await message.reply("❌ An error occurred while processing your request. Please try again.", quote=True)


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
