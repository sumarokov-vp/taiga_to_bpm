# Standard Library
from os import environ

# Third Party Stuff
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

load_dotenv()
token = environ.get("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN environment variable not set. Check .env file")
bot: TeleBot = TeleBot(token, parse_mode="MarkdownV2")


def list_buttons(rows: list) -> InlineKeyboardMarkup:
    """
    :param rows: list of tuples with id (0) and name (1)
    """
    keyboard = InlineKeyboardMarkup()
    for row in rows:
        keyboard.add(
            InlineKeyboardButton(
                text=row[1],
                callback_data=row[0],
            )
        )
    return keyboard
