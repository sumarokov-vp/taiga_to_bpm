# Standard Library
from os import environ

# Third Party Stuff
from dotenv import load_dotenv
from psycopg.rows import TupleRow
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

load_dotenv()
token = environ.get("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN environment variable not set. Check .env file")
bot: TeleBot = TeleBot(token, parse_mode="MarkdownV2", threaded=False)


def list_buttons(rows: list[TupleRow], callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Creates buttons with text from 'name' fieldand
        and callback_data from 'id' field and prefix.

    - id should be a first element in tuple
    - name should be second element in tuple

    Example:
        projects = get_all(query)
        keyboard = list_buttons(projects, 'main#')
    """
    keyboard = InlineKeyboardMarkup()
    for row in rows:
        item_id = str(row[0])
        data = f"{callback_prefix}{item_id}"
        keyboard.add(InlineKeyboardButton(text=row[1], callback_data=data))
    return keyboard


def replace_reserved_characters(cell: str) -> str:
    return (
        cell.replace("_", "\\_")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("~", "\\~")
        .replace("`", "\\`")
        .replace(">", "\\>")
        .replace("#", "\\#")
        .replace("+", "\\+")
        .replace("-", "\\-")
        .replace("=", "\\=")
        .replace("|", "\\|")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace(".", "\\.")
        .replace("!", "\\!")
    )
