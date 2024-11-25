from plugins import ratelimiter
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


# Batch Command
@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
# @ratelimiter
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
