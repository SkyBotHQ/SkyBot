#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import functools
import click
import tweepy
from configparser import ConfigParser
from telegram import __version__ as TG_VER

from ptbstats import SimpleStats, register_stats, set_application
from bot.setup import setup_application
from bot.userdata import UserData

try:
    from telegram import __version_info__

except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    Defaults,
    ContextTypes,
    AIORateLimiter,
    PersistenceInput,
    PicklePersistence,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command()
@click.option(
    "--local", default=False, is_flag=True, help="Use local bot."  # Same as above
)


# Start the bot
def main(local: bool) -> None:
    """Start the bot."""

    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read("bot.ini")

    if local:
        token = config["TwitterStatusBot"]["local_token"]
        payment_provider_token = config["Payment"]["test_payment_provider_token"]
        twitter_redirect_url = config["TwitterAccess"]["test_twitter_redirect_url"]
    else:
        token = config["TwitterStatusBot"]["token"]
        payment_provider_token = config["Payment"]["payment_provider_token"]
        twitter_redirect_url = config["TwitterAccess"]["twitter_redirect_url"]

    admin_id = int(config["TwitterStatusBot"]["admins_chat_id"])
    sticker_chat_id = config["TwitterStatusBot"]["sticker_chat_id"]

    twitter_api_token = config["TwitterAccess"]["api_key"]
    twitter_api_secret = config["TwitterAccess"]["api_secret_key"]
    twitter_bearer_token = config["TwitterAccess"]["bearer_token"]

    db_host = config["HerokuDB"]["db_host"]
    db_password = config["HerokuDB"]["db_password"]
    db_name = config["HerokuDB"]["db_name"]
    db_user = config["HerokuDB"]["db_user"]

    openai_api_key = config["OpenAIAccess"]["openai_api_key"]

    oauth1_user_handler = tweepy.OAuth1UserHandler(
        consumer_key=twitter_api_token,
        consumer_secret=twitter_api_secret,
        callback=twitter_redirect_url,
    )

    # Enable chat persistence
    defaults = Defaults(parse_mode=ParseMode.HTML, disable_notification=True, block=False)
    context_types = ContextTypes(user_data=UserData)
    persistence = PicklePersistence(
        "tsb.pickle",
        context_types=context_types,
        single_file=False,
        store_data=PersistenceInput(chat_data=False),
    )

    # Create the Application and pass it your bot's token.
    application = (
        Application.builder()
        .token(token)
        .persistence(persistence)
        .arbitrary_callback_data(True)
        .context_types(context_types)
        .post_init(
            functools.partial(
                setup_application,
                admin_id=admin_id,
                sticker_chat_id=sticker_chat_id,
                oauth1_user_handler=oauth1_user_handler,
                twitter_api_token=twitter_api_token,
                twitter_api_secret=twitter_api_secret,
                twitter_bearer_token=twitter_bearer_token,
                twitter_redirect_url=twitter_redirect_url,
                db_host=db_host,
                db_password=db_password,
                db_name=db_name,
                db_user=db_user,
                openai_api_key=openai_api_key,
                payment_provider_token=payment_provider_token,
            )
        )
        .rate_limiter(
            AIORateLimiter(
                overall_max_rate=0,
                overall_time_period=0,
                group_max_rate=0,
                group_time_period=0,
                max_retries=3,
            )
        )
        .build()
    )

    # Start the Bot
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
