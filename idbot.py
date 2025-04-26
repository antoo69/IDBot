import logging
import os
import re
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

TOKEN = os.getenv("TOKEN", "8033318643:AAHHrl-s2ZMCT895h7is6zSe35foQmtn8m8")
APP_ID = int(os.getenv("APP_ID", "23345148"))
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

def create_app():
    return Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)

app = create_app()

async def get_user_detail(user: User | Chat, client: Client = None) -> str:
    if not user:
        return "Tidak dapat mengambil info."
    return f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: <code>{user.id}</code>
🌐 Username: @{user.username if user.username else "Tidak ada"}
"""

def get_chat_detail(chat: Chat) -> str:
    return f"""
📢 Info Grup/Channel:
🏷 Nama: {chat.title}
🆔 ID: <code>{chat.id}</code>
🌐 Username: @{chat.username if chat.username else "Tidak ada"}
"""

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user = message.from_user
    text = await get_user_detail(user)
    await message.reply_text(
        text + "\nInfo lebih lanjut ketik /info \nStore aman dan terpercaya. Klik di bawah ini.",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Ferdi Store", url="https://t.me/FerdiStore")]
        ])
    )

@app.on_message(filters.command("info") & filters.private)
async def info_handler(client: Client, message: Message):
    usage_text = """🛠 *Cara Penggunaan Bot ID*
✅ Notes:
1. Ketik /start maka bot akan mengirim id akun anda
2. Cukup Kirimkan username anda, orang lain, group maupun channel: `@username`
3. Link seperti: `https://t.me/username`
4. Forward pesan dari pengguna, grup, atau channel
5. Tidak bisa untuk group/channel private
Bot akan otomatis mendeteksi dan membalas dengan informasi yang tersedia.
📌
Owner : @fsyrl9
Store : @FerdiStore
    """
    await message.reply_text(usage_text, quote=True)

@app.on_message(filters.forwarded & filters.private)
async def forward_handler(client: Client, message: Message):
    user = message.from_user
    forwarded_user = message.forward_from
    forwarded_chat = message.forward_from_chat

    teks = f"""
👤 Pengirim:
🆔 ID: <code>{user.id}</code>
Username: @{user.username if user.username else "Tidak ada"}
"""

    if forwarded_user:
        teks += f"""
📨 Asal Pesan:
👤 Dari user:
🆔 ID: <code>{forwarded_user.id}</code>
Username: @{forwarded_user.username if forwarded_user.username else "Tidak ada"}
"""

    if forwarded_chat:
        teks += f"""
📢 Dari Grup/Channel:
🏷 Nama: {forwarded_chat.title}
🆔 ID: <code>{forwarded_chat.id}</code>
🌐 Username: @{forwarded_chat.username if forwarded_chat.username else "Tidak ada"}
"""

    await message.reply_text(teks, quote=True)

@app.on_message(filters.text & filters.private & ~filters.command("info") & ~filters.command("start"))
async def private_handler(client: Client, message: Message):
    text = message.text

    if "t.me/+" in text or "t.me/joinchat/" in text:
        await message.reply_text(
            "Maaf, bot tidak dapat mengakses tautan undangan grup/channel private. "
            "Silakan gunakan username publik atau forward pesan dari grup/channel tersebut.",
            quote=True
        )
        return

    username = re.sub(r"@+|https://t.me/", "", text)
    funcs = [get_users, get_channel]

    result_text = ""
    for func in funcs:
        try:
            if func == get_users:
                result_text = await func(username)
            else:
                result_text = await func(username)
            if result_text:
                break
        except Exception:
            logging.error(traceback.format_exc())
            result_text = "Tidak dapat menemukan pengguna/grup." 

    await message.reply_text(result_text, quote=True)

async def get_users(username: str) -> str:
    user = await app.get_users(username)
    return await get_user_detail(user)

async def get_channel(username: str) -> str:
    peer = await app.resolve_peer(username)
    result = await app.invoke(functions.channels.GetChannels(id=[peer]))
    for ch in result.chats:
        return get_chat_detail(ch)
    return "Channel/Group tidak ditemukan."

if __name__ == '__main__':
    app.run()
