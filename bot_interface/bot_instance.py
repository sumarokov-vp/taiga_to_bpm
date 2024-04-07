# Standard Library
from os import environ

# Third Party Stuff
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()
token = environ.get("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN environment variable not set. Check .env file")
bot: TeleBot = TeleBot(token, parse_mode="MarkdownV2")
