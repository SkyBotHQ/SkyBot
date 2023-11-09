import re
from telegram import LabeledPrice, Update, Sticker
from typing import cast

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot.userdata import CCT, UserData
from bot.heroku import set_num_tweets

async def send_token_invoice(update: Update, context: CCT) -> None:
    """Sends an invoice without shipping-payment."""
    chat_id = update.effective_chat.id
    description = "Purchase Twitter Timeline Tokens"
    # select a payload just for you to recognize its the donation from your bot
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "USD"
    PAYMENT_PROVIDER_TOKEN = context.application.bot_data["PAYMENT_PROVIDER_TOKEN"]
    # price in dollars
    price = [2.99, 8.99, 19.99]
    # price * 100 so as to include 2 decimal points
    for price in price:

        if price == 2.99:
            tokens = 50
        elif price == 8.99:
            tokens = 200
        elif price == 19.99:
            tokens = 500

        payload = f"Custom-Payload-{tokens}-{update.effective_user.id}"
        title = f"Purchase {tokens} Tokens 😍  "
        prices = [LabeledPrice("Token", int(price * 100))]

        await context.bot.send_invoice(
            chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
        )



async def precheckout_callback(
    update: Update, context: CCT
) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query

    # check the payload, is this from your bot?
    if not re.search(r"Custom-Payload", query.invoice_payload):
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


# finally, after contacting the payment provider...

async def successful_payment_callback(
    update: Update, context: CCT
) -> None:
    """Confirms the successful payment."""

    # do something after successfully receiving payment?
    user = update.effective_user
    user_data = cast(UserData, context.user_data)
    tokens = user_data.timeline_tokens
    payload = update.message.successful_payment.invoice_payload
    _, _, purchase_tokens, *_ = payload.split("-")

    total_tokens = int(tokens) + int(purchase_tokens)
    print(f"Total Tokens: {total_tokens}")
    set_num_tweets(context, user.id, total_tokens)
    user_data.update_timeline_tokens(total_tokens)

    await update.message.reply_text("Thank you for your payment!")
    await context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker="CAACAgIAAxkBAAEKOFRk9hkbIl_weGtpRwLE-LRlq7jEWQACqhgAAg9lCEoGzNzn0P2-0zAE",
        )
