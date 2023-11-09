#!/usr/bin/env python3
"""Methods for initializing the application."""
import warnings
from tweepy import OAuth1UserHandler
from typing import Union

from ptbstats import SimpleStats, register_stats, set_application
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ExtBot,
    JobQueue,
    filters,
)

from bot.tweethandler import (
    set_tweet_conversation_handler,
    set_voice_to_tweet_handler,
    start_tweet_actions,
)
from bot.commands import cancel, info_handler
from bot.userdata import CCT, UserData
from bot.constants import (
    ADMIN_KEY,
    STICKER_CHAT_ID_KEY,
    OAUTH1_USER_HANDLER,
    TWITTER_API_TOKEN,
    TWITTER_API_SECRET,
    TWITTER_BEARER_TOKEN,
    TWITTER_REDIRECT_URL,
    DB_HOST,
    DB_PASSWORD,
    DB_NAME,
    DB_USER,
    OPENAI_API_KEY,
    PAYMENT_PROVIDER_TOKEN,
)
from bot.deletesticker import delete_sticker_conversation
from bot.setfallbackpicture import set_fallback_picture_conversation
from bot.settimezone import build_set_timezone_conversation
from bot.tweet_reply import set_reply_handler
from bot.payment import send_token_invoice, precheckout_callback, successful_payment_callback
from bot.friendtech import friendtech_reply_handler

# B/C we know what we're doing
warnings.filterwarnings(
    "ignore", message="If 'per_", module="telegram.ext.conversationhandler"
)
warnings.filterwarnings(
    "ignore",
    message=".*does not handle objects that can not be copied",
    module="telegram.ext.basepersistence",
)


async def setup_application(
    application: Application[ExtBot, CCT, UserData, dict, dict, JobQueue],
    admin_id: int,
    sticker_chat_id: Union[str, int],
    oauth1_user_handler: OAuth1UserHandler,
    twitter_api_token: str,
    twitter_api_secret: str,
    twitter_bearer_token: str,
    twitter_redirect_url: str,
    db_host: str,
    db_password: str,
    db_name: str,
    db_user: str,
    openai_api_key: str,
    payment_provider_token: str,
) -> None:
    """
    Adds handlers and sets up ``bot_data``. Also sets the bot commands.

    Args:
        application: The :class:`telegram.ext.Application`.
        admin_id: The admins chat id.
        sticker_chat_id: The name of the chat where stickers can be sent to get their file IDs.
        twitter_api_token: The Twitter API token.
        twitter_api_secret: The Twitter API secret.
        twitter_bearer_token: The Twitter bearer token.
        twitter_redirect_url: The Twitter redirect URL.
        db_host: The database host.
        db_password: The database password.
        db_name: The database name.
        db_user: The database user.
        openai_api_key: The OpenAI API key.
    """
    set_application(application)
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("token", send_token_invoice))

    application.add_handler(delete_sticker_conversation)
    application.add_handler(set_fallback_picture_conversation)
    application.add_handler(build_set_timezone_conversation(application.bot))

    application.add_handler(info_handler)
    application.add_handler(set_tweet_conversation_handler)
    application.add_handler(set_voice_to_tweet_handler)
    application.add_handler(set_reply_handler)
    application.add_handler(friendtech_reply_handler)

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, start_tweet_actions)
    )

    # Pre-checkout handler to final check
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    # Bot commands
    base_commands = [
        ("start", 'Start application'),
        ("cancel", "Cancels the current conversation"),
    ]

    await application.bot.set_my_commands(base_commands)

    # Bot data
    application.bot_data[ADMIN_KEY] = admin_id
    application.bot_data[STICKER_CHAT_ID_KEY] = sticker_chat_id
    application.bot_data[OAUTH1_USER_HANDLER] = oauth1_user_handler
    application.bot_data[TWITTER_API_TOKEN] = twitter_api_token
    application.bot_data[TWITTER_API_SECRET] = twitter_api_secret
    application.bot_data[TWITTER_BEARER_TOKEN] = twitter_bearer_token
    application.bot_data[TWITTER_REDIRECT_URL] = twitter_redirect_url
    application.bot_data[DB_USER] = db_user
    application.bot_data[DB_HOST] = db_host
    application.bot_data[DB_PASSWORD] = db_password
    application.bot_data[DB_NAME] = db_name
    application.bot_data[OPENAI_API_KEY] = openai_api_key
    application.bot_data[PAYMENT_PROVIDER_TOKEN] = payment_provider_token
