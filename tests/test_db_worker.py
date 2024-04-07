from db import db_worker
from dotenv import load_dotenv

load_dotenv()


def test_get_one():
    query = "SELECT id, telegram_id FROM bot_users WHERE telegram_id = %s"
    user = db_worker.get_one(
        query,
        65310,
    )
    assert user
    assert user[0] == 1
