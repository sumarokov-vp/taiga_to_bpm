# Third Party Stuff
from prettytable import PrettyTable
from telebot.types import Message

# My Stuff
from bot_interface.bot_instance import bot
from bot_interface.user_roles import user_is_admin
from db.db_worker import get_all


@bot.message_handler(
    commands=["start"],
    chat_types=["private"],
    func=user_is_admin,
)
def command_start(message: Message):
    bot.reply_to(message, "Hello, admin!")


@bot.message_handler(
    commands=["my_id", "myid"],
    chat_types=["private"],
)
def command_my_id(message: Message):
    """ """
    bot.reply_to(message, str(message.from_user.id))


@bot.message_handler(
    commands=["report_31_days"],
    chat_types=["private"],
    func=user_is_admin,
)
def command_report_31_days(message: Message):
    query = """
SELECT * FROM(SELECT
	full_name,
	sum(hours) as total_hours 
FROM (
	SELECT
		ROUND(COALESCE((attr.attributes_values::json -> 
            fields.tracked_hours_id::text)::text::NUMERIC, 0) + 
            COALESCE((attr.attributes_values::json -> 
            fields.tracked_minutes_id::text)::text::NUMERIC, 0) 
        / 60,2) AS hours,

		u.full_name
	FROM
		tasks_task AS task
	LEFT JOIN custom_attributes_taskcustomattributesvalues 
        AS attr ON attr.task_id = task.id
	LEFT JOIN bpm_project_settings 
        AS fields ON fields.project_id = task.project_id
	JOIN users_user u ON u.id = assigned_to_id
WHERE
    (attr.attributes_values::json -> fields.done_date_id::text)::text::DATE >= 
        now()::DATE - 31
) AS not_grouped
GROUP BY
	full_name) as grouped
	ORDER BY total_hours DESC
;
        """
    result = get_all(query)
    if not result:
        bot.send_message(message.chat.id, "No data")
        return
    table = PrettyTable()
    table.field_names = ["Имя", "Часы"]
    for row in result:
        table.add_row(row)
    response = "```\n{}```".format(table.get_string())
    bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")


@bot.message_handler(
    commands=["report_7_days"],
    chat_types=["private"],
    func=user_is_admin,
)
def command_report_7_days(message: Message):
    query = """
SELECT * FROM(SELECT
	full_name,
	sum(hours) as total_hours 
FROM (
	SELECT
		ROUND(COALESCE((attr.attributes_values::json -> 
            fields.tracked_hours_id::text)::text::NUMERIC, 0) + 
            COALESCE((attr.attributes_values::json -> 
                fields.tracked_minutes_id::text)::text::NUMERIC, 0) 
        / 60,2) AS hours,

		u.full_name
	FROM
		tasks_task AS task
	LEFT JOIN custom_attributes_taskcustomattributesvalues 
        AS attr ON attr.task_id = task.id
	LEFT JOIN bpm_project_settings 
        AS fields ON fields.project_id = task.project_id
	JOIN users_user u ON u.id = assigned_to_id
WHERE 
    (attr.attributes_values::json -> fields.done_date_id::text)::text::DATE >= 
        now()::DATE - 7
) AS not_grouped
GROUP BY
	full_name) as grouped
	ORDER BY total_hours DESC
;
        """
    result = get_all(query)
    if not result:
        bot.send_message(message.chat.id, "No data")
        return
    table = PrettyTable()
    table.field_names = ["Имя", "Часы"]
    for row in result:
        table.add_row(row)
    response = "```\n{}```".format(table.get_string())
    bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")


if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()
