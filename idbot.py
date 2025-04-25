#!/usr/local/bin/python3
# coding: utf-8

author = "@fsyrl9"

import logging
import os
import re
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

# Bot credentials
TOKEN = os.getenv("TOKEN", "8033318643:AAHHrl-s2ZMCT895h7is6zSe35foQmtn8m8")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

def create_app():
    return Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)

app = create_app()

async def get_user_detail(user: "User", client: Client = None) -> str:
    if user is None:
        return "❌ Tidak bisa mengambil informasi pengguna."
    
    return f"""
👤 Pengguna:
🆔 ID: {user.id}
👤 Nama: {user.first_name}
🌐 Username: @{user.username if user.username else "Tidak ada"}
"""

def get_chat_detail(chat: "Chat") -> str:
    return f"""
📢 Grup/Channel:
🆔 ID: {chat.id}
🏷 Nama: {chat.title}
🌐 Username: @{chat.username if chat.username else "Tidak ada"}
"""

# /start command
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    text = await get_user_detail(message.from_user, client)
    await message.reply_text(
        text + "\n\nStore aman dan terpercaya 👇",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🛒 Ferdi Store", url="https://t.me/fsyrl9")]]
        )
    )

# /info command
@app.on_message(filters.command(["info"]))
async def info_command(client: Client, message: Message):
    await message.reply_text(
        """🛠 *Cara Penggunaan Bot ID*

✅ Kirim:
1. Username seperti: `@username`
2. Link seperti: `https://t.me/username`
3. Forward pesan dari pengguna, grup, atau channel

Bot akan otomatis mendeteksi dan membalas dengan informasi yang tersedia.

📌 Tidak perlu pakai perintah /getgc lagi.
        """,
        quote=True
    )

# Handle forwarded messages
@app.on_message(filters.forwarded)
async def handle_forwarded(client: Client, message: Message):
    user = message.forward_from
    chat = message.forward_from_chat

    if user:
        text = await get_user_detail(user, client)
    elif chat:
        text = get_chat_detail(chat)
    else:
        text = "❌ Tidak bisa mengambil informasi dari pesan ini."

    await message.reply_text(text, quote=True)

# Handle text messages for @username or t.me/...
@app.on_message(filters.text & filters.private)
async def handle_text(client: Client, message: Message):
    username = message.text.strip()

    # Bersihkan dari awalan @ atau link t.me
    username = re.sub(r"^(https?://)?(t\.me/|@)", "", username)

    try:
        try:
            user = await client.get_users(username)
            text = await get_user_detail(user, client)
        except Exception:
            peer = await client.resolve_peer(username)
            result = await client.invoke(functions.channels.GetChannels(id=[peer]))
            chat = result.chats[0]
            text = get_chat_detail(chat)
    except Exception as e:
        logging.error(traceback.format_exc())
        text = f"❌ Gagal mengambil data.\n{str(e)}"

    await message.reply_text(text, quote=True)

if __name__ == "__main__":
    app.run()
