#!/usr/bin/env python3
"""Conversation for deleting stored stickers."""
import openai
import random
import time
from typing import cast

from telegram import (
    Message,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)

from bot.userdata import CCT, UserData
from bot.utils import FALLBACK_HANDLER, TIMEOUT_HANDLER, cancel
from bot.twitter import post_tweet, generate_new_tweet
from bot.command_menus import build_menu, tweet_action_menu
from bot.friendtech import post_friendtech_chat

TWEET_ACTION = 42

STICKERS = [
    "CAACAgIAAxkBAAEKOFRk9hkbIl_weGtpRwLE-LRlq7jEWQACqhgAAg9lCEoGzNzn0P2-0zAE",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
    "CAACAgIAAxkBAAEKObtk9swJuQUy3-Irw2sOfpCqSEMJzAACSgIAAladvQrJasZoYBh68DAE",
    "CAACAgIAAxkBAAEKOblk9swFzX_WsFPZGcEd0k3oVvg_BgACXgMAArrAlQVceSrBWv5H7DAE",
    "CAACAgIAAxkBAAEKObVk9svsORP9Ow8_Hsxa4GUdmyGrUAAClQADO2AkFOcewv9SzXpmMAQ",
    "CAACAgIAAxkBAAEKObdk9sv3BHsK7Az_zy5R5j8gpjQbGQAC3gADVp29CqXvdzhVgxXEMAQ",
    "CAACAgIAAxkBAAEKObNk9svIL_OXKe0eN_9ErjvcAAFD9oMAAgoQAAIERhFIqLb_bSd3Tk8wBA",
]


async def start_tweet_actions(update: Update, context: CCT) -> int:
    """Starts the conversation and asks for new tweet..

    Args:
        update: The Telegram update.
        _: The callback context as provided by the application.

    Returns:
        int: The next state.
    """
    """Store info provided by user and ask for the next category."""
    user = update.effective_user
    user_data = cast(UserData, context.user_data)

    text = update.message.text

    user_data.update_tmp_message_id(user, (0, update.message.message_id))
    user_data.update_tweet(user, text)

    keyboard = tweet_action_menu()
    await update.message.reply_text(text, reply_markup=keyboard)

    return TWEET_ACTION


# Voice Message Handler
async def voice_message_handler(update: Update, context: CCT):
    """Starts the conversation and asks for new tweet..

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    bot = context.bot
    user = update.message.from_user
    voice_message = update.message.voice

    new_file = await bot.get_file(voice_message.file_id)
    await new_file.download_to_drive(custom_path="voice_message.ogg")

    print("Received voice message")

    audio_file = open("voice_message.ogg", "rb")

    openai.api_key = context.application.bot_data["OPENAI_API_KEY"]
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    user_data = context.user_data
    user_data.update_tweet(user, transcript["text"])

    keyboard = tweet_action_menu()
    reply_msg = transcript["text"]

    await cast(Message, update.effective_message).reply_text(
        reply_msg, reply_markup=keyboard
    )

    #user_data.update_tmp_message_id(user, (0, update.message.message_id))
    return TWEET_ACTION


async def reply_action_button(update: Update, context: CCT) -> None:
    """Parses the CallbackQuery and updates the message text.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "post_tweet":
        print("Posting tweet")
        user_data = cast(UserData, context.user_data)

        tweet_sticker = await post_tweet(update, context)

        sticker = random.choice(STICKERS)
        message = await context.bot.send_sticker(
            chat_id=update.effective_chat.id, sticker=sticker
        )

        time.sleep(2)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[0]
        )
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
        )
        await query.message.edit_reply_markup(reply_markup=None),
        await query.message.delete(),

        time.sleep(3)
        for i in tweet_sticker if isinstance(tweet_sticker, list) else [tweet_sticker]:
            await i.delete()
        await message.delete()

        return ConversationHandler.END

    if query.data == "post_friendtech":
        user_data = cast(UserData, context.user_data)
        await post_friendtech_chat(update, context)

        sticker = random.choice(STICKERS)
        message = await context.bot.send_sticker(
            chat_id=update.effective_chat.id, sticker=sticker
        )

        time.sleep(2)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
        )
        await query.message.edit_reply_markup(reply_markup=None),
        await query.message.delete(),

        await message.delete()

        return ConversationHandler.END


    if query.data == "improve_tweet":
        keyboard = tweet_action_menu()
        generated_tweet = await generate_new_tweet(update, context)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            text=generated_tweet,
            message_id=update.effective_message.message_id,
        )
        await context.bot.edit_message_reply_markup(
            update.effective_chat.id,
            reply_markup=keyboard,
            message_id=update.effective_message.message_id,
        )

        return TWEET_ACTION

    if query.data == "cancel":
        #await context.bot.delete_message(
        #    chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[0]
        #)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=user_data.tmp_message_id[1]
        )
        await query.message.edit_reply_markup(reply_markup=None),
        await query.message.delete(),

        return ConversationHandler.END

    return ConversationHandler.END


set_voice_to_tweet_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.VOICE, voice_message_handler)],
    states={
        TWEET_ACTION: [CallbackQueryHandler(reply_action_button)],
        ConversationHandler.TIMEOUT: [TIMEOUT_HANDLER],
    },
    fallbacks=[FALLBACK_HANDLER],
    conversation_timeout=30,
    persistent=False,
    per_user=True,
    per_chat=True,
)

set_tweet_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT, start_tweet_actions)],
    states={
        TWEET_ACTION: [CallbackQueryHandler(reply_action_button)],
        ConversationHandler.TIMEOUT: [TIMEOUT_HANDLER],
    },
    fallbacks=[FALLBACK_HANDLER],
    conversation_timeout=30,
    persistent=False,
    per_user=True,
    per_chat=True,
)
