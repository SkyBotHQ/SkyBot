import time
import hashlib
from typing import cast

from tweepy import OAuth1UserHandler
from telegram import (
    Message,
    Update,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
)

from bot.payment import send_token_invoice, precheckout_callback, successful_payment_callback
from bot.userdata import CCT, UserData
from bot.command_menus import info_menu, auth_menu
from bot.heroku import (
    get_data,
    insert_friendtech_data,
    insert_data,
    get_twitter_data,
    get_all_data,
    delete_data,
    update_table,
    set_num_tweets,
    get_num_tweets,
    delete_all_data,
    create_table,
    retrieve_access_tokens,
    add_access_tokens,
    use_access_code,
)
from bot.utils import FALLBACK_HANDLER, TIMEOUT_HANDLER, cancel
from bot.tweethandler import start_tweet_actions, voice_message_handler
from bot.tweet_reply import (
    retrieve_timeline,
    reply_button,
    enter_reply,
    enter_reply_voice,
)
from bot.friendtech import (
    get_chats,
    friendtech_reply_action,
    friendtech_enter_reply_voice,
    friendtech_enter_reply,
    friendtech_reply_button,
)

from bot.constants import OAUTH1_USER_HANDLER

REPLY_TEXT = 44
REPLY_ACTION = 43
TWEET_ACTION = 42
PAYMENT_ACTION = 41
FRIENDTECH_REPLY_ACTION = 39
FRIENDTECH_REPLY_TEXT = 38

async def start(update: Update, context: CCT) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    user = update.effective_user
    user_data = cast(UserData, context.user_data)
    context_oauth = context.args

    if user_data.access_token is None and user_data.access_token_secret is None and user_data.jwt is None:
        try:
            data = get_data(user.id, context)
            if not data:
                pass
            else:
                user_data.update_access_token(data[0][1])
                user_data.update_access_token_secret(data[0][2])
                user_data.update_timeline_tokens(data[0][3])
                user_data.update_jwt(data[0][4])
                user_data.update_address(data[0][5])
        except Exception as e:
            print(str(e)) # Or log the error details to a file

    if user_data.access_token and user_data.access_token_secret != None:
        timeline_tokens = user_data.timeline_tokens
        if type(timeline_tokens) == str:
            user_data.update_timeline_tokens(50)

        timeline_tokens = user_data.timeline_tokens
        text, keyboard = info_menu(timeline_tokens)
        await cast(Message, update.effective_message).reply_text(
            text, reply_markup=keyboard, parse_mode="MarkdownV2"
        )
        return TWEET_ACTION

    if context_oauth and context_oauth[0]:
        oauth_verifier = context.args[0]
        oauth1_user_handler = context.application.bot_data["OAUTH1_USER_HANDLER"]
        access_token, access_token_secret = oauth1_user_handler.get_access_token(
            oauth_verifier
        )
        insert_data(user.id, user.username, access_token, access_token_secret, 50, context)

        # Update user context
        user_data = cast(UserData, context.user_data)

        user_data.update_access_token(access_token)
        user_data.update_access_token_secret(access_token_secret)
        user_data.update_timeline_tokens(50)

        timeline_tokens = user_data.timeline_tokens

        text, keyboard = info_menu(timeline_tokens)
        await cast(Message, update.effective_message).reply_text(
            text, reply_markup=keyboard, parse_mode="MarkdownV2"
        )
        return TWEET_ACTION

    else:
        await authenticate(update, context)
        return ConversationHandler.END


async def authenticate(update: Update, context: CCT) -> None:
    """Authenticate user with Twitter API.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    oauth1_user_handler = OAuth1UserHandler(
        context.application.bot_data["TWITTER_API_TOKEN"],
        context.application.bot_data["TWITTER_API_SECRET"],
        context.application.bot_data["TWITTER_REDIRECT_URL"],
    )
    auth_url = oauth1_user_handler.get_authorization_url()

    context.application.bot_data[OAUTH1_USER_HANDLER] = oauth1_user_handler

    text, keyboard = auth_menu(auth_url)
    await cast(Message, update.effective_message).reply_text(
        text, reply_markup=keyboard
    )
    return ConversationHandler.END


async def button(update: Update, context: CCT) -> None:
    """Parses the CallbackQuery and updates the message text.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    query = update.callback_query
    await query.answer()

    user_data = cast(UserData, context.user_data)
    user = update.effective_user

    if query.data == "retrieve_timeline":
        user_id = update.effective_user.id

        tokens = user_data.timeline_tokens
        print(tokens)
        if int(tokens) >= 5:
            new_tokens = int(tokens) - 5
            user_data.update_timeline_tokens(new_tokens)
            return await retrieve_timeline(update, context)
        else:
            return await cast(Message, update.effective_message).reply_text(
                "You need to purchase more tokens to use this feature. Use /tokens to purchase."
            )

    if query.data == "tweet":
        text = "Enter your tweet:"
        message = await cast(Message, update.effective_message).reply_text(
            text, reply_markup=ReplyKeyboardRemove()
        )
        user = update.effective_user
        user_data = cast(UserData, context.user_data)
        user_data.update_tmp_message_id(user, (message.message_id, 0))

        return ConversationHandler.END

    if query.data == "purchase_tokens":
        await send_token_invoice(update, context)
        return ConversationHandler.END

    if query.data == "logout":

        delete_data(user.id, context)
        user_data.update_access_token(None)
        user_data.update_access_token_secret(None)

        return ConversationHandler.END

    if query.data == "retrieve_friendtech":
        user = update.effective_user
        user_data = cast(UserData, context.user_data)
        if user_data.jwt is None:
            return await cast(Message, update.effective_message).reply_text(
                "This feature is still in development.  Check back soon!"
            )
        else:
            return await friendtech_reply_action(update, context)


    return ConversationHandler.END


info_handler = ConversationHandler(
    entry_points=[CommandHandler(["start", "help", "info"], start)],
    states={
        TWEET_ACTION: [
            CallbackQueryHandler(button),
            MessageHandler(filters.TEXT & ~filters.COMMAND, start_tweet_actions),
            MessageHandler(filters.VOICE & ~filters.COMMAND, voice_message_handler),
        ],
        REPLY_ACTION: [CallbackQueryHandler(reply_button)],
        REPLY_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, enter_reply),
            MessageHandler(filters.VOICE & ~filters.COMMAND, enter_reply_voice),
        ],
        FRIENDTECH_REPLY_ACTION: [CallbackQueryHandler(friendtech_reply_button)],
        FRIENDTECH_REPLY_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, friendtech_enter_reply),
            MessageHandler(filters.VOICE & ~filters.COMMAND, friendtech_enter_reply_voice),
        ],
        ConversationHandler.TIMEOUT: [TIMEOUT_HANDLER],
    },
    fallbacks=[FALLBACK_HANDLER],
    conversation_timeout=340,
    persistent=False,
    per_user=True,
    per_chat=True,
)
