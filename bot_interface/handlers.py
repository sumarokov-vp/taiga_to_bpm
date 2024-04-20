from __future__ import annotations

# Standard Library
import os

# import traceback
from enum import (
    Enum,
    auto,
)

# Third Party Stuff
import validators
from prettytable import PrettyTable
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# My Stuff
from bot_interface.bot_instance import (
    bot,
    list_buttons,
)
from bot_interface.pdf_output import make_pdf_report
from core.models import User
from db.db_worker import (
    execute_query,
    get_all,
    get_one,
)

# from taiga_to_bpm.creatio_worker import create_receipt


class State(Enum):
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


class Report(Enum):
    HOURS_7_DAYS = 1
    HOURS_31_DAYS = 2


class Command(Enum):
    CLOSE_TOPAY = 1
    EDIT_REPORTS = 2
    EDIT_REPORTS_PERMISSIONS = 3
    EDIT_REPORTS_QUERY = 4
    EDIT_REPORTS_PERMISSIONS_ADD = 5
    EDIT_REPORTS_PERMISSIONS_REMOVE = 6


class ReportEngine(Enum):
    PDF = "pdf"
    MD = "md"
    RAW = "raw"


def router(user: User) -> Message:
    match user.bot_state:
        case State.COMMANDS_I.name:
            return show_allowed_commands(user.chat_id)
        case State.COMMANDS_O.name:
            match user.bot_state_value:
                case Command.CLOSE_TOPAY.value:
                    pass
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


@bot.callback_query_handler(func=lambda c: True)
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
    user.bot_state_value = int(callback_query.data)
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
    keyboard = list_buttons(reports)

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
    keyboard = list_buttons(commands)

    User.set_state(chat_id, State.COMMANDS_O.name)
    return bot.send_message(
        chat_id=chat_id,
        text="Доступные команды",
        reply_markup=keyboard,
    )


def generate_report(user: User) -> Message:
    """
    Generate and send report to user telegram chat
    returns telegram message


    """
    chat_id = user.chat_id
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=chat_id,
            text="Error: no report selected",
        )
    report_id = user.bot_state_value

    # Get report (query, name, engine, slug)
    # slug is used for filename creation
    # report_engine is used for determining report output format (pdf, md)
    # report name is used for report title
    query = """
    SELECT report_query, "name", report_engine, slug
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": report_id}
    report_query_row = get_one(query, args)
    if not report_query_row:
        return bot.send_message(
            chat_id=chat_id,
            text="Error: report not found in database",
        )
    report_query = report_query_row[0]
    report_name: str = report_query_row[1]
    report_engine: str = report_query_row[2]
    slug: str = report_query_row[3]

    report_result_rows = get_all(report_query)
    if not report_result_rows:
        return bot.send_message(chat_id, "No data")

    # convert Tuples collection to list
    result_list = [list(row) for row in report_result_rows]

    # Make url links clickable for markdown -> pdf
    for row in result_list:
        for i, cell in enumerate(row):
            if validators.url(cell):
                row[i] = f"[link]({cell})"

    # Get report column names
    query = f"""
SELECT json_object_keys(row_to_json(t)) FROM
({report_query} LIMIT 1) t
    """
    report_columns = get_all(query)
    if not report_columns:
        return bot.send_message(
            chat_id=chat_id,
            text="Error: report columns not found",
        )
    columns = []
    for column in report_columns:
        columns.append(column[0])

    # Generate report based on engine
    match report_engine:
        case ReportEngine.PDF.value:
            # make file name
            file_name = slug + ".pdf"
            full_path = os.path.join(os.getcwd(), file_name)

            # Calculate total
            # if last column is numeric sum it
            # if not just add empty string
            total = 0
            total_footer = []
            try:
                for row in result_list:
                    total += row[-1]
                for cell in columns:
                    total_footer.append("-")
                total_footer[-1] = total
                total_footer[0] = "Total"
            except Exception:
                pass

            # Generate report file
            make_pdf_report(
                footers=total_footer,
                title=report_name,
                headers=columns,
                data=result_list,
                output_file=full_path,
            )

            # Send file
            return bot.send_document(chat_id, open(full_path, "rb"))

        case ReportEngine.MD.value:
            table = PrettyTable()
            table.title = report_name
            all_columns = []
            for column in report_columns:
                all_columns.append(column[0])
            table.field_names = all_columns
            for row in result_list:
                table.add_row(row)
            response = "```\n{}```".format(table.get_string())
            return bot.send_message(chat_id, response, parse_mode="MarkdownV2")

        case ReportEngine.RAW.value:
            text = ""
            for row in result_list:
                for cell in row:
                    text += f"{cell}\t"
                text += "\n"
            return bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2",
            )

    return bot.send_message(chat_id, "Unknown report engine")


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
    keyboard = list_buttons(reports)
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
    keyboard = list_buttons(unallowed_roles)

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
    keyboard = list_buttons(allowed_roles)
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


#
# @bot.callback_query_handler(
#     # chat_types=["private"],
#     func=lambda c: (c.data.startswith(f"command#{Command.CLOSE_TOPAY.value}")),
# )
# def callback_close_topay_command(callback_query: CallbackQuery) -> Message:
#     # Show project list
#     query = """


#         SELECT id, name
#     FROM projects_project
#     ORDER BY name
#     ;
#     """
#     projects = get_all(query)
#     keyboard = InlineKeyboardMarkup()
#     if not projects:
#         return bot.send_message(
#             chat_id=callback_query.from_user.id,
#             text="No projects found",
#         )
#     for project in projects:
#         keyboard.add(
#             InlineKeyboardButton(
#                 text=project[1],
#                 callback_data=
#                 f"command${Command.CLOSE_TOPAY.value}$project#{project[0]}",
#             )
#         )
#     return bot.send_message(
#         chat_id=callback_query.from_user.id,
#         text="Выберите проект",
#         reply_markup=keyboard,
#     )
#

#
# @bot.callback_query_handler(
#     # chat_types=["private"],
#     func=lambda c:
#     (c.data.startswith(f"command${Command.CLOSE_TOPAY.value}$project#")),
# )
# def callback_close_topay_project(callback_query: CallbackQuery) -> Message:
#     project_id = int(callback_query.data.split("#")[1])
#     try:
#         receipt = create_receipt(project_id)
#     except Exception as e:
#         # send traceback as file
#         with open("traceback.txt", "w") as f:
#             f.write(traceback.format_exc())
#         with open("traceback.txt", "rb") as f:
#             bot.send_document(
#                 chat_id=callback_query.from_user.id,
#                 document=f,
#             )
#         return bot.send_message(
#             chat_id=callback_query.from_user.id,
#             text=f"Error: {e}",
#         )
#     return bot.send_message(
#         chat_id=callback_query.from_user.id,
#         text=receipt,
#     )
