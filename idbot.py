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

async def get_user_detail(user: User) -> str:
    if user is None:
        return "Can't get hidden forwards!"
    
    # Get user creation date from the ID
    user_date = datetime.fromtimestamp(user.id >> 32)
    date_str = user_date.strftime('%d %B %Y')
    
    # Create a detailed user info message
    text = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}
📅 Tanggal Pembuatan: {date_str}
    """
    
    return text

def getgroup_handler(group) -> str:
    # Get group creation date from the ID
    group_date = datetime.fromtimestamp(group.id >> 32)
    date_str = group_date.strftime('%d %B %Y')
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: {group.id}
🌐 Username: @{group.username if group.username else "Tidak ada"}
🏷 Title: {group.title}
📅 Tanggal Pembuatan: {date_str}
    """

def get_channel_detail(channel) -> str:
    # Get channel creation date from the ID
    channel_date = datetime.fromtimestamp(channel.id >> 32)
    date_str = channel_date.strftime('%d %B %Y')
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: {channel.id}
🌐 Username: @{channel.username if channel.username else "Tidak ada"}
🏷 Title: {channel.title}
📅 Tanggal Pembuatan: {date_str}
    """

# Handle /start command - directly show the user's ID and information
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    # Get user details
    user_details = await get_user_detail(user)

    # Create an inline keyboard with store link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])

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
    user_details = await get_user_detail(user)
    
    # Get forwarded message details
    if message.forward_from_chat:
        # For messages forwarded from channels/groups
        chat_date = datetime.fromtimestamp(message.forward_from_chat.id >> 32)
        chat_date_str = chat_date.strftime('%d %B %Y')
        
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}
  Tanggal Pembuatan: {user_details.split("\n")[3]}

📢 Dari Channel/Grup:
  Nama: {message.forward_from_chat.title}
  ID: {message.forward_from_chat.id}
  Username: @{message.forward_from_chat.username if message.forward_from_chat.username else "Tidak ada"}
  Tanggal Pembuatan: {chat_date_str}
        """
    else:
        # For messages forwarded from users
        fwd_details = await get_user_detail(fwd) if fwd else "Tidak bisa mengambil informasi dari pesan ini."
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}
  Tanggal Pembuatan: {user_details.split("\n")[3]}

👤 Pesan asli dari:
{fwd_details}
        """
    
    # Add inline keyboard to store
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    await message.reply_text(me, quote=True, reply_markup=keyboard)

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
    me = await getgroup_handler(message.chat)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    await message.reply_text(me, quote=True, reply_markup=keyboard)

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

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    await message.reply_text(text, quote=True, reply_markup=keyboard)

# Get user information by username
async def get_users(username, client):
    user = await app.get_users(username)
    return await get_user_detail(user)

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
