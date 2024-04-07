# Standard Library
from os import environ
from typing import (
    List,
    LiteralString,
)

# Third Party Stuff
from psycopg import connect
from psycopg.rows import TupleRow


def get_one(query: LiteralString, *args) -> TupleRow | None:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchone()


def get_first(query: LiteralString, *args) -> TupleRow | None:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()[0]


def get_all(query: LiteralString, *args) -> List[TupleRow] | None:
    db_url = environ.get("DB_URL")
    if not db_url:
        raise ValueError("DB_URL environment variable not set")
    with connect(conninfo=db_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()
