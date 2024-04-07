# My Stuff
from taiga_to_bpm.creatio_worker import create_receipt
from dotenv import load_dotenv

load_dotenv()


def test_create_receipt():
    message = create_receipt(1)
    assert message == "Success"
