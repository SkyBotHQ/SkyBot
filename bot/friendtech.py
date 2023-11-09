import requests
import websockets
import uuid
import json
import re
import random
import asyncio
import time
import openai
import ijson
from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import QueryBase
from typing import cast
from collections import deque
from websockets.exceptions import ConnectionClosedError

from telegram import (
    Message,
    InputMedia,
    Update,
    Sticker,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)

from bot.userdata import CCT, UserData
from bot.command_menus import reply_action_menu, reply_base_menu, reply_extended_menu, friendtech_reply_base_menu, friendtech_reply_extended_menu, user_info_menu
from bot.utils import FALLBACK_HANDLER, TIMEOUT_HANDLER, cancel
from bot.prompt import generate_reply
from bot.platform import Platform

FRIENDTECH_REPLY_ACTION = 39
FRIENDTECH_REPLY_TEXT = 38

STICKERS = [
    "CAACAgIAAxkBAAEKOFRk9hkbIl_weGtpRwLE-LRlq7jEWQACqhgAAg9lCEoGzNzn0P2-0zAE",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
    "CAACAgIAAxkBAAEKObtk9swJuQUy3-Irw2sOfpCqSEMJzAACSgIAAladvQrJasZoYBh68DAE",
    "CAACAgIAAxkBAAEKOblk9swFzX_WsFPZGcEd0k3oVvg_BgACXgMAArrAlQVceSrBWv5H7DAE",
    "CAACAgIAAxkBAAEKObVk9svsORP9Ow8_Hsxa4GUdmyGrUAAClQADO2AkFOcewv9SzXpmMAQ",
    "CAACAgIAAxkBAAEKObdk9sv3BHsK7Az_zy5R5j8gpjQbGQAC3gADVp29CqXvdzhVgxXEMAQ",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
]


async def post_friendtech_chat(update: Update, context: CCT):
    print("post_friendtech_chat")
    user_data = cast(UserData, context.user_data)

    text = user_data.tweet
    jwt = user_data.jwt
    address = user_data.address

    uri = f"wss://prod-api.kosetto.com/?authorization={jwt}"
    async with websockets.connect(uri) as ws:
        clientMessageId = uuid.uuid4().hex
        message_data = {
            'action': 'sendMessage',
            'text': text,
            'imagePaths': None,
            'chatRoomId': address.lower(),
            "replyingToMessageId": None,
            'clientMessageId': clientMessageId
        }
        await ws.send(json.dumps(message_data))


async def reply_friendtech_chat(update: Update, context: CCT, text: str, chatRoomId: str, image_paths=None, replyingToMessageId=None) -> None:
    user_data = cast(UserData, context.user_data)

    jwt = user_data.jwt

    uri = f"wss://prod-api.kosetto.com/?authorization={jwt}"
    async with websockets.connect(uri) as ws:
        clientMessageId = uuid.uuid4().hex
        message_data = {
            'action': 'sendMessage',
            'text': text,
            'imagePaths': image_paths,
            'chatRoomId': chatRoomId.lower(),
            "replyingToMessageId": replyingToMessageId,
            'clientMessageId': clientMessageId
        }
        await ws.send(json.dumps(message_data))



async def get_chats(updte: Update, context: CCT, address):
    user_data = cast(UserData, context.user_data)

    jwt = user_data.jwt

    uri = f"wss://prod-api.kosetto.com/?authorization={jwt}"
    async with websockets.connect(uri) as ws:
        message_data = {
            'action': 'requestMessages',
            'chatRoomId': address.lower(),
        }
        await ws.send(json.dumps(message_data))

        while True:
            try:
                msg = await ws.recv()
                if isinstance(msg, str):
                    data = json.loads(msg)
                    messages = data.get("messages", [])

                    for message in messages:
                        sender = data.get("sendingUserId", "")
                        if sender != user_data.address:
                            return message
                    else:
                        pass
                else:
                    print(f"Received: {msg}")
            except ConnectionClosedError:
                print("Connection closed")
                ws.close()
                ws = await websockets.connect(uri)


async def friendtech_reply_action(update: Update, context: CCT) -> int:
    user_data = cast(UserData, context.user_data)
    platform = Platform()
    data = platform.getHoldings(user_data.address).json()
    coroutines = [get_chats(update, context, user["address"]) for user in data["users"]]
    messages = await asyncio.gather(*coroutines)
    print(messages)
    latest_messages = sorted([i for n, i in enumerate(messages) if i not in messages[n + 1:]], key=lambda x: x['timestamp'], reverse=True)[:10]

    for message in latest_messages:
        user_info = platform.getInfoFromAddress(message["sendingUserId"])

        sender_address = message["sendingUserId"].lower()

        if sender_address != user_data.address.lower():
            data_string = user_info.json()
            text = message["text"] + "\n\n" + "@" + data_string["twitterUsername"]
            keyboard = friendtech_reply_base_menu(message["sendingUserId"], message["text"])
            await cast(message, update.effective_message).reply_text(
                text, reply_markup=keyboard
            )
        else:
            pass

    return FRIENDTECH_REPLY_ACTION


async def friendtech_reply_button(update: Update, context: CCT):
    # Get the selected button action
    query = update.callback_query

    try:
        action_data = json.loads(query.data)
        action = action_data["action"]
    except json.JSONDecodeError:
        action = "None"

    if action == "skip":
        await query.message.delete(),
        sticker_id = (
            "CAACAgIAAxkBAAEKOa1k9rvpyivRLOjtsJshOw-yGCwAAXAAAlkAA8GcYAxsy-iz2LOOhjAE"
        )

        await query.message.edit_reply_markup(reply_markup=None),
        await query.message.delete(),

        message = await context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker="CAACAgIAAxkBAAEKOa1k9rvpyivRLOjtsJshOw-yGCwAAXAAAlkAA8GcYAxsy-iz2LOOhjAE",
        )
        time.sleep(1)
        await message.delete()


    elif action == "post_reply":
        await reply_friendtech_chat(update, context, action_data["tweet_text"], action_data["tweet_id"])

        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=action_data["message_id"]
            )
        except Exception:
            pass

        try:
            user_data = cast(UserData, context.user_data)
            await context.bot.delete_message(
                chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[0]
            )
        except Exception:
            pass

        await asyncio.gather(
            query.message.edit_reply_markup(reply_markup=None),
            query.message.delete(),
        )

        sticker = random.choice(STICKERS)

        message = await context.bot.send_sticker(
            chat_id=update.effective_chat.id, sticker=sticker
        )
        time.sleep(2)
        await message.delete()


    elif action == "enter_reply":
        await query.message.delete(),

        reply_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=action_data["tweet_text"]
        )

        user = update.effective_user
        user_data = cast(UserData, context.user_data)

        user_data.update_tweet_id(tweet_id=action_data["tweet_id"], user=user)
        text = "Enter your reply:"
        message = await cast(Message, update.effective_message).reply_text(
            text, reply_markup=ReplyKeyboardRemove()
        )
        user_data.update_tmp_message_id(
            user, (reply_message.message_id, message.message_id)
        )

        return FRIENDTECH_REPLY_TEXT

    elif re.match(r".*_prompt", action):
        await query.message.delete(),

        user = update.effective_user
        user_data = cast(UserData, context.user_data)

        prompt_keyword = re.split(r"_prompt", action)[0]
        generate_reply_text = await generate_reply(
            action_data["tweet_text"], prompt_keyword, context
        )
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=action_data["tweet_text"]
        )

        message_id = message.message_id

        keyboard = reply_action_menu(
            action_data["tweet_id"], action_data["tweet_text"], generate_reply_text, message_id=message_id
        )
        ai_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=generate_reply_text,
            reply_markup=keyboard,
        )

        user_data.update_tmp_message_id(
            user, (ai_message.message_id, message.message_id)
        )

        return FRIENDTECH_REPLY_ACTION

    elif action == "prev_option":
        new_markup = friendtech_reply_base_menu(action_data["tweet_id"], action_data["tweet_text"])
        await query.message.edit_reply_markup(reply_markup=new_markup)

    elif action == "next_option":
        new_markup = friendtech_reply_extended_menu(action_data["tweet_id"], action_data["tweet_text"])
        await query.message.edit_reply_markup(reply_markup=new_markup)

    elif action == "user_info":
        await query.message.delete(),

        user_data = cast(UserData, context.user_data)
        user = update.effective_user

        reply_message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=action_data["tweet_text"]
        )

        platform = Platform()
        user_info = platform.getInfoFromAddress(action_data["tweet_id"])

        wallet_to_info = {}
        with open("./cache/userScores.json", 'r') as f:
            objects = ijson.items(f, 'item')
            for obj in objects:
                wallet_to_info[obj['wallet_only']] = obj

        matching_info = wallet_to_info[action_data["tweet_id"]]

        key_price = float(matching_info['key_price'][0])
        formatted_key_price = "{:.4f}".format(key_price)

        wallet_eth_balance = float(matching_info['wallet_eth_balance'])
        formatted_wallet_eth_balance = "{:.4f}".format(wallet_eth_balance)

        quality_score = float(matching_info['quality_score'])
        formatted_quality_score = "{:.4f}".format(quality_score)

        text = f"""
        🔑🔷📊  User Info 🔑🔷📊

        Twitter: @{user_info.json()["twitterUsername"]}
        Holders: {user_info.json()["holderCount"]}
        Holdings: {user_info.json()["holdingCount"]}

        Key Price: {formatted_key_price}
        Wallet Eth Balance: {formatted_wallet_eth_balance}
        Defections: {matching_info['defections']}
        Quality Score: {formatted_quality_score}
        Num (3,3) Pairs: {matching_info['num_3_3_pairs']}
        """

        user_info_keyboard = user_info_menu(action_data["tweet_id"], action_data["tweet_text"])
        message = await cast(Message, update.effective_message).reply_text(
            text, reply_markup=user_info_keyboard)

        user_data.update_tmp_message_id(
            user, (reply_message.message_id, message.message_id)
        )

        return FRIENDTECH_REPLY_ACTION


    elif action == "close":
        user = update.effective_user
        user_data = cast(UserData, context.user_data)

        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[0]
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
        )

        keyboard = friendtech_reply_base_menu(action_data["tweet_id"], action_data["tweet_text"])
        user_reply = await context.bot.send_message(
            chat_id=update.effective_chat.id, text=action_data["tweet_text"], reply_markup=keyboard
        )

        return FRIENDTECH_REPLY_ACTION


    elif action == "buy_key":
        pass

    elif action == "sell_key":
        pass

    # Closing the current inline message
    await query.answer()




async def friendtech_enter_reply(update: Update, context: CCT):
    user = update.effective_user
    user_data = cast(UserData, context.user_data)

    text = update.message.text

    user_data.update_tweet(user, text)

    message_id = update.message.message_id

    keyboard = reply_action_menu(tweet_id=user_data.tweet_id, original_tweet="",tweet_text=text, message_id=message_id)
    user_reply = await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, reply_markup=keyboard
    )

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
    )
    await update.message.delete()

    return FRIENDTECH_REPLY_ACTION


async def friendtech_enter_reply_voice(update: Update, context: CCT):
    bot = context.bot
    user = update.message.from_user
    voice_message = update.message.voice

    new_file = await bot.get_file(voice_message.file_id)
    await new_file.download_to_drive(custom_path="voice_message.ogg")

    print("Received voice message")

    audio_file = open("voice_message.ogg", "rb")

    openai.api_key = context.application.bot_data["OPENAI_API_KEY"]
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    text = transcript["text"]

    user_data = context.user_data
    user_data.update_tweet(user, text)

    message_id = update.message.message_id

    keyboard = reply_action_menu(tweet_id=user_data.tweet_id, original_tweet="", tweet_text=text, message_id=message_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, reply_markup=keyboard
    )

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
    )
    await update.message.delete()

    return FRIENDTECH_REPLY_ACTION


friendtech_reply_handler = ConversationHandler(
    entry_points=[CommandHandler("retrieve_friendtech", friendtech_reply_action)],
    states={
        FRIENDTECH_REPLY_ACTION: [
            CallbackQueryHandler(friendtech_reply_button),
        ],
        FRIENDTECH_REPLY_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, friendtech_enter_reply),
            MessageHandler(filters.VOICE, friendtech_enter_reply_voice),
        ],
    },
    fallbacks=[FALLBACK_HANDLER],
    persistent=False,
    per_user=True,
    per_chat=True,
)
