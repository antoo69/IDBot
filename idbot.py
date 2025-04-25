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

# Replace the following with your bot's credentials
TOKEN = os.getenv("TOKEN", "8033318643:AAHHrl-s2ZMCT895h7is6zSe35foQmtn8m8")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

def create_app():
    _app = Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)
    return _app

app = create_app()

async def get_user_detail(user: "Union[User, Chat]", client: Client = None) -> str:
    if user is None:
        return "Can't get hidden forwards!"
    
    # Membuat detail pesan pengguna
    text = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}
    """
    
    return text

def getgroup_handler(group) -> str:
    if group.is_private:
        group_details = f"""
Channel/group detail:

🆔 ID: -100{group.id}
🌐 Username: @{group.username if group.username else "Tidak ada"}
🏷 Title: {group.title}
        """
    else:
        group_details = "Grup ini tidak private atau tidak dapat diakses."
    return group_details

def get_channel_detail(channel) -> str:
    if channel.is_private:
        channel_details = f"""
Channel/group detail:

🆔 ID: -100{channel.id}
🌐 Username: @{channel.username if channel.username else "Tidak ada"}
🏷 Title: {channel.title}
        """
    else:
        channel_details = "Channel ini tidak private atau tidak dapat diakses."
    
    return channel_details

# Handle /start command - directly show the user's ID and information
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    # Get user details
    user_details = await get_user_detail(user, client)

    # Create an inline keyboard with store link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])

    # Send user details to chat
    await client.send_message(
        chat_id, 
        user_details + "\nStore aman dan terpercaya. Klik di bawah ini.",
        reply_markup=keyboard
    )

# Handle forwarded messages (both from group and private)
@app.on_message(filters.forwarded)
async def forward_handler(client: Client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    user = message.from_user
    
    # Get user details
    user_details = await get_user_detail(user, client)
    
    # Get forwarded message details
    if message.forward_from_chat:
        # For messages forwarded from channels/groups
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}

📢 Dari Channel/Grup:
  Nama: {message.forward_from_chat.title}
  ID: {message.forward_from_chat.id}
  Username: @{message.forward_from_chat.username if message.forward_from_chat.username else "Tidak ada"}
        """
    else:
        # For messages forwarded from users
        fwd_details = await get_user_detail(fwd, client) if fwd else ("Tidak bisa mengambil informasi dari pesan ini.")
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}

👤 Pesan asli dari:
{fwd_details}
        """
    
    # Create an inline keyboard with store link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    # Send the forwarded message's user or group details
    await message.reply_text(me, quote=True, reply_markup=keyboard)

# Handle private messages to check user/channel details from a username
@app.on_message(filters.text & filters.private)
async def private_handler(client: Client, message: Message):
    username = re.sub(r"@+|https://t.me/", "", message.text)
    
    # Check if it is a channel or user
    if message.text.startswith("https://t.me/"):
        # Try to get channel details
        try:
            peer = await app.resolve_peer(username)
            result = await app.invoke(
                functions.channels.GetChannels(
                    id=[peer]
                )
            )
            # Send channel details
            channel_details = get_channel_detail(result)
            await message.reply_text(channel_details, quote=True)
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}", quote=True)
    else:
        # Try to get user details
        try:
            user = await app.get_users(username)
            user_details = await get_user_detail(user, client)
            await message.reply_text(user_details, quote=True)
        except Exception as e:
            await message.reply_text(f"Error: {str(e)}", quote=True)

# Handle /info command - provide usage instructions
@app.on_message(filters.command(["info"]))
async def info_handler(client: Client, message: Message):
    info_text = """
🤖 **Cara Penggunaan Bot:**

1. **/start** - Menampilkan ID dan informasi pengguna Anda.
2. **Kirimkan username atau link grup/channel** - Bot akan menampilkan detail grup/channel berdasarkan username atau link.
3. **/info** - Menampilkan informasi tentang cara menggunakan bot ini.
4. **Tombol "Ferdi Store"** - Klik tombol ini untuk mengunjungi Ferdi Store yang aman dan terpercaya.

🛒 **Tautan ke Ferdi Store**: [Ferdi Store](https://t.me/FerdiStore)
    """
    
    # Send the usage instructions
    await message.reply_text(info_text)

if __name__ == '__main__':
    app.run()
