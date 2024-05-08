# Standard Library
from os import environ
from typing import (
    List,
    Optional,
)

# Third Party Stuff
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import TupleRow

load_dotenv()
TAIGA_DB_URL = environ.get("DB_URL")
CREATIO_DB_URL = environ.get("CREATIO_DB_URL")
if not TAIGA_DB_URL:
    raise ValueError("DB_URL environment variable not set")
if not CREATIO_DB_URL:
    raise ValueError("CREATIO_DB_URL environment variable not set")


def get_one(
    query: str,
    args: Optional[dict] = None,
    db_url: Optional[str] = TAIGA_DB_URL,
) -> TupleRow | None:
    """
    Returns one row from the database.
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)  # pyright: ignore[reportArgumentType]
            return cursor.fetchone()


def get_first(
    query: str,
    args: Optional[dict] = None,
    db_url: Optional[str] = TAIGA_DB_URL,
) -> TupleRow | None:
    """
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)  # pyright: ignore[reportArgumentType]
            return cursor.fetchall()[0]


def get_all(
    query: str,
    args: Optional[dict] = None,
    db_url: Optional[str] = TAIGA_DB_URL,
) -> list[TupleRow] | None:
    """
    Example:

        ...
        WHERE
            u.telegram_id = %(chat_id)s
        ...

        args = {"chat_id": chat_id}
    """
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)  # pyright: ignore[reportArgumentType]
            return cursor.fetchall()


def execute_query(
    query: str,
    args: Optional[dict] = None,
    db_url: Optional[str] = TAIGA_DB_URL,
) -> None:
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
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)  # pyright: ignore[reportArgumentType]
            conn.commit()


def query_columns(
    query_sql: str,
    db_url: Optional[str] = TAIGA_DB_URL,
) -> List[str]:
    # Get report column names
    query = f"""
SELECT json_object_keys(row_to_json(t)) FROM
({query_sql} LIMIT 1) t
    """
    report_columns = get_all(query, db_url=db_url)
    if not report_columns:
        raise ValueError("Report columns not found")
    columns: list[str] = []
    for column in report_columns:
        columns.append(str(column[0]))
    return columns


if __name__ == "__main__":
    load_dotenv()
    get_all("SELECT * FROM bot_users")
    pass
