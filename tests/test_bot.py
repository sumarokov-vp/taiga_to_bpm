# My Stuff
from bot_interface.bot_instance import bot
from bot_interface.handlers import (
    Command,
    State,
    all_callback_query_handler,
    command_start,
    edit_report_query_next_step,
)
from core.models import TUser

NEW_CHAT_ID = 5465927463
EXISTING_CHAT_ID = 65310


def test_send_message():
    msg = bot.send_message(EXISTING_CHAT_ID, "Test message")
    assert msg


def test_start_for_not_known_user():
    """Test start command for user that is not in the database"""
    with TUser(chat_id=NEW_CHAT_ID) as user:
        msg = command_start(user.tg_message)
        assert msg
        txt = (
            f"You have no allowed reports\nsend you id to administrator:\n{NEW_CHAT_ID}"
        )
        assert msg.text == txt


def test_2_report():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.REPORTS_O.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "2"
        msg = all_callback_query_handler(test_user.callback_query)

        assert msg


def test_5_report():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.REPORTS_O.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "5"
        msg = all_callback_query_handler(test_user.callback_query)

        assert msg


def test_6_report():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.REPORTS_O.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "6"
        msg = all_callback_query_handler(test_user.callback_query)

        assert msg


def test_7_report():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.REPORTS_O.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "7"
        msg = all_callback_query_handler(test_user.callback_query)

        assert msg


def test_commands_menu():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMANDS_I.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "0"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg


def test_commands_edit_reports():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMANDS_O.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = str(Command.EDIT_REPORTS.value)
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text == "Редактировать отчет"


def test_commands_edit_report_3():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "6"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Отчет:")


def test_commands_edit_report_4():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS.name
        test_user.user.save_to_redis()
        test_user.callback_query.data = "4"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Отчет:")


def test_commands_edit_report_3_edit_permissions():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORT.name
        test_user.user.report_id = 3
        test_user.user.save_to_redis()
        test_user.callback_query.data = str(Command.EDIT_REPORTS_PERMISSIONS.value)
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Редактировать разрешения")


def test_commands_edit_report_4_edit_query():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORT.name
        test_user.user.report_id = 4
        test_user.user.save_to_redis()
        test_user.callback_query.data = str(Command.EDIT_REPORTS_QUERY.value)
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Редактировать запрос")


def test_commands_edit_report_4_edit_query_new_text():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS_QUERY.name
        test_user.user.report_id = 4
        test_user.user.save_to_redis()
        test_user.tg_message.text = "SELECT * FROM TABLE"
        msg = edit_report_query_next_step(test_user.tg_message)
        assert msg.text
        assert msg.text.startswith("Query updated")


def test_commands_edit_report_3_edit_permissions_add():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS.name
        test_user.user.report_id = 3
        test_user.user.save_to_redis()
        test_user.callback_query.data = str(Command.EDIT_REPORTS_PERMISSIONS_ADD.value)
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Добавить разрешение")


def test_commands_edit_report_3_edit_permissions_remove():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS.name
        test_user.user.report_id = 3
        test_user.user.save_to_redis()
        test_user.callback_query.data = str(
            Command.EDIT_REPORTS_PERMISSIONS_REMOVE.value
        )
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Удалить разрешение")


def test_commands_edit_report_3_edit_permissions_add_stakeholder():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS_ADD.name
        test_user.user.report_id = 3
        test_user.user.save_to_redis()
        test_user.callback_query.data = "2"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Permission added")


def test_commands_edit_report_3_edit_permissions_remove_stakeholder():
    with TUser(chat_id=EXISTING_CHAT_ID, delete_on_exit=False) as test_user:
        test_user.user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS_REMOVE.name
        test_user.user.report_id = 3
        test_user.user.save_to_redis()
        test_user.callback_query.data = "2"
        msg = all_callback_query_handler(test_user.callback_query)
        assert msg.text
        assert msg.text.startswith("Permission removed")
