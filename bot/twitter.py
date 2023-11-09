import tweepy
import asyncio
import time
import json
import openai
from typing import cast, List

from telegram import Message, Sticker, Update, User, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from telegram.constants import ChatAction

from bot.userdata import CCT, UserData
from bot.constants import TWITTER_BEARER_TOKEN, TWITTER_API_TOKEN, TWITTER_API_SECRET
from bot.heroku import get_twitter_data
from bot.utils import get_sticker_photo_stream


# Manage Twitter API
def fetch_twitter_client(
    access_token, access_token_secret, context: CCT
) -> tweepy.Client:
    """Fetches a Twitter API client for the given user.
    Args:
        access_token: The Twitter API access token.
        access_token_secret: The Twitter API access token secret.
        context: The callback context as provided by the application.
    Returns:
        A Twitter API client.

    """
    twitter_bearer_token = cast(str, context.bot_data[TWITTER_BEARER_TOKEN])
    twitter_api_token = cast(str, context.bot_data[TWITTER_API_TOKEN])
    twitter_api_secret = cast(str, context.bot_data[TWITTER_API_SECRET])

    client = tweepy.Client(
        bearer_token=twitter_bearer_token,
        consumer_key=twitter_api_token,
        consumer_secret=twitter_api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True,
    )
    return client


async def post_tweet(update: Update, context: CCT):
    """Tweets the given text.
    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """

    user = update.effective_user
    user_context = context.user_data
    user_data = cast(UserData, context.user_data)

    access_token = user_data.access_token
    access_token_secret = user_data.access_token_secret

    twitter = fetch_twitter_client(access_token, access_token_secret, context)

    text = user_data.tweet

    # takes whatever follows /tweet and posts it
    text = text.replace("blank", "")
    if len(text) > 280:
        chunks = parse_to_twitter_threads(text)

        # Post thread to chat
        stickers = []
        for c in chunks:
            context.application.create_task(
                context.bot.send_chat_action(user.id, ChatAction.UPLOAD_PHOTO)
            )
            msg = cast(Message, update.effective_message)
            user = cast(User, update.effective_user)
            stream = await get_sticker_photo_stream(cast(str, c), user, context)
            sticker_message = await msg.reply_sticker(stream)
            stickers.append(sticker_message)

        post_tweet_thread(chunks, twitter)
        return stickers
    else:
        twitter.create_tweet(text=text)
        context.application.create_task(
            context.bot.send_chat_action(user.id, ChatAction.UPLOAD_PHOTO)
        )
        msg = cast(Message, update.effective_message)
        user = cast(User, update.effective_user)
        stream = await get_sticker_photo_stream(cast(str, text), user, context)

        sticker_message = await msg.reply_sticker(stream)
        return sticker_message
    return ConversationHandler.END


# Thread actions
def parse_to_twitter_threads(text) -> List[str]:
    """Parses a string into a list of strings suitable for Twitter threads.
    Args:
        text: The text to parse.
    Returns:
        A list of strings suitable for Twitter threads.
    """
    chunks = []
    i = 0
    count_length = 0
    while text:
        i += 1
        excess_length = len(str(i)) + 3  # accounting for "/\n\n"
        if len(text) + excess_length > 280:
            pos = text.rfind(".", 0, 280 - excess_length)
            if pos != -1:  # Period found within suitable length
                chunk, text = text[: pos + 1], text[pos + 1 :]
            else:  # No period found, or period outside suitable range
                chunk, text = text[: 280 - excess_length], text[280 - excess_length :]
        else:
            chunk = text
            text = ""
        chunks.append(f"{chunk}\n\n{i}/")
    return chunks


def post_tweet_thread(tweets, twitter):
    """Posts a thread of tweets.
    Args:
        tweets: A list of tweets to post.
        twitter: The Twitter API client.
    """
    previous_tweet_id = None

    for tweet_text in tweets:
        response = twitter.create_tweet(
            text=tweet_text, in_reply_to_tweet_id=previous_tweet_id
        )
        previous_tweet_id = response.data["id"]
        time.sleep(1)



async def generate_new_tweet(update: Update, context: CCT):
    """Generate new Tweet!.'
    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    openai.api_key = context.application.bot_data["OPENAI_API_KEY"]

    user = update.effective_user
    user_data = cast(UserData, context.user_data)
    tweet = user_data.tweet

    max_tokens = 100
    if len(tweet) > 240:
        max_tokens = 800

    prompt = "Improve the following text.  Your goal is to subtly improve the quality of the text.  Make sure the text does not contain passive voice or grammar mistakes:\n\n###\n\n"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt + tweet + "\n\n###\n\n",
        temperature=0.5,
        max_tokens=50,
        top_p=0.8,
        stop=["###"],
    )

    new_tweet = response.choices[0].text
    user_data.update_tweet(user, new_tweet)

    return new_tweet
