# Third Party Stuff
from telebot.types import Message

# My Stuff
from db.db_worker import get_all


def taiga_reports_allowed(message: Message) -> bool:
    user_roles = get_all(
        """ 
SELECT
	u.id as user_id,
	r."name" s role_name
FROM bot_users u
JOIN bot_user_roles ur on ur.user_id=u.id
JOIN bot_roles r ON ur.role_id = r.id
WHERE 
r.allow_taiga_reports
and telegram_id = %s;
        """,
        message.from_user.id,
    )
    if not user_roles:
        return False
    if len(user_roles) == 0:
        return False
    return True


def finance_reports_allowed(message: Message) -> bool:
    user_roles = get_all(
        """ 
SELECT
	u.id as user_id,
	r."name" s role_name
FROM bot_users u
JOIN bot_user_roles ur on ur.user_id=u.id
JOIN bot_roles r ON ur.role_id = r.id
WHERE 
r.allow_finance_reports
and telegram_id = %s;
        """,
        message.from_user.id,
    )
    if not user_roles:
        return False
    if len(user_roles) == 0:
        return False
    return True
