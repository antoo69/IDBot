#!/usr/local/bin/python3
# coding: utf-8

author = "@fsyrl9"

import logging
import os
import re
import traceback
from typing import Any, Union

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User, Chat

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

def get_user_detail(user: "Union[User, Chat]") -> str:
    global service_count
    service_count += 1
    if user is None:
        return "Can't get hidden forwards!"
    
    # Create a detailed user info message
    return f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}
    """

def getgroup_handler(group) -> str:
    global service_count
    service_count += 1
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{group.chats[0].id}
🌐 Username: @{group.chats[0].username}
🏷 Title: {group.chats[0].title}
    """

def get_channel_detail(channel) -> str:
    global service_count
    service_count += 1
    return f"""
Channel/group detail (you can also forward message to see detail):

🆔 ID: -100{channel.chats[0].id}
🌐 Username: @{channel.chats[0].username}
🏷 Title: {channel.chats[0].title}
    """

# Handle /start command - directly show the user's ID and information
@app.on_message(filters.command(["start"]))
async def start_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    # Generate user detail message
    user_details = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}

Store aman dan terpercaya. Klik di bawah ini.
    """
    
    # Create an inline keyboard with store link
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])

    # Send user details and store button
    await client.send_message(chat_id, user_details, reply_markup=keyboard)

# Handle forwarded messages (both from group and private)
@app.on_message(filters.forwarded)
async def forward_handler(client: Client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    user = message.from_user
    
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
        me = f"""
👤 Pengirim:
  Nama: {user.first_name}
  ID: {user.id}
  Username: @{user.username if user.username else "Tidak ada"}

👤 Pesan asli dari:
{get_user_detail(fwd) if fwd else "Tidak bisa mengambil informasi dari pesan ini."}
        """
    
    # Add inline keyboard to store
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])
    
    # Send the forwarded message's user or group details
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
    me = get_user_detail(message.chat)
    await message.reply_text(me, quote=True)

# Handle private messages to check user/channel details from a username
@app.on_message(filters.text & filters.private)
async def private_handler(client: Client, message: Message):
    username = re.sub(r"@+|https://t.me/", "", message.text)
    funcs = [get_users, get_channel]
    text = ""

    for func in funcs:
        try:
            text = await func(username)
            if text:
                break
        except Exception as e:
            logging.error(traceback.format_exc())
            text = str(e)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])
    await message.reply_text(text, quote=True, reply_markup=keyboard)

# Get user information by username
async def get_users(username):
    user = await app.get_users(username)
    return get_user_detail(user)

# Get channel information by username
async def get_channel(username):
    peer = await app.resolve_peer(username)
    result = await app.invoke(
        raw.functions.channels.GetChannels(
            id=[peer]
        )
    )
    return get_channel_detail(result)

if __name__ == '__main__':
    app.run()
