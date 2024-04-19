# Third Party Stuff
from dotenv import load_dotenv

# My Stuff
from bot_interface import handlers
from bot_interface.bot_instance import bot

if __name__ == "__main__":
    print(handlers.State.COMMANDS_I.name)
    load_dotenv()
    print("Bot started")
    bot.infinity_polling()
