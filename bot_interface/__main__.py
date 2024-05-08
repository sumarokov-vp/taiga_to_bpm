# Third Party Stuff
from telebot.types import Message

# My Stuff
from bot_interface import handlers
from bot_interface.bot_instance import bot

if __name__ == "__main__":
    print(handlers.State.COMMANDS_I.name)
    print("Bot started")

    bot.infinity_polling()
