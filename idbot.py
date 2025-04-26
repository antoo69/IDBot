import logging
import os
import re
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions
from pyrogram.errors import BotMethodInvalid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

TOKEN = os.getenv("TOKEN", "8033318643:AAHHrl-s2ZMCT895h7is6zSe35foQmtn8m8")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

def create_app():
    return Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)

app = create_app()

async def get_user_detail(user: "User | Chat", client: Client = None) -> str:
    if user is None:
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

@app.on_message(filters.command(["start"], prefixes="/"))
async def start_handler(client: Client, message: Message):
    user = message.from_user
    text = await get_user_detail(user, client)
    await message.reply_text(
        text + "\nInfo lebih lanjut ketik /info \nStore aman dan terpercaya. Klik di bawah ini.",
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Ferdi Store", url="https://t.me/FerdiStore")]
        ])
    )

@app.on_message(filters.forwarded)
async def forward_handler(client: Client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    user = message.from_user

    if message.forward_from_chat:
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: <code>{user.id}</code>
  Username: @{user.username if user.username else "Tidak ada"}

📢 Dari Channel/Grup:
  Nama: {message.forward_from_chat.title}
  ID: <code>{message.forward_from_chat.id}</code>
  Username: @{message.forward_from_chat.username if message.forward_from_chat.username else "Tidak ada"}
        """
    else:
        fwd_details = await get_user_detail(fwd, client) if fwd else "Tidak bisa mengambil informasi."
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: <code>{user.id}</code>
  Username: @{user.username if user.username else "Tidak ada"}

👤 Pesan asli dari:
{fwd_details}
        """

    await message.reply_text(me, quote=True)

@app.on_message(filters.command("info"))
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

@app.on_message(filters.text & filters.private & ~filters.command("info"))
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
    text = ""

    for func in funcs:
        try:
            if func == get_users:
                text = await func(username, client)
            else:
                text = await func(username)
            if text:
                break
        except Exception as e:
            logging.error(traceback.format_exc())
            text = str(e)

    await message.reply_text(text, quote=True)

async def get_users(username, client):
    user = await app.get_users(username)
    return await get_user_detail(user, client)

async def get_channel(username):
    peer = await app.resolve_peer(username)
    result = await app.invoke(functions.channels.GetChannels(id=[peer]))
    for ch in result.chats:
        return get_chat_detail(ch)
    return "Channel/Group tidak ditemukan."

@app.on_message(filters.text & filters.private)
async def detect_private_group_or_channel(client, message: Message):
    chat = message.chat
    if chat.username is None:
        chat_type = "Grup" if chat.type in ["group", "supergroup"] else "Channel"
        await message.reply_text(
            f"📢 Terdeteksi {chat_type} private:\n🏷 Nama: {chat.title}\n🆔 ID: <code>-100{chat.id}</code>",
            quote=True
        )

if __name__ == '__main__':
    app.run()
