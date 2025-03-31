"""
All bot handlers are here
"""

from __future__ import annotations

# Standard Library
from enum import (
    Enum,
    auto,
)

# Third Party Stuff
from telebot.types import (  # type: ignore[import-untyped]
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# My Stuff
import bot_interface.topay_closer as topay_closer
from bot_interface.bot_instance import (
    bot,
    list_buttons,
)
from bot_interface.report_generator import generate_report
from core.models import User
from db.db_worker import (
    execute_query,
    get_all,
    get_one,
)

# from taiga_to_bpm.creatio_worker import create_receipt


class State(Enum):
    """
    Bot states. Saved in User.bot_state (string State.name) and stored in redis
    """

    COMMANDS_I = auto()
    COMMANDS_O = auto()
    REPORTS_I = auto()
    REPORTS_O = auto()
    COMMAND_EDIT_REPORTS = auto()
    COMMAND_EDIT_REPORT = auto()
    COMMAND_EDIT_REPORTS_PERMISSIONS = auto()
    COMMAND_EDIT_REPORTS_PERMISSIONS_ADD = auto()
    COMMAND_EDIT_REPORTS_PERMISSIONS_REMOVE = auto()
    COMMAND_EDIT_REPORTS_QUERY = auto()


class Command(Enum):
    """
    Bot commands. Saved in User.bot_state_value (int Command.value) and stored in redis
    """

    CLOSE_TOPAY = 1
    EDIT_REPORTS = 2
    EDIT_REPORTS_PERMISSIONS = 3
    EDIT_REPORTS_QUERY = 4
    EDIT_REPORTS_PERMISSIONS_ADD = 5
    EDIT_REPORTS_PERMISSIONS_REMOVE = 6


def router(user: User) -> Message:
    """
    Router for bot commands.
    All handlers get User instance, sets State and Command to it and run this function.
    """
    match user.bot_state:
        case State.COMMANDS_I.name:
            # Show allowed commands, default state
            # Used when user sends /commands bot command
            return show_allowed_commands(user.chat_id)
        case State.COMMANDS_O.name:
            """
            Handle command selection in /commands menu
            Commands are stored in database in bot_commands table
            Values of Enum Command are used as command `id` field
              in bot_commands table
            """
            match user.bot_state_value:
                case Command.CLOSE_TOPAY.value:
                    user.bot_state = topay_closer.State.STARTED.name
                    return topay_closer.router(user)
                case Command.EDIT_REPORTS.value:
                    return edit_reports(user)
                case _:
                    return bot.send_message(
                        chat_id=user.chat_id,
                        text="Error: unknown command",
                    )
        case State.REPORTS_I.name:
            return show_allowed_reports(user.chat_id)
        case State.REPORTS_O.name:
            return generate_report(user)
        case State.COMMAND_EDIT_REPORTS.name:
            return edit_report(user)
        case State.COMMAND_EDIT_REPORT.name:
            match user.bot_state_value:
                case Command.EDIT_REPORTS_PERMISSIONS.value:
                    return edit_report_permissions(user)
                case Command.EDIT_REPORTS_QUERY.value:
                    return edit_report_query(user)
                case _:
                    return bot.send_message(
                        chat_id=user.chat_id,
                        text="Error: unknown command",
                    )
        case State.COMMAND_EDIT_REPORTS_PERMISSIONS.name:
            match user.bot_state_value:
                case Command.EDIT_REPORTS_PERMISSIONS_ADD.value:
                    return edit_report_permissions_add(user)
                case Command.EDIT_REPORTS_PERMISSIONS_REMOVE.value:
                    return edit_report_permissions_remove(user)
        case State.COMMAND_EDIT_REPORTS_PERMISSIONS_ADD.name:
            return edit_report_permissions_add_role(user)
        case State.COMMAND_EDIT_REPORTS_PERMISSIONS_REMOVE.name:
            return edit_report_permissions_remove_role(user)

        case _:
            pass
    return bot.send_message(
        chat_id=user.chat_id,
        text="Error: unknown state",
    )


@bot.message_handler(
    commands=["reports"],
    chat_types=["private"],
)
def command_reports(message: Message) -> Message:
    user = User.get_from_redis(message.from_user.id)
    if not user:
        user = User(
            chat_id=message.from_user.id,
            name=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user.save_to_redis()

    user.bot_state = State.REPORTS_I.name
    return router(user)


@bot.callback_query_handler(func=lambda c: (c.data.startswith("main#")))
def all_callback_query_handler(callback_query: CallbackQuery) -> Message:
    user = User.get_from_redis(callback_query.from_user.id)
    if not user:
        return bot.send_message(
            chat_id=callback_query.from_user.id,
            text="Error: conversation not found, restart your command",
        )
    try:
        bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )
    except Exception:
        pass
    user.bot_state_value = int(callback_query.data.split("#")[1])
    return router(user)


@bot.message_handler(
    commands=["start"],
    chat_types=["private"],
)
def command_start(message: Message) -> Message:
    user = User(
        chat_id=message.from_user.id,
        name=message.from_user.username,
        full_name=message.from_user.full_name,
        bot_state=State.REPORTS_I.name,
    )
    user.save_to_redis()
    user.save_to_db()
    return router(user)


@bot.message_handler(
    commands=["my_id", "myid"],
    chat_types=["private"],
)
def command_my_id(message: Message):
    """ """
    bot.reply_to(message, str(message.from_user.id))


@bot.message_handler(
    commands=["commands"],
    chat_types=["private"],
)
def command_commands(message: Message) -> Message:
    user = User.get_from_redis(message.from_user.id)
    if not user:
        user = User(
            chat_id=message.from_user.id,
            name=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user.save_to_redis()
    user.bot_state = State.COMMANDS_I.name
    return router(user)


def show_allowed_reports(chat_id: int) -> Message:
    query = """
SELECT r.id, r."name"
FROM bot_reports r
JOIN bot_roles_reports rr on rr.report_id = r.id
JOIN bot_user_roles ur on ur.role_id = rr.role_id
JOIN bot_users u on u.id = ur.user_id
WHERE
	u.telegram_id = %(chat_id)s
    ;
        """
    args = {"chat_id": chat_id}
    reports = get_all(query, args)
    if not reports:
        txt = f"You have no allowed reports\nsend you id to administrator:\n`{chat_id}`"
        return bot.send_message(
            chat_id=chat_id,
            text=txt,
        )
    keyboard = list_buttons(reports, "main#")

    User.set_state(chat_id, State.REPORTS_O.name)

    return bot.send_message(
        chat_id=chat_id,
        text="Доступные отчеты",
        reply_markup=keyboard,
    )


def show_allowed_commands(chat_id: int) -> Message:
    query = """
SELECT c.id, c."name"
FROM bot_commands c
JOIN bot_roles_commands rc on rc.command_id = c.id
JOIN bot_user_roles ur on ur.role_id = rc.role_id
JOIN bot_users u on u.id = ur.user_id
WHERE
	u.telegram_id = %(chat_id)s
;
        """
    args = {"chat_id": chat_id}
    commands = get_all(query, args)
    if not commands:
        return bot.send_message(chat_id=chat_id, text="You have no allowed commands")
    keyboard = list_buttons(commands, "main#")

    User.set_state(chat_id, State.COMMANDS_O.name)
    return bot.send_message(
        chat_id=chat_id,
        text="Доступные команды",
        reply_markup=keyboard,
    )


def edit_reports(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    query = """
    SELECT id, "name"
    FROM bot_reports
    """
    reports = get_all(query)
    if not reports:
        return bot.send_message(
            chat_id=user.chat_id,
            text="No reports found",
        )
    keyboard = list_buttons(reports, "main#")
    user.bot_state = State.COMMAND_EDIT_REPORTS.name
    user.save_to_redis()
    return bot.send_message(user.chat_id, "Редактировать отчет", reply_markup=keyboard)


def edit_report(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    report_id = user.bot_state_value
    user.report_id = report_id
    keyboard = InlineKeyboardMarkup()
    query = """
    SELECT "name", report_query
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": report_id}
    report = get_one(query, args)
    if not report:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: report not found",
        )
    report_name = report[0]
    report_query = report[1]

    button_permissions = InlineKeyboardButton(
        text="Редактировать разрешения",
        callback_data=f"{Command.EDIT_REPORTS_PERMISSIONS.value}",
    )
    button_query = InlineKeyboardButton(
        text="Редактировать запрос",
        callback_data=f"{Command.EDIT_REPORTS_QUERY.value}",
    )
    keyboard.add(button_permissions)
    keyboard.add(button_query)

    user.bot_state = State.COMMAND_EDIT_REPORT.name
    user.save_to_redis()
    txt = f"""
Отчет: `{report_name}`
```sql
{report_query}
```
    """
    return bot.send_message(
        user.chat_id,
        text=txt,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


def edit_report_query(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    report_id = user.bot_state_value
    user.report_id = report_id
    query = """
    SELECT "name", report_query
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": report_id}
    report = get_one(query, args)
    if not report:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: report not found",
        )
    report_name = report[0]
    report_query = report[1]
    user.bot_state = State.COMMAND_EDIT_REPORTS_QUERY.name
    user.save_to_redis()
    txt = f"""Редактировать запрос
Отчет: `{report_name}`

```sql
{report_query}
```

Введите новый запрос
    """

    msg = bot.send_message(
        user.chat_id,
        text=txt,
    )
    bot.register_next_step_handler(msg, edit_report_query_next_step)
    return msg


def edit_report_query_next_step(message: Message) -> Message:
    user = User.get_from_redis(message.from_user.id)
    if not user:
        return bot.send_message(
            chat_id=message.from_user.id,
            text="Error: conversation not found, restart your command",
        )
    report_id = user.report_id
    query = """
    UPDATE bot_reports
    SET report_query = %(report_query)s
    WHERE id = %(report_id)s
    """
    args = {"report_query": message.text, "report_id": report_id}
    execute_query(query, args)
    return bot.send_message(
        chat_id=message.chat.id,
        text="Query updated",
    )


def edit_report_permissions(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    # Get report name
    query = """
    SELECT "name"
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": user.report_id}
    result = get_one(query, args)
    if not result:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: report not found",
        )
    report_name = result[0]

    # Get all allowed roles for report
    query = """
    SELECT bot_roles."name"
    FROM bot_roles
    JOIN bot_roles_reports rr on rr.role_id = bot_roles.id
    WHERE rr.report_id = %(report_id)s
    """
    args = {"report_id": user.report_id}
    allowed_roles = get_all(query, args)

    # Get all unallowed roles for report
    query = """
    SELECT bot_roles."name"
    FROM bot_roles
    WHERE id NOT IN (
    SELECT role_id
    FROM bot_roles_reports
    WHERE report_id = %(report_id)s)
    """
    args = {"report_id": user.report_id}
    unallowed_roles = get_all(query, args)

    keyboard = InlineKeyboardMarkup()
    button_add = InlineKeyboardButton(
        text="Добавить разрешение",
        callback_data=f"{Command.EDIT_REPORTS_PERMISSIONS_ADD.value}",
    )
    button_remove = InlineKeyboardButton(
        text="Удалить разрешение",
        callback_data=f"{Command.EDIT_REPORTS_PERMISSIONS_REMOVE.value}",
    )
    keyboard.add(button_add)
    keyboard.add(button_remove)
    user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS.name
    user.save_to_redis()
    return bot.send_message(
        user.chat_id,
        f"""
Редактировать разрешения

Отчет: `{report_name}`

Разрешенные роли:
```
{allowed_roles}
```

Неразрешенные роли:
```
{unallowed_roles}
```
""",
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


def edit_report_permissions_add(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )

    # Get report name
    query = """
    SELECT "name"
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": user.report_id}
    result = get_one(query, args)
    if not result:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: report not found",
        )
    report_name = result[0]

    # Get all unallowed roles for report
    query = """
    SELECT bot_roles.id,bot_roles."name"
    FROM bot_roles
    WHERE id NOT IN (
    SELECT role_id
    FROM bot_roles_reports
    WHERE report_id = %(report_id)s)
    """
    args = {"report_id": user.report_id}
    unallowed_roles = get_all(query, args)
    if not unallowed_roles:
        return bot.send_message(
            chat_id=user.chat_id,
            text="All roles are allowed",
        )
    keyboard = list_buttons(unallowed_roles, "main#")

    user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS_ADD.name
    user.save_to_redis()
    return bot.send_message(
        user.chat_id,
        f"""
Добавить разрешение

Отчет: `{report_name}`
        """,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


def edit_report_permissions_remove(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )

    # Get report name
    query = """
    SELECT "name"
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": user.report_id}
    result = get_one(query, args)
    if not result:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: report not found",
        )
    report_name = result[0]

    # Get all allowed roles for report
    query = """
    SELECT bot_roles.id,bot_roles."name"
    FROM bot_roles
    JOIN bot_roles_reports rr on rr.role_id = bot_roles.id
    WHERE rr.report_id = %(report_id)s
    """
    args = {"report_id": user.report_id}
    allowed_roles = get_all(query, args)
    if not allowed_roles:
        return bot.send_message(
            chat_id=user.chat_id,
            text="All roles are unallowed",
        )
    keyboard = list_buttons(allowed_roles, "main#")
    user.bot_state = State.COMMAND_EDIT_REPORTS_PERMISSIONS_REMOVE.name
    user.save_to_redis()
    return bot.send_message(
        user.chat_id,
        f"""
Удалить разрешение

Отчет: `{report_name}`
        """,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


def edit_report_permissions_add_role(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    role_id = user.bot_state_value
    query = """
    INSERT INTO bot_roles_reports (role_id, report_id)
    VALUES (%(role_id)s, %(report_id)s)
    """
    args = {"role_id": role_id, "report_id": user.report_id}
    execute_query(query, args)
    return bot.send_message(
        chat_id=user.chat_id,
        text="Permission added",
    )


def edit_report_permissions_remove_role(user: User) -> Message:
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: no report selected",
        )
    role_id = user.bot_state_value
    query = """
    DELETE FROM bot_roles_reports
    WHERE role_id = %(role_id)s AND report_id = %(report_id)s
    """
    args = {"role_id": role_id, "report_id": user.report_id}
    execute_query(query, args)
    return bot.send_message(
        chat_id=user.chat_id,
        text="Permission removed",
    )
