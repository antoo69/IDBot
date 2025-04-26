import logging
import os
import re
import traceback
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw import functions
from pyrogram.errors import UsernameNotOccupied

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
👤 Nama: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: `<code>{user.id}</code>`
🌐 Username: @{user.username if user.username else "Tidak ada"}
"""

def get_chat_detail(chat: Chat) -> str:
    return f"""
📢 Info Grup/Channel:
🏷 Nama: {chat.title}
🆔 ID: `-100<code>{chat.id}</code>`
🌐 Username: @{chat.username if chat.username else "Tidak ada"}
"""

def format_user_info(user: User, prefix="👤") -> str:
    created_date = "newer than 10/2021 (?)"
    if user.id < 1700000000:  # Rough estimate for accounts before 10/2021
        created_date = "~ 11/2020 (?)"
        
    username_text = f"{user.username} (https://t.me/{user.username})" if user.username else "None"
    
    return f"""{prefix}
 ├ id: `{user.id}`
 ├ is_bot: {str(user.is_bot).lower()}
 ├ first_name: {user.first_name}
 ├ username: {username_text}
 ├ language_code: {user.language_code if user.language_code else 'None'} (-)
 ├ is_premium: {str(user.is_premium).lower() if user.is_premium is not None else 'None'}
 └ created: {created_date}"""

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
    forward_sender_name = message.forward_sender_name
    
    response = format_user_info(user, "👤 You")
    
    if forwarded_user and forwarded_chat:
        response += "\n\n" + format_user_info(forwarded_user, "👤 Forwarded from")
        response += f"""

📢 From Group/Channel
 ├ id: `-100{forwarded_chat.id}`
 ├ title: {forwarded_chat.title}
 └ username: {forwarded_chat.username if forwarded_chat.username else 'None'}"""
    elif forwarded_user:
        response += "\n\n" + format_user_info(forwarded_user, "👤 Forwarded from")
    elif forwarded_chat:
        response += f"""

📢 Forwarded from Group/Channel
 ├ id: `-100{forwarded_chat.id}`
 ├ title: {forwarded_chat.title}
 └ username: {forwarded_chat.username if forwarded_chat.username else 'None'}"""
    elif forward_sender_name:
        response += f"""

👤 Forwarded from Private User
 └ name: {forward_sender_name}
 └ note: User ini memiliki privasi forward message yang diaktifkan"""
    
    if message.forward_date:
        response += f"""

📃 Message
 └ forward_date: {message.forward_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}"""
        
    await message.reply_text(response, quote=True)

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

    result_text = "Tidak dapat menemukan pengguna/grup."
    for func in funcs:
        try:
            temp_result = await func(username)
            if temp_result:
                result_text = temp_result
                break
        except (UsernameNotOccupied, IndexError):
            continue
        except Exception:
            logging.error(traceback.format_exc())

    await message.reply_text(result_text, quote=True)

async def get_users(username: str) -> str:
    try:
        user = await app.get_users(username)
        if not user:
            return ""
        return await get_user_detail(user)
    except IndexError:
        return ""

async def get_channel(username: str) -> str:
    try:
        peer = await app.resolve_peer(username)
        result = await app.invoke(functions.channels.GetChannels(id=[peer]))
        for ch in result.chats:
            return get_chat_detail(ch)
        return ""
    except Exception:
        return ""

if __name__ == '__main__':
    app.run()
