#!/usr/local/bin/python3
# coding: utf-8

__author__ = "Benny <benny.think@gmail.com>"

import logging
import os
import re
import traceback
from typing import Any, Union

from pyrogram import Client, filters, types, raw
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot_ping import get_runtime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

TOKEN = os.getenv("TOKEN". "23345148")
APP_ID = os.getenv("APP_ID", "23345148")
APP_HASH = os.getenv("APP_HASH", "fe37a47fef4345512ed47c17d3306f0b")

# telegram DC map: https://docs.pyrogram.org/faq/what-are-the-ip-addresses-of-telegram-data-centers
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


def get_user_detail(user: "Union[types.User, types.Chat]") -> "str":
    global service_count
    service_count += 1
    if user is None:
        return "Can't get hidden forwards!"

    return f"""
user name: `@{user.username} `
first name: `{user.first_name or user.title}`
last name: `{user.last_name}`
user id: `{user.id}`

is bot: {getattr(user, "is_bot", None)}
DC: {user.dc_id} {DC_MAP.get(user.dc_id, "")}
language code: {getattr(user, "language_code", None)}
phone number: {getattr(user, "phone_number", None)}
    """


def get_channel_detail(channel) -> "str":
    global service_count
    service_count += 1
    return f"""
Channel/group  detail(you can also forward message to see detail):

name: `@{channel.chats[0].username} `
title: `{channel.chats[0].title}`
id: `-100{channel.chats[0].id}`
    """


@app.on_message(filters.command(["start"]))
def start_handler(client: "Client", message: "types.Message"):
    chat_id = message.chat.id
    user = message.from_user
    user_details = f"""
👤 Mention: [{user.first_name}](tg://user?id={user.id})
🆔 ID kamu: {user.id}
🌐 Username: @{user.username if user.username else "Tidak ada"}

   keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ferdi Store", url="https://t.me/Galerifsyrl")]
    ])

    client.send_message(chat_id, user_details, reply_markup=keyboard, parse_mode="Markdown")
    

@app.on_message(filters.command(["help"]))
def help_handler(client: "Client", message: "types.Message"):
    chat_id = message.chat.id
    text = """Forward messages, send username, use /id to get your account's detail.\n
    My Store : @Galerifsyrl\n/getgc untuk melihat ID group atau channel.
    """
    client.send_message(chat_id, text)


@app.on_message(filters.command(["id"]))
def getme_handler(client: "Client", message: "types.Message"):
    me = get_user_detail(message.from_user)
    message.reply_text(me, quote=True)


@app.on_message(filters.command(["ping"]))
def start_handler(client: "Client", message: "types.Message"):
    logging.info("Pong!")
    chat_id = message.chat.id
    runtime = get_runtime("botsrunner_idbot_1")
    global service_count
    if getattr(message.chat, "username", None) == "BennyThink":
        msg = f"{runtime}\n\nService count:{service_count}"
    else:
        msg = runtime
    client.send_message(chat_id, msg)


@app.on_message(filters.command(["getgc"]))
def getgroup_handler(client: "Client", message: "types.Message"):
    me = get_user_detail(message.chat)
    message.reply_text(me, quote=True)


@app.on_message(filters.text & filters.group)
def getgroup_compatibly_handler(client: "Client", message: "types.Message"):
    text = message.text
    if getattr(message.forward_from_chat, "type", None) == "channel" or not re.findall(r"^/getgroup@.*bot$", text):
        logging.warning("this is from channel or non-command text")
        return

    logging.info("compatibly getgroup")
    getgroup_handler(client, message)


@app.on_message(filters.forwarded & filters.private)
def forward_handler(client: "Client", message: "types.Message"):
    fwd = message.forward_from or message.forward_from_chat
    me = get_user_detail(fwd)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏪 Channel Store", url="https://t.me/Galerifsyrl")]
    ])
    message.reply_text(me, quote=True, reply_markup=keyboard)


def get_users(username):
    user: "Union[types.User, Any]" = app.get_users(username)
    return get_user_detail(user)


def get_channel(username):
    peer: "Union[raw.base.InputChannel, Any]" = app.resolve_peer(username)
    result = app.invoke(
        raw.functions.channels.GetChannels(
            id=[peer]
        )
    )
    return get_channel_detail(result)


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
            text = e

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏪 Channel Store", url="https://t.me/Galerifsyrl")]
    ])
    message.reply_text(text, quote=True, reply_markup=keyboard)


if __name__ == '__main__':
    app.run()
