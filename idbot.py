#!/usr/local/bin/python3
# coding: utf-8

author = "Benny <benny.think@gmail.com>"

import logging
import os
import re
import traceback
from typing import Any, Union

from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

# Replace the following with your bot's credentials
TOKEN = os.getenv("TOKEN", "23345148")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

DC_MAP = {
    1: "Miami",
    2: "Amsterdam",
    3: "Miami",
    4: "Amsterdam",
    5: "Singapore"
}

def create_app():
    _app = Client("idbot", APP_ID, APP_HASH, bot_token=TOKEN)
    return _app

app = create_app()
service_count = 0

def get_user_detail(user: "Union[types.User, types.Chat]") -> str:
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
def start_handler(client: "Client", message: "types.Message"):
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
    client.send_message(chat_id, user_details, reply_markup=keyboard, parse_mode="Markdown")

# Handle forwarded messages (both from group and private)
@app.on_message(filters.forwarded)
def forward_handler(client: "Client", message: "types.Message"):
    fwd = message.forward_from or message.forward_from_chat
    me = get_user_detail(fwd) if fwd else "Tidak bisa mengambil informasi dari pesan ini."
    
    # Add inline keyboard to store
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])
    
    # Send the forwarded message's user or group details
    message.reply_text(me, quote=True, reply_markup=keyboard)

# Handle messages from group chats to get group/channel info
@app.on_message(filters.text & filters.group)
def getgroup_compatibly_handler(client: "Client", message: "types.Message"):
    text = message.text
    if getattr(message.forward_from_chat, "type", None) == "channel" or not re.findall(r"^/getgc@.*bot$", text):
        logging.warning("This is from a channel or non-command text")
        return

    logging.info("Compatibly getgroup")
    getgroup_handler(client, message)

# Get group/channel details if the user forwards from a group/channel
@app.on_message(filters.command(["getgc"]))
def getgroup_handler(client: "Client", message: "types.Message"):
    me = get_user_detail(message.chat)
    message.reply_text(me, quote=True)

# Handle private messages to check user/channel details from a username
@app.on_message(filters.text & filters.private)
def private_handler(client: "Client", message: "types.Message"):
    username = re.sub(r"@+|https://t.me/", "", message.text)
    funcs = [get_users, get_channel]
    text = ""

    for func in funcs:
        try:
            text = func(username)
            if text:
                break
        except Exception as e:
            logging.error(traceback.format_exc())
            text = str(e)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("AGIK STORE", url="https://t.me/Galerifsyrl")]
    ])
    message.reply_text(text, quote=True, reply_markup=keyboard)

# Get user information by username
def get_users(username):
    user: "Union[types.User, Any]" = app.get_users(username)
    return get_user_detail(user)

# Get channel information by username
def get_channel(username):
    peer: "Union[types.raw.base.InputChannel, Any]" = app.resolve_peer(username)
    result = app.invoke(
        types.raw.functions.channels.GetChannels(
            id=[peer]
        )
    )
    return get_channel_detail(result)

if name == 'main':
    app.run()
