# Third Party Stuff
from dotenv import load_dotenv

# My Stuff
from bot_interface.topay_closer import (
    State,
    all_callback_query_handler,
)
from core.models import TUser
from db.db_worker import (
    CREATIO_DB_URL,
    execute_query,
    get_one,
)
from taiga_to_bpm.creatio_worker import (
    Receipt,
)

TEST_TASK_ID = 314
TEST_PROJECT_ID = 9
EXISTING_CHAT_ID = 65310

load_dotenv()


def before_test():
    query = """
UPDATE tasks_task t
SET status_id = ps.topay_status_id
FROM bpm_project_settings ps WHERE ps.project_id = t.project_id AND t.id = %(task_id)s;
    """
    args = {
        "task_id": TEST_TASK_ID,
    }
    execute_query(query, args)


def after_test():
    query = """
UPDATE tasks_task t
SET status_id = ps.task_finished_status_id
FROM bpm_project_settings ps WHERE ps.project_id = t.project_id AND t.id = %(task_id)s;
        """
    args = {
        "task_id": TEST_TASK_ID,
    }
    execute_query(query, args)


def test_new_receipt():
    before_test()
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.PROJECT_SELECTED.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = f"topay_closer#{TEST_PROJECT_ID}"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg
        assert msg.text
        receipt = Receipt.get_from_url(msg.text)
        query = """
    SELECT "Id"
    FROM public."SLReceipt"
    WHERE "Id" = %(receipt_id)s
            """
        args = {
            "receipt_id": receipt.guid,
        }
        receipt_dict = get_one(query, args, db_url=CREATIO_DB_URL)
        assert receipt_dict
        receipt.delete(CREATIO_DB_URL)
    after_test()
