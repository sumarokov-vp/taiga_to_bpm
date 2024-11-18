# Standard Library
import io

# Third Party Stuff
from telebot import TeleBot


class SendFile:
    def __init__(self, bot: TeleBot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    def text(
        self,
        text: str,
    ) -> None:
        with io.StringIO(text) as f:
            f.seek(0)
            self.bot.send_document(
                chat_id=self.chat_id,
                document=f,
                visible_file_name="temp.txt",
            )
