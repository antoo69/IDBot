#!/usr/local/bin/python3
# coding: utf-8

author = "@fsyrl9"

import logging
import os
import re
import traceback
from typing import Any, Union
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User, Chat
from pyrogram.raw import functions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

# Replace the following with your bot's credentials
TOKEN = os.getenv("TOKEN", "7568080253:AAFTljQwDwRoP7D1IxmgTcN2Gw1OS-OkFSk")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

def create_app():
    _app = Client("idbot", api_id=APP_ID, api_hash=APP_HASH, bot_token=TOKEN)
    return _app

app = create_app()
service_count = 0

async def get_user_detail(user: "Union[User, Chat]", client: Client = None) -> tuple:
    global service_count
    service_count += 1
    if user is None:
        return "Can't get hidden forwards!", None
    
    # Get user creation date
    user_dc_id = user.dc_id if hasattr(user, 'dc_id') else None
    user_date = datetime.fromtimestamp(user.id >> 32) if user.id else None
    date_str = user_date.strftime('%d %B %Y') if user_date else "Unknown"
    
    # Get profile photo if client is provided
    profile_pic = None
    if client:
        try:
            photos = await client.get_chat_photos(user.id)
            if photos:
                profile_pic = photos[0].file_id
        except:
            pass
    
    # Create a detailed user info message
    text = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}
📅 Tanggal Pembuatan: {date_str}
🌍 DC ID: {user_dc_id if user_dc_id else "Unknown"}
    """
    
    return text, profile_pic

def getgroup_handler(group) -> str:
    global service_count
    service_count += 1
    
    # Get group creation date
    group_date = datetime.fromtimestamp(group.chats[0].id >> 32)
    date_str = group_date.strftime('%d %B %Y')
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{group.chats[0].id}
🌐 Username: @{group.chats[0].username}
🏷 Title: {group.chats[0].title}
📅 Tanggal Pembuatan: {date_str}
    """

def get_channel_detail(channel) -> str:
    global service_count
    service_count += 1
    
    # Get channel creation date
    channel_date = datetime.fromtimestamp(channel.chats[0].id >> 32)
    date_str = channel_date.strftime('%d %B %Y')
    
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{channel.chats[0].id}
🌐 Username: @{channel.chats[0].username}
🏷 Title: {channel.chats[0].title}
📅 Tanggal Pembuatan: {date_str}
    """

# Handle /start command - directly show the user's ID and information
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    # Get user details and profile photo
    user_details, profile_pic = await get_user_detail(user, client)

    # Create an inline keyboard with store link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])

    # Send profile photo if available
    if profile_pic:
        await message.reply_photo(
            photo=profile_pic,
            caption=user_details + "\nStore aman dan terpercaya. Klik di bawah ini.",
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            user_details + "\nStore aman dan terpercaya. Klik di bawah ini.", 
            reply_markup=keyboard
        )

# Handle forwarded messages (both from group and private)
@app.on_message(filters.forwarded)
async def forward_handler(client: Client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    user = message.from_user
    
    # Get user details and profile photo
    user_details, profile_pic = await get_user_detail(user, client)
    
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
  Tanggal Pembuatan: {date_str}

📢 Dari Channel/Grup:
  Nama: {message.forward_from_chat.title}
  ID: {message.forward_from_chat.id}
  Username: @{message.forward_from_chat.username if message.forward_from_chat.username else "Tidak ada"}
  Tanggal Pembuatan: {chat_date_str}
        """
    else:
        # For messages forwarded from users
        fwd_details = await get_user_detail(fwd, client) if fwd else ("Tidak bisa mengambil informasi dari pesan ini.", None)
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}
  Tanggal Pembuatan: {date_str}

👤 Pesan asli dari:
{fwd_details[0]}
        """
    
    # Add inline keyboard to store
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    # Send the forwarded message's user or group details with profile photo
    if profile_pic:
        await message.reply_photo(photo=profile_pic, caption=me, reply_markup=keyboard)
    else:
        await message.reply_text(me, reply_markup=keyboard)

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
    me, profile_pic = await get_user_detail(message.chat, client)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/FerdiStore")]
    ])
    
    if profile_pic:
        await message.reply_photo(photo=profile_pic, caption=me, reply_markup=keyboard)
    else:
        await message.reply_text(me, reply_markup=keyboard)

# Handle private messages to check user/channel details from a username
@app.on_message(filters.text & filters.private)
async def private_handler(client: Client, message: Message):
    username = re.sub(r"@+|https://t.me/", "", message.text)
    funcs = [get_users, get_channel]
    text = ""
    profile_pic = None

    for func in funcs:
        try:
            if func == get_users:
                text, profile_pic = await func(username, client)
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
    
    if profile_pic:
        await message.reply_photo(photo=profile_pic, caption=text, reply_markup=keyboard)
    else:
        await message.reply_text(text, reply_markup=keyboard)

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
