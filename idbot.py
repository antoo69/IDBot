#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s [%(levelname)s]: %(message)s"
)

# Ambil Token & API dari Environment atau Hardcoded (Ganti Sesuai Kebutuhan)
TOKEN = os.getenv("TOKEN", "7568080253:AAFTljQwDwRoP7D1IxmgTcN2Gw1OS-OkFSk")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

# Inisialisasi Bot
app = Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)


@app.on_message(filters.command("start"))
def start_handler(client, message):
    chat_id = message.chat.id
    user = message.from_user

    user_details = f"""
<b>👤 Nama:</b> <a href="tg://user?id={user.id}">{user.first_name}</a>
<b>🆔 ID:</b> <code>{user.id}</code>
<b>🌐 Username:</b> @{user.username if user.username else "Tidak ada"}

🚀 Selamat datang di <b>Ferdi Store</b>! Klik tombol di bawah ini untuk info lebih lanjut.
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])

    try:
        client.send_message(
            chat_id,
            user_details,
            reply_markup=keyboard,
            parse_mode="html"
        )
        logging.info(f"✅ /start diproses untuk {user.id}")
    except Exception as e:
        logging.error(f"❌ Error saat mengirim /start: {e}")


if __name__ == "__main__":
    logging.info("🚀 Bot Sedang Berjalan...")
    app.run()
