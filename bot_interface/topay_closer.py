from __future__ import annotations

# Standard Library
import traceback
from enum import (
    Enum,
    auto,
)

# Third Party Stuff
from telebot.types import (  # type: ignore[import-untyped]
    CallbackQuery,
    Message,
)

# My Stuff
from bot_interface.bot_instance import (
    bot,
    list_buttons,
    replace_reserved_characters,
)
from core.models import User
from db.db_worker import (
    execute_query,
    get_all,
)
from taiga_to_bpm.creatio_worker import (
    Receipt,
    get_tasks,
)

from .utils.send_file import SendFile

# from taiga_to_bpm.creatio_worker import create_receipt


class State(Enum):
    """
    Bot states. Saved in User.bot_state (string State.name) and stored in redis
    """

    STARTED = auto()
    PROJECT_SELECTED = auto()


class Command(Enum):
    """
    Bot commands. Saved in User.bot_state_value (int Command.value) and stored in redis
    """

    CLOSE_TOPAY = 1


def router(user: User) -> Message:
    """
    Router for bot commands.
    All handlers get User instance, sets State and Command to it and run this function.
    """
    match user.bot_state:
        case State.STARTED.name:
            return show_project_list(user)
        case State.PROJECT_SELECTED.name:
            return create_new_receipt(user)
    return bot.send_message(
        chat_id=user.chat_id,
        text="Error: unknown state",
    )


@bot.callback_query_handler(func=lambda c: (c.data.startswith("topay_closer#")))
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


def create_new_receipt(user: User) -> Message:
    project_id = user.bot_state_value
    send_file = SendFile(bot, user.chat_id)
    bot.send_message(
        chat_id=user.chat_id,
        text="Creating receipt",
    )
    if not project_id:
        return bot.send_message(
            chat_id=user.chat_id,
            text="Error: project_id is None",
        )
    try:
        tasks = get_tasks(project_id)
        desk_guid = tasks[0].desk_guid
        receipt = Receipt.new(desk_guid)
        bot.send_message(
            chat_id=user.chat_id,
            text="Receipt created, adding tasks to it",
        )
    except Exception as e:
        send_file.text(traceback.format_exc())
        txt = replace_reserved_characters(str(e))
        return bot.send_message(
            chat_id=user.chat_id,
            text=txt,
        )

    try:
        for task in tasks:
            task.push_to_creatio(receipt.guid)
            bot.send_message(
                chat_id=user.chat_id,
                text=f"Task {task.id} added to receipt",
            )
    except Exception as e:
        send_file.text(traceback.format_exc())
        txt = replace_reserved_characters(str(e))
        return bot.send_message(
            chat_id=user.chat_id,
            text=txt,
        )

    # Move tasks to finished (Paid) status
    query = """
UPDATE
tasks_task t
SET
status_id = ps.task_finished_status_id
FROM
bpm_project_settings ps
WHERE
ps.project_id = t.project_id
AND t.status_id = ps.topay_status_id
AND t.project_id = %(project_id)s
    """
    args = {"project_id": project_id}
    execute_query(query, args)
    txt = replace_reserved_characters(receipt.url)
    return bot.send_message(
        chat_id=user.chat_id,
        text=txt,
    )


def show_project_list(user: User) -> Message:
    """
    Start topay closer
    Get projects from database
    Show project list
    """
    query = """
SELECT id, name
FROM projects_project
ORDER BY name
;
    """
    projects = get_all(query)
    if not projects:
        return bot.send_message(
            chat_id=user.chat_id,
            text="No projects found",
        )
    keyboard = list_buttons(projects, "topay_closer#")
    user.bot_state = State.PROJECT_SELECTED.name
    user.save_to_redis()
    return bot.send_message(
        chat_id=user.chat_id,
        text="Выберите проект",
        reply_markup=keyboard,
    )
