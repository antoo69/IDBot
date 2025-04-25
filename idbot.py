#!/usr/local/bin/python3
# coding: utf-8

author = "@fsyrl9"

import logging
import os
import re
import traceback
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message, User, Chat
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
    
    # Mengambil tanggal pembuatan akun
    user_date = user.date if user.date else "Tidak Diketahui"
    
    # Membuat detail pesan pengguna
    text = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}
📅 Tanggal Pembuatan: {user_date}
    """
    
    return text

def getgroup_handler(group) -> str:
    # Mengambil tanggal pembuatan grup
    group_date = group.date if group.date else "Tidak Diketahui"
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{group.id}
🌐 Username: @{group.username if group.username else "Tidak ada"}
🏷 Title: {group.title}
📅 Tanggal Pembuatan: {group_date}
    """

def get_channel_detail(channel) -> str:
    # Mengambil tanggal pembuatan channel
    channel_date = channel.date if channel.date else "Tidak Diketahui"
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{channel.id}
🌐 Username: @{channel.username if channel.username else "Tidak ada"}
🏷 Title: {channel.title}
📅 Tanggal Pembuatan: {channel_date}
    """

# Handle /start command - directly show the user's ID and information
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    # Get user details
    user_details = await get_user_detail(user, client)

    # Send user details to chat
    await client.send_message(
        chat_id, 
        user_details + "\nStore aman dan terpercaya. Klik di bawah ini."
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
        chat_date = message.forward_from_chat.date if message.forward_from_chat.date else "Tidak Diketahui"
        
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}
  Tanggal Pembuatan: {user_details}

📢 Dari Channel/Grup:
  Nama: {message.forward_from_chat.title}
  ID: {message.forward_from_chat.id}
  Username: @{message.forward_from_chat.username if message.forward_from_chat.username else "Tidak ada"}
  Tanggal Pembuatan: {chat_date}
        """
    else:
        # For messages forwarded from users
        fwd_details = await get_user_detail(fwd, client) if fwd else ("Tidak bisa mengambil informasi dari pesan ini.")
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}
  Tanggal Pembuatan: {user_details}

👤 Pesan asli dari:
{fwd_details}
        """
    
    # Send the forwarded message's user or group details
    await message.reply_text(me, quote=True)

# Handle messages from group chats to get group/channel info
@app.on_message(filters.text & filters.group)
async def getgroup_compatibly_handler(client: Client, message: Message):
    text = message.text
    if getattr(message.forward_from_chat, "type", None) == "channel" or not re.findall(r"^/getgc@.*bot$", text):
        logging.warning("This is from a channel or non-command text")
        return

    logging.info("Compatibly getgroup")
    await getgroup_handler(client, message)

# Get group/channel details if the user forwards from a group/channel
@app.on_message(filters.command(["getgc"]))
async def getgroup_handler(client: Client, message: Message):
    me = await get_user_detail(message.chat, client)
    await message.reply_text(me, quote=True)

# Handle private messages to check user/channel details from a username
@app.on_message(filters.text & filters.private)
async def private_handler(client: Client, message: Message):
    username = re.sub(r"@+|https://t.me/", "", message.text)
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

# Get user information by username
async def get_users(username, client):
    user = await app.get_users(username)
    return await get_user_detail(user, client)

# Get channel information by username
async def get_channel(username):
    peer = await app.resolve_peer(username)
    result = await app.invoke(
        functions.channels.GetChannels(
            id=[peer]
        )
    )
    return get_channel_detail(result)

if __name__ == '__main__':
    app.run()
