from __future__ import annotations

# Third Party Stuff
from pydantic import (
    BaseModel,
    PositiveInt,
)
from telebot import types as telebot_types

# My Stuff
from db.db_worker import execute_query
from db.redis_instance import redis_connection


class User(BaseModel):
    """
    User model. Contains all the information about the user.
    Can save and load itself from the Redis and DB.
    Can get itself from the DB and Redis.
    """

    chat_id: PositiveInt
    name: str | None = None
    full_name: str | None = None
    bot_state: str | None = None
    bot_state_value: int | None = None
    last_message_id: int | None = None
    report_id: int | None = None

    @classmethod
    def get_from_redis(cls, chat_id: int) -> User | None:
        user_json = str(redis_connection.get(str(chat_id)))
        if user_json == "None":
            return None
        return cls.model_validate_json(user_json)

    def save_to_redis(self):
        """
        Dump user to JSON and save it to Redis.
        """
        redis_connection.set(str(self.chat_id), self.model_dump_json())

    def save_to_db(self):
        query = """
            INSERT INTO bot_users (telegram_id, name, full_name, json_dump)
            VALUES (%(chat_id)s, %(name)s, %(full_name)s, %(json_dump)s)
            ON CONFLICT (telegram_id) DO UPDATE
            SET json_dump = %(json_dump)s, name = %(name)s, full_name = %(full_name)s
            ;
            """
        args = {
            "chat_id": self.chat_id,
            "name": self.name,
            "full_name": self.full_name,
            "json_dump": self.model_dump_json(),
        }
        execute_query(query, args)

    @staticmethod
    def set_state(chat_id: int, state: str):
        user = User.get_from_redis(chat_id)
        if not user:
            user = User(chat_id=chat_id)
        user.bot_state = state
        user.save_to_redis()


class TUser:
    """
    Usser model for testing purposes.
    """

    user: User
    tg_user: telebot_types.User
    callback_query: telebot_types.CallbackQuery
    tg_chat: telebot_types.Chat
    tg_message: telebot_types.Message
    _delete_on_exit: bool

    def __init__(self, chat_id: int, delete_on_exit: bool = True):
        self.user = User(chat_id=chat_id)
        self._delete_on_exit = delete_on_exit

    def __enter__(self):
        self.tg_user = telebot_types.User(
            id=self.user.chat_id,
            is_bot=False,
            username="test_user",
            first_name="Test",
            last_name="User",
        )

        self.callback_query = telebot_types.CallbackQuery(
            id="3223687221385220948",
            from_user=self.tg_user,
            data="$deal_select_coin$2",
            chat_instance="5508489576152291065",
            json_string="{'id': '3223687221385220948', 'from': {'id': 750573170, 'is_bot': False, 'first_name': 'Simple Logic', 'last_name': 'Solutions', 'username': 'simplelogic_sol', 'language_code': 'ru'}, 'message': {'message_id': 64, 'from': {...}, 'chat': {...}, 'date': 1675016226, 'text': 'Выберите', 'reply_markup': {...}}, 'chat_instance': '5508489576152291065', 'data': '$deal_select_direction$buy_direction'}",  # noqa E501
        )

        self.tg_chat = telebot_types.Chat(
            id=self.user.chat_id,
            type="private",
        )
        self.tg_message = telebot_types.Message(
            message_id=76,
            from_user=self.tg_user,
            date=1675112371,
            chat=self.tg_chat,
            content_type="text",
            options={},
            json_string="{'message_id': 76, 'from': {'id': 65310, 'is_bot': False, 'first_name': 'Vladimir', 'last_name': 'Sumarokov ️ ️', 'username': 'sumarokov_cyclist', 'language_code': 'ru', 'is_premium': True}, 'chat': {'id': 65310, 'first_name': 'Vladimir', 'last_name': 'Sumarokov ️ ️', 'username': 'sumarokov_cyclist', 'type': 'private'}, 'date': 1675112371, 'text': '/start', 'entities': [{...}]}",  # noqa E501
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pyright: ignore[reportUnknownVariableType]
        if self._delete_on_exit:
            self.delete()
        pass

    def delete(self):
        query = """
            DELETE FROM bot_users
            WHERE telegram_id = %(chat_id)s
            ;
            """
        args = {"chat_id": self.user.chat_id}
        execute_query(query, args)
