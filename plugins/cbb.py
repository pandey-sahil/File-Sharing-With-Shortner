from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    """Handles callback queries from inline buttons."""
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text=f'''<b>Step 1. Join the channel 
Step 2. Then tap on the link again or come back to the bot and click on Try Again. 
Step 3. Tap on Start and Done ✅
</b>''',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data="close")
                    ]
                ]
            )
        )
    
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except Exception as e:
            logger.error(f"Error deleting the replied message: {str(e)}")
            await query.message.reply_text("Could not delete the previous message.")
