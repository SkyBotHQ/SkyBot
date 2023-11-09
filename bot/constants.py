#!/usr/bin/env python3
"""Constants for the bot."""
from configparser import ConfigParser
from pathlib import Path

from enum import Enum, auto
from hyphen import Hyphenator
from PIL import Image, ImageFont
from tweepy import OAuth1UserHandler

config = ConfigParser()
config.read("bot.ini")

# A little trick to get the corrects paths both at runtime and when building the docs
PATH_PREFIX = "../" if Path("../headers").is_dir() else ""
PAYMENT_PROVIDER_TOKEN: str = "PAYMENT_PROVIDER_TOKEN"
""":obj:`PaymentProviderToken`: Stored under this key in ``bot_data``."""
OAUTH1_USER_HANDLER: OAuth1UserHandler = "OAUTH1_USER_HANDLER"
""":obj:`OAuth1UserHandler`: The oauth1_user_handler is stored under this key in ``bot_data``."""
TWITTER_API_TOKEN: str = "TWITTER_API_TOKEN"
""":obj:`str`: The twitter_api_token is stored under this key in ``bot_data``."""
TWITTER_API_SECRET: str = "TWITTER_API_SECRET"
""":obj:`str`: The twitter_api_secret is stored under this key in ``bot_data``."""
TWITTER_BEARER_TOKEN: str = "TWITTER_BEARER_TOKEN"
""":obj:`str`: The twitter_bearer_token is stored under this key in ``bot_data``."""
TWITTER_REDIRECT_URL: str = "TWITTER_REDIRECT_URL"
""":obj:`str`: The twitter_redirect_url is stored under this key in ``bot_data``."""
DB_HOST: str = "DB_HOST"
""":obj:`str`: The db_host id is stored under this key in ``bot_data``."""
DB_PASSWORD: str = "DB_PASSWORD"
""":obj:`str`: The db_password is stored under this key in ``bot_data``."""
DB_NAME: str = "DB_NAME"
""":obj:`str`: The db_name is stored under this key in ``bot_data``."""
DB_USER: str = "DB_USER"
""":obj:`str`: The db_user id is stored under this key in ``bot_data``."""
OPENAI_API_KEY: str = "OPENAI_API_KEY"
""":obj:`str`: The open_ai_api key is stored under this key in ``bot_data``."""
ADMIN_KEY: str = "ADMIN_KEY"
""":obj:`str`: The admins chat id is stored under this key in ``bot_data``."""
STICKER_CHAT_ID_KEY: str = "STICKER_CHAT_ID_KEY"
""":obj:`srt`: The name of the chat where stickers can be sent to get their file IDs is stored
under this key in ``bot_data``."""
REMOVE_KEYBOARD_KEY: str = "REMOVE_KEYBOARD_KEY"
""":obj:`str`: Store a message object in under this key in ``chat_data`` to remove its reply
markup later on with :meth:`utils.remove_reply_markup`."""
HOMEPAGE: str = "https://bibo-joshi.github.io/twitter-status-bot/"
""":obj:`str`: Homepage of this bot."""
TEMPLATE_DIRECTORY = f"{PATH_PREFIX}templates"
""":obj:`str`: Name of the directory containing the templates."""
HEADER_TEMPLATE = f"{TEMPLATE_DIRECTORY}/header.png"
""":obj:`str`: Path of the template for the header."""
FOOTER_TEMPLATE = f"{TEMPLATE_DIRECTORY}/footer.png"
""":obj:`str`: Path of the template for the footer."""
BODY_TEMPLATE = f"{TEMPLATE_DIRECTORY}/body.png"
""":obj:`str`: Path of the template for the body."""
VERIFIED_TEMPLATE = f"{TEMPLATE_DIRECTORY}/verified.png"
""":obj:`str`: Path of the template for the »verified« symbol."""
VERIFIED_IMAGE = Image.open(VERIFIED_TEMPLATE)
""":class:`Pillow.Image.Image`: The »verified« symbol as Pillow image in the correct size."""
VERIFIED_IMAGE.thumbnail((27, 27))
BACKGROUND = "#16202cff"
""":obj:`str`: Background color."""
TEXT_MAIN = "#ffffff"
""":obj:`str`: Color of the main text."""
TEXT_SECONDARY = "#8d99a5ff"
""":obj:`str`: Color of secondary text."""
FONTS_DIRECTORY = f"{PATH_PREFIX}fonts"
""":obj:`str`: Name of the directory containing the fonts."""
FONT_HEAVY = f"{FONTS_DIRECTORY}/seguibl.ttf"
""":obj:`str`: Font of the main text."""
FONT_SEMI_BOLD = f"{FONTS_DIRECTORY}/seguisb.ttf"
""":obj:`str`: Font of the secondary text."""
FALLBACK_PROFILE_PICTURE = "logo/TwitterStatusBot-rectangle.png"
""":obj:`str`: Path of the picture to use as profile picture, if the user has none."""
HEADERS_DIRECTORY = f"{PATH_PREFIX}headers"
""":obj:`str`: Name of the directory containing the saved headers."""
FOOTER_FONT = ImageFont.truetype(FONT_SEMI_BOLD, 24)
""":class:`PIL.ImageFont.Font`: Font to use for the footer."""
USER_NAME_FONT = ImageFont.truetype(FONT_HEAVY, 24)
""":class:`PIL.ImageFont.Font`: Font to use for the username."""
USER_HANDLE_FONT = ImageFont.truetype(FONT_SEMI_BOLD, 23)
""":class:`PIL.ImageFont.Font`: Font to use for the user handle."""
BIG_TEXT_FONT = ImageFont.truetype(FONT_SEMI_BOLD, 70)
""":class:`PIL.ImageFont.Font`: Font to use for big text in the body."""
SMALL_TEXT_FONT = ImageFont.truetype(FONT_SEMI_BOLD, 36)
""":class:`PIL.ImageFont.Font`: Font to use for small text in the body."""
HYPHENATOR = Hyphenator("en_US")
""":class:`PyHyphen.Hyphenator`: A hyphenator to use to wrap text."""
LTR = "ltr"
""":obj:`str`: Text direction left to right."""
RTL: str = "rtl"
""":obj:`str`: Text direction right to let."""
