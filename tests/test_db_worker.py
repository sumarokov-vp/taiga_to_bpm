# Third Party Stuff
from dotenv import load_dotenv

# My Stuff
from db import db_worker

load_dotenv()


def test_get_one():
    query = "SELECT id, telegram_id FROM bot_users WHERE telegram_id = %(telegram_id)s"
    args = {"telegram_id": 65310}
    user = db_worker.get_one(
        query,
        args,
    )
    assert user
    assert user[0] == 1
