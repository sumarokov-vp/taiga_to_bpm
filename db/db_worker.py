# Standard Library
from os import environ
from typing import List

# Third Party Stuff
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import TupleRow


def get_one(query: str, args: dict | None = None) -> TupleRow | None:
    """
    Returns one row from the database.
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchone()


def get_first(query: str, args: dict | None = None) -> TupleRow | None:
    """
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()[0]


def get_all(query: str, args: dict | None = None) -> List[TupleRow] | None:
    """
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()


def execute_query(query: str, args: dict | None = None) -> None:
    """
    Example:
        query =
            INSERT INTO bot_users (telegram_id, name, full_name, json_dump)
            VALUES (%(chat_id)s, %(name)s, %(full_name)s, %(json_dump)s)

        args = {
            "chat_id": self.chat_id,
            "name": self.name,
            "full_name": self.full_name,
            "json_dump": json_dump,
        }
    """
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            conn.commit()


if __name__ == "__main__":
    load_dotenv()
    get_all("SELECT * FROM bot_users")
    pass
