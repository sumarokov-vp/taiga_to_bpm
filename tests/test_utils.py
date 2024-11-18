# My Stuff
from bot_interface.bot_instance import bot
from bot_interface.utils.send_file import SendFile


def test_send_file_text():
    text = "Hello, World!"
    user_id = 65310
    send_file = SendFile(bot, user_id)
    send_file.text(text)
