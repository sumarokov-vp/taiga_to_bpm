# Standard Library
from os import getenv

# Third Party Stuff
from dotenv import load_dotenv
from redis import Redis

load_dotenv()

REDIS_HOST = getenv("REDIS_HOST")
if not REDIS_HOST:
    raise ValueError("REDIS_HOST is not set")

port = getenv("REDIS_PORT")
if not port:
    raise ValueError("REDIS_PORT is not set")
REDIS_PORT = int(port)

db = getenv("REDIS_DB")
if not db:
    raise ValueError("REDIS_DB is not set")
REDIS_DB = int(db)

redis_connection = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    encoding="utf-8",
)
