import json
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def info_menu(num_tweets):
    text = (
        "*🌅🌄 Welcome to SkyBot\! 🌅🌄 * \n\n"
        "Scrolling sucks, let's build a better way\. Pin this bot and 1000x your Twitter\. \n\n"
        "Here are a few ways to interact with me:\n\n"
        " • Use AI to interact with your Twitter timeline\n"
        " • Send Tweets by sending the bot a message\n"
        " • Send voice messages Tweets\n"
        "• /help or /info displays this message\.\n"
        "\n"
        "If you run into any issues or bugs send a message to @bigsky7\."
    )

    threshold = 500 if int(num_tweets) > 200 else (200 if int(num_tweets) > 50 else 50)
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "Purchase more tokens 🏆 ",
                callback_data="purchase_tokens",
            ),
            InlineKeyboardButton(
                f"Retrieve Timeline 📚 {num_tweets}/{threshold}",
                callback_data="retrieve_timeline",
            ),
            InlineKeyboardButton(
                "FriendTech Chat 🤖 ",
                callback_data="retrieve_friendtech",
            ),
            InlineKeyboardButton(
                "Create Post 🔈 ",
                callback_data="tweet",
            ),
            InlineKeyboardButton(
                "Logout 👋 ",
                callback_data="logout",
            ),
        ]
    )
    return text, keyboard


def auth_menu(auth_url: str):
    text = (
        "Welcome to the Twitter-Telegram Bot. Before you can use this App you need to authenticate to Twitter:\n\n"
        "If you run into any issues with the redirect on Mobile, try authorizing via desktop app.\n\n"
        "• /help or /info displays this message.\n"
    )
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "Twitter-Telegram Bot 🤖",
                url="https://bigsky.gg",
            ),
            InlineKeyboardButton(
                "Authorize Twitter 🐦  ",
                url=auth_url,
            ),
        ]
    )
    return text, keyboard


# Build menu
def tweet_action_menu():
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "Post Tweet 🐦",
                callback_data="post_tweet",
            ),
            InlineKeyboardButton(
                "Post to FriendTech 🤖",
                callback_data = "post_friendtech",
            ),
            InlineKeyboardButton(
                "Improve Tweet 📝",
                callback_data="improve_tweet",
            ),
            InlineKeyboardButton(
                "Cancel ❌",
                callback_data="cancel",
            ),
        ]
    )
    return keyboard


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]

    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)

    return menu


# Reply menu
def reply_base_menu(tweet_id: str, tweet_text: str):
    keyboard = [
        [
            InlineKeyboardButton(
                "Sarcastic 🙄 ",
                callback_data=json.dumps(
                    {
                        "action": "sarcastic_prompt",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
            InlineKeyboardButton(
                "Enthusiastic 🚀 ",
                callback_data=json.dumps(
                    {"action": "enthusiastic_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Emoji 🐱 ",
                callback_data=json.dumps(
                    {"action": "emoji_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Question ❓ ",
                callback_data=json.dumps(
                    {
                        "action": "question_prompt",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data=json.dumps(
                    {"action": "prev_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=json.dumps(
                    {"action": "next_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Enter Reply ✍ ",
                callback_data=json.dumps(
                    {
                        "action": "enter_reply",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "Skip 🏃 ",
                callback_data=json.dumps(
                    {
                        "action": "skip_tweet",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def reply_action_menu(tweet_id: str, original_tweet: str, tweet_text: str, message_id: str):
    keyboard = InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                "Post Reply 👋 ",
                callback_data=json.dumps(
                    {
                        "action": "post_reply",
                        "tweet_id": tweet_id,
                        "original_tweet": original_tweet,
                        "tweet_text": tweet_text,
                        "message_id": message_id,
                    }
                ),
            ),
            InlineKeyboardButton(
                "Regenerate Reply 🔥 ",
                callback_data=json.dumps(
                    {
                        "action": "regenerate",
                        "tweet_id": tweet_id,
                        "original_tweet": original_tweet,
                        "tweet_text": tweet_text,
                        "message_id": message_id,
                    }
                ),
            ),
            InlineKeyboardButton(
                "Skip 🏃 ",
                callback_data=json.dumps(
                    {
                        "action": "skip",
                        "tweet_id": tweet_id,
                        "original_tweet": original_tweet,
                        "tweet_text": tweet_text,
                        "message_id": message_id,
                    }
                ),
            ),
        ]
    )
    return keyboard


def reply_extended_menu(tweet_id: str, tweet_text: str):
    keyboard = [
        [
            InlineKeyboardButton(
                "Ancient Wisdom 🏺",
                callback_data=json.dumps(
                    {"action": "wisdom_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Abstract 🎨",
                callback_data=json.dumps(
                    {"action": "abstract_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Contrary 😈",
                callback_data=json.dumps(
                    {"action": "contrary_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Fortune Cookie 🥠",
                callback_data=json.dumps(
                    {"action": "fortune_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Congratulations 👑",
                callback_data=json.dumps(
                    {"action": "congrats_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Answer question 🤔",
                callback_data=json.dumps(
                    {"action": "answer_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Treasure Hunt Clue 🗺",
                callback_data=json.dumps(
                    {"action": "treasure_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Elaborate 🧐",
                callback_data=json.dumps(
                    {"action": "elaborate_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data=json.dumps(
                    {"action": "prev_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=json.dumps(
                    {"action": "next_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


# Friendtech

# Reply menu
def friendtech_reply_base_menu(tweet_id: str, tweet_text: str):
    keyboard = [
        [
            InlineKeyboardButton(
                "Generate GM 🌅  ",
                callback_data=json.dumps(
                    {
                        "action": "gm_prompt",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
            InlineKeyboardButton(
                "Enthusiastic 🚀 ",
                callback_data=json.dumps(
                    {"action": "enthusiastic_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Emoji 🐱 ",
                callback_data=json.dumps(
                    {"action": "emoji_prompt", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Question ❓ ",
                callback_data=json.dumps(
                    {
                        "action": "question_prompt",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data=json.dumps(
                    {"action": "prev_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=json.dumps(
                    {"action": "next_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Enter Reply 📝 ",
                callback_data=json.dumps(
                    {"action": "enter_reply", "tweet_id": tweet_id, "tweet_text": tweet_text},
                 ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Skip 🏃 ",
                callback_data=json.dumps(
                    {
                        "action": "skip",
                        "tweet_id": tweet_id,
                        "tweet_text": tweet_text,
                    }
                ),
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup



def friendtech_reply_extended_menu(tweet_id: str, tweet_text: str):
    keyboard = [
        [
            InlineKeyboardButton(
                "User Info 📊 ",
                callback_data=json.dumps(
                    {"action": "user_info", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "Buy Key 🔑 ",
                callback_data=json.dumps(
                    {"action": "buy_key", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Sell Key 🗝 ",
                callback_data=json.dumps(
                    {"action": "sell_key", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data=json.dumps(
                    {"action": "prev_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=json.dumps(
                    {"action": "next_option", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def user_info_menu(tweet_id: str, tweet_text: str):
    keyboard = [
        [
            InlineKeyboardButton(
                "Close 📕",
                callback_data=json.dumps(
                    {"action": "close", "tweet_id": tweet_id, "tweet_text": tweet_text}
                ),
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
