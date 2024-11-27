from pyrogram import Client, filters
from pyrogram.types import Message
from helper_func import get_message_id  # Import the function from helper_func.py

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
