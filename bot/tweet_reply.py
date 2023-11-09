import json
import re
import random
import asyncio
import time
import openai
from typing import cast
from collections import deque

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
from bot.twitter import fetch_twitter_client
from bot.heroku import get_twitter_data, pull_and_action_tweets
from bot.command_menus import reply_action_menu, reply_base_menu, reply_extended_menu
from bot.utils import FALLBACK_HANDLER, TIMEOUT_HANDLER, cancel
from bot.prompt import generate_reply

REPLY_ACTION = 43
REPLY_TEXT = 44

STICKERS = [
    "CAACAgIAAxkBAAEKOFRk9hkbIl_weGtpRwLE-LRlq7jEWQACqhgAAg9lCEoGzNzn0P2-0zAE",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
    "CAACAgIAAxkBAAEKObtk9swJuQUy3-Irw2sOfpCqSEMJzAACSgIAAladvQrJasZoYBh68DAE",
    "CAACAgIAAxkBAAEKOblk9swFzX_WsFPZGcEd0k3oVvg_BgACXgMAArrAlQVceSrBWv5H7DAE",
    "CAACAgIAAxkBAAEKObVk9svsORP9Ow8_Hsxa4GUdmyGrUAAClQADO2AkFOcewv9SzXpmMAQ",
    "CAACAgIAAxkBAAEKObdk9sv3BHsK7Az_zy5R5j8gpjQbGQAC3gADVp29CqXvdzhVgxXEMAQ",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
]


async def retrieve_timeline(update: Update, context: CCT):
    user = update.effective_user
    user_context = context.user_data
    user_data = cast(UserData, context.user_data)

    if not user_data.timeline_tweets:
        twitter = fetch_twitter_client(user_data.access_token, user_data.access_token_secret, context)

        if user.id == 1574952849:
            tweets = pull_and_action_tweets(context)
            print(tweets)
        else:
            tweets = twitter.get_home_timeline(
                exclude=["retweets", "replies"], max_results=50
            ).data

        temp_tweets = deque(maxlen=50)
        for tweet in tweets:
                temp_tweets.append((tweet.id, tweet.text))

        user_data.update_timeline_tweets(temp_tweets)

    for _ in range(5):
        if user_data.timeline_tweets:
            tweet_id, tweet_text = user_data.timeline_tweets.popleft()
            keyboard = reply_base_menu(tweet_id, tweet_text)
            await cast(Message, update.effective_message).reply_text(
                tweet_text, reply_markup=keyboard
            )

    return REPLY_ACTION


async def reply_button(update: Update, context: CCT):
    # Get the selected button action
    query = update.callback_query
    action_data = json.loads(query.data)

    action = action_data["action"]

    if action == "skip_tweet":
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
        return REPLY_ACTION

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

        return REPLY_TEXT

    elif action == "regenerate":
        await query.message.delete(),

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

        keyboard = reply_base_menu(action_data["tweet_id"], action_data["original_tweet"])
        await cast(Message, update.effective_message).reply_text(
            action_data["original_tweet"], reply_markup=keyboard
        )

        return REPLY_ACTION

    elif action == "skip":
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
        return REPLY_ACTION

    elif action == "post_reply":
        await post_reply(
            action_data["tweet_id"], action_data["tweet_text"], update, context
        )

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

    elif action == 'prev_option':
        new_markup = reply_base_menu(action_data["tweet_id"], action_data["tweet_text"])
        await query.message.edit_reply_markup(reply_markup=new_markup)

    elif action == 'next_option':
        new_markup = reply_extended_menu(action_data["tweet_id"], action_data["tweet_text"])
        await query.message.edit_reply_markup(reply_markup=new_markup)

    # Closing the current inline message
    await query.answer()


async def post_reply(tweet_id: str, tweet_text: str, update: Update, context: CCT):
    user = update.effective_user
    user_context = context.user_data
    user_data = cast(UserData, context.user_data)

    access_token = user_data.access_token
    access_token_secret = user_data.access_token_secret

    twitter = fetch_twitter_client(access_token, access_token_secret, context)
    res = twitter.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_id)
    print(res)


async def enter_reply(update: Update, context: CCT):
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

    return REPLY_ACTION


async def enter_reply_voice(update: Update, context: CCT):
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

    return REPLY_ACTION


set_reply_handler = ConversationHandler(
    entry_points=[CommandHandler("retrieve_timeline", retrieve_timeline)],
    states={
        REPLY_ACTION: [
            CallbackQueryHandler(reply_button),
        ],
        REPLY_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, enter_reply),
        ],
    },
    fallbacks=[FALLBACK_HANDLER],
    persistent=False,
    per_user=True,
    per_chat=True,
)
