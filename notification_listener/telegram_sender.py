# Standard Library
import json
import logging
from typing import (
    Any,
    Dict,
    List,
)

# Third Party Stuff
from telebot import TeleBot  # type: ignore

# My Stuff
# Local Application
from notification_listener.interfaces import INotificationSender, IDataStorage


class TelegramNotificationSender(INotificationSender):
    """Sends notifications to Telegram users with scrum_master role"""

    def __init__(
        self,
        data_storage: IDataStorage,
        bot: TeleBot,
        base_url: str = "https://taiga.smartist.dev",
    ) -> None:
        """Initialize sender with data storage and bot instance

        Args:
            data_storage: Data storage implementation for database access
            bot: Telegram bot instance
            base_url: Base URL for Taiga instance to generate links
        """
        self.logger = logging.getLogger("telegram_sender")
        self.data_storage = data_storage
        self.bot = bot
        self.base_url = base_url

        # Словарь для перевода типов событий на русский
        self.event_translations = {
            "userstories.userstory.change": "Изменение истории пользователя",
            "userstories.userstory.create": "Создание истории пользователя",
            "userstories.userstory.delete": "Удаление истории пользователя",
            "tasks.task.change": "Изменение задачи",
            "tasks.task.create": "Создание задачи",
            "tasks.task.delete": "Удаление задачи",
            "epics.epic.change": "Изменение эпика",
            "epics.epic.create": "Создание эпика",
            "epics.epic.delete": "Удаление эпика",
            "issues.issue.change": "Изменение проблемы",
            "issues.issue.create": "Создание проблемы",
            "issues.issue.delete": "Удаление проблемы",
            "milestones.milestone.change": "Изменение спринта",
            "milestones.milestone.create": "Создание спринта",
            "milestones.milestone.delete": "Удаление спринта",
        }

    def get_scrum_masters(self) -> List[int]:
        """Get telegram_ids of all users with scrum_master role (id=1)

        Returns:
            List of telegram_ids
        """
        users = self.data_storage.get_users_by_role_id(1)  # scrum_master role_id=1
        if not users:
            self.logger.warning("No scrum masters found in database")
            return []

        telegram_ids = [user["telegram_id"] for user in users]
        return telegram_ids

    def send_notification(self, payload: Dict[str, Any]) -> None:
        """Send notification to all scrum masters

        Args:
            payload: The notification payload as a dictionary
        """
        self.logger.info("Sending notification to scrum masters")

        # Get all scrum masters telegram IDs
        telegram_ids = self.get_scrum_masters()
        if not telegram_ids:
            self.logger.warning("No scrum masters to notify")
            return

        try:
            # Логируем полученный payload для отладки
            payload_str = json.dumps(payload, ensure_ascii=False)
            self.logger.info(f"Received payload: {payload_str}")

            # Получаем тип события и JSONB-данные события
            event_type = payload.get("event_type", "unknown")
            timeline_data = None

            # Структура данных в timeline_timeline отличается
            if "data" in payload and payload["data"]:
                # data может быть строкой JSON или уже словарем
                if isinstance(payload["data"], str):
                    try:
                        timeline_data = json.loads(payload["data"])
                    except json.JSONDecodeError:
                        self.logger.error("Failed to parse data JSON string")
                else:
                    timeline_data = payload["data"]
                self.logger.debug("Successfully parsed timeline data")

            if not timeline_data:
                self.logger.warning("No valid data found in payload")
                timeline_data = {}

            # Получаем информацию в зависимости от типа события
            # Для задач, историй пользователя, и т.д. структура разная
            content_type = "unknown"
            subject = "Без названия"
            ref = None
            project_slug = None
            object_data = {}

            # Определяем тип события и извлекаем соответствующие данные
            if "project" in timeline_data:
                project = timeline_data.get("project", {})
                project_slug = project.get("slug")

            # Событие связано с историей пользователя
            # Анализируем изменения из values_diff и comment_html
            changes_description = []

            if event_type.startswith("userstories."):
                content_type = "us"  # Используем правильный путь в URL
                object_data = timeline_data.get("userstory", {})
            # Событие связано с задачей
            elif event_type.startswith("tasks."):
                content_type = "task"
                object_data = timeline_data.get("task", {})

                # Добавляем информацию о создателе задачи, если это создание задачи
                if event_type == "tasks.task.create" and "owner" in object_data:
                    owner = object_data.get("owner")
                    owner_name = "Неизвестный пользователь"

                    if isinstance(owner, dict):
                        if "id" in owner:
                            # Получаем имя создателя из базы
                            owner_id = owner["id"]
                            owner_data = self.data_storage.get_taiga_user_by_id(
                                owner_id
                            )
                            if owner_data:
                                if owner_data.get("full_name"):
                                    owner_name = owner_data["full_name"]
                                elif owner_data.get("username"):
                                    owner_name = owner_data["username"]
                                else:
                                    owner_name = f"Пользователь #{owner_id}"
                        elif "name" in owner:
                            owner_name = owner["name"]

                    changes_description.append(f"📝 Создатель: {owner_name}")

                # Добавляем информацию об исполнителе
                if event_type == "tasks.task.create" and "assigned_to" in object_data:
                    assigned = object_data.get("assigned_to")
                    if assigned:
                        assigned_name = "Неизвестный пользователь"

                        if isinstance(assigned, dict):
                            if "id" in assigned:
                                # Получаем имя исполнителя из базы
                                assigned_id = assigned["id"]
                                assigned_data = self.data_storage.get_taiga_user_by_id(
                                    assigned_id
                                )
                                if assigned_data:
                                    if assigned_data.get("full_name"):
                                        assigned_name = assigned_data["full_name"]
                                    elif assigned_data.get("username"):
                                        assigned_name = assigned_data["username"]
                                    else:
                                        assigned_name = f"Пользователь #{assigned_id}"
                            elif "name" in assigned:
                                assigned_name = assigned["name"]

                        changes_description.append(f"👤 Исполнитель: {assigned_name}")

            # Событие связано с эпиком
            elif event_type.startswith("epics."):
                content_type = "epic"
                object_data = timeline_data.get("epic", {})
            # Событие связано с задачей в спринте
            elif event_type.startswith("milestones."):
                content_type = "milestone"
                object_data = timeline_data.get("milestone", {})
            # Событие связано с issue
            elif event_type.startswith("issues."):
                content_type = "issue"
                object_data = timeline_data.get("issue", {})

            # Извлекаем общие поля из объекта
            subject = object_data.get("subject", "Без названия")
            ref = object_data.get("ref")

            # Переводим тип события на русский
            event_description = self.event_translations.get(
                event_type, f"Событие: {event_type}"
            )

            # Проверяем наличие всех необходимых параметров для URL
            if project_slug and ref:
                url = f"{self.base_url}/project/{project_slug}/{content_type}/{ref}"
            else:
                # Логируем проблему с параметрами
                self.logger.warning(
                    f"Missing URL parameters: project_slug={project_slug}, "
                    f"ref={ref}, content_type={content_type}"
                )
                # Используем URL до проекта, если доступен slug проекта
                if project_slug:
                    url = f"{self.base_url}/project/{project_slug}"
                else:
                    url = self.base_url

            # Получаем название проекта
            project_name = "Проект"
            if project and "name" in project:
                project_name = project.get("name", "Проект")

            # Проверяем наличие комментария и пользователя
            comment_html = timeline_data.get("comment_html", "")
            user = timeline_data.get("user", {})

            # Получаем имя пользователя - либо из payload, либо из базы данных
            user_name = "Неизвестный пользователь"

            # Подробный лог для отладки
            self.logger.debug(
                f"User data in payload: {json.dumps(user, ensure_ascii=False)}"
            )

            if "name" in user and user["name"]:
                # Имя есть в payload
                user_name = user["name"]
                self.logger.debug(f"Using name from payload: {user_name}")
            elif "id" in user and user["id"]:
                # Имя нужно получить из базы данных
                user_id = user["id"]
                self.logger.debug(f"Fetching taiga user with id {user_id}")

                # Пытаемся получить пользователя через более прямой запрос
                try:
                    # Здесь предполагаем, что self.data_storage это PostgresDataStorage
                    direct_query = """
                    SELECT id, username, full_name, username as name
                    FROM users_user
                    WHERE id = %(user_id)s
                    """
                    args = {"user_id": user_id}
                    self.logger.info(
                        f"DEBUG: Trying direct query for user_id={user_id}"
                    )
                    direct_user = self.data_storage.get_one(direct_query, args)
                    self.logger.info(f"DEBUG: Direct query result: {direct_user}")

                    if direct_user:
                        self.logger.info(
                            f"DEBUG: User found: full_name={direct_user.get('full_name')}, username={direct_user.get('username')}"
                        )
                        if direct_user.get("full_name"):
                            user_name = direct_user["full_name"]
                            self.logger.info(
                                f"Using direct query full_name: {user_name}"
                            )
                except Exception as e:
                    self.logger.error(f"Error getting direct user: {str(e)}")

                # Если прямой запрос не сработал, используем стандартный метод
                self.logger.info(
                    f"DEBUG: Trying get_taiga_user_by_id query for user_id={user_id}"
                )
                taiga_user = self.data_storage.get_taiga_user_by_id(user_id)
                if taiga_user:
                    self.logger.info(
                        f"DEBUG: Found taiga_user in database: {json.dumps(taiga_user)}"
                    )
                    # Приоритет: full_name > username > id
                    if taiga_user.get("full_name"):
                        user_name = taiga_user["full_name"]
                        self.logger.info(
                            f"DEBUG: Using full_name from database: {user_name}"
                        )
                    elif taiga_user.get("username"):
                        user_name = taiga_user["username"]
                        self.logger.info(
                            f"DEBUG: Using username from database: {user_name}"
                        )
                    else:
                        user_name = f"Пользователь #{user_id}"
                        self.logger.info(f"DEBUG: Using user ID as name: {user_name}")
                else:
                    self.logger.warning(
                        f"DEBUG: User with id {user_id} not found in database"
                    )
                    user_name = f"Пользователь #{user_id}"
            else:
                self.logger.warning("No user identification in payload")

            # Добавляем информацию о пользователе, внесшем изменения
            if user_name != "Неизвестный пользователь":
                changes_description.append(f"👤 Изменения внёс: {user_name}")

            if comment_html and comment_html.strip():
                # Удаляем HTML-теги для простого отображения
                comment_text = comment_html.replace("<p>", "").replace("</p>", "")
                comment_text = comment_text.strip()
                if comment_text:
                    changes_description.append(f"💬 {user_name}: {comment_text}")

            # Проверяем наличие изменений в values_diff
            values_diff = timeline_data.get("values_diff", {})
            if values_diff:
                # Изменение статуса
                if "status" in values_diff:
                    status_change = values_diff["status"]
                    if isinstance(status_change, list) and len(status_change) >= 2:
                        old_status = status_change[0]
                        new_status = status_change[1]
                        changes_description.append(
                            f"🔄 Статус: {old_status} → {new_status}"
                        )

                # Изменение исполнителя
                if "assigned_to" in values_diff:
                    assigned_change = values_diff["assigned_to"]
                    if isinstance(assigned_change, list) and len(assigned_change) >= 2:
                        # Получаем старого и нового исполнителя
                        old_assigned = assigned_change[0]
                        new_assigned = assigned_change[1]

                        # Получаем имена исполнителей
                        old_assigned_name = "Не назначен"
                        new_assigned_name = "Не назначен"

                        # Обрабатываем старого исполнителя если есть
                        if old_assigned:
                            if isinstance(old_assigned, dict) and "id" in old_assigned:
                                # Получаем имя из базы
                                old_user_id = old_assigned["id"]
                                old_user = self.data_storage.get_taiga_user_by_id(
                                    old_user_id
                                )
                                if old_user:
                                    if old_user.get("full_name"):
                                        old_assigned_name = old_user["full_name"]
                                    elif old_user.get("username"):
                                        old_assigned_name = old_user["username"]
                                    else:
                                        old_assigned_name = (
                                            f"Пользователь #{old_user_id}"
                                        )
                            elif (
                                isinstance(old_assigned, dict)
                                and "name" in old_assigned
                            ):
                                old_assigned_name = old_assigned["name"]

                        # Обрабатываем нового исполнителя если есть
                        if new_assigned:
                            if isinstance(new_assigned, dict) and "id" in new_assigned:
                                # Получаем имя из базы
                                new_user_id = new_assigned["id"]
                                new_user = self.data_storage.get_taiga_user_by_id(
                                    new_user_id
                                )
                                if new_user:
                                    if new_user.get("full_name"):
                                        new_assigned_name = new_user["full_name"]
                                    elif new_user.get("username"):
                                        new_assigned_name = new_user["username"]
                                    else:
                                        new_assigned_name = (
                                            f"Пользователь #{new_user_id}"
                                        )
                            elif (
                                isinstance(new_assigned, dict)
                                and "name" in new_assigned
                            ):
                                new_assigned_name = new_assigned["name"]

                        changes_description.append(
                            f"👤 Исполнитель: {old_assigned_name} → {new_assigned_name}"
                        )

                # Изменения в backlog_order
                if "backlog_order" in values_diff:
                    changes_description.append("📋 Изменен порядок в беклоге")

                # Изменения в пользовательских атрибутах
                if "custom_attributes" in values_diff:
                    custom_attrs = values_diff["custom_attributes"]

                    # Новые атрибуты
                    for attr in custom_attrs.get("new", []):
                        attr_name = attr.get("name", "")
                        attr_value = attr.get("value", "")

                        if attr_name and attr_value:
                            value_diff = attr.get("value_diff")
                            if isinstance(value_diff, list) and len(value_diff) >= 2:
                                # Если есть предыдущее и новое значение
                                old_val = (
                                    "-" if value_diff[0] is None else value_diff[0]
                                )
                                new_val = (
                                    "-" if value_diff[1] is None else value_diff[1]
                                )
                                changes_description.append(
                                    f"📝 {attr_name}: {old_val} → {new_val}"
                                )
                            else:
                                # Если есть только новое значение
                                changes_description.append(
                                    f"📝 {attr_name}: {attr_value}"
                                )

                    # Измененные атрибуты
                    for attr in custom_attrs.get("changed", []):
                        attr_name = attr.get("name", "")
                        if (
                            "value_diff" in attr
                            and isinstance(attr["value_diff"], list)
                            and len(attr["value_diff"]) >= 2
                        ):
                            value_diff = attr["value_diff"]
                            old_val = "-" if value_diff[0] is None else value_diff[0]
                            new_val = "-" if value_diff[1] is None else value_diff[1]
                            changes_description.append(
                                f"📝 {attr_name}: {old_val} → {new_val}"
                            )

            # Формируем блок с изменениями
            changes_block = ""
            if changes_description:
                changes_block = "\n".join(changes_description)

            # Format message
            message = (
                f"<b>{project_name}</b>\n<b>{event_description}</b>\n<i>{subject}</i>\n"
            )

            # Добавляем информацию об изменениях, если есть
            if changes_block:
                message += f"\n{changes_block}\n"

            # Добавляем ссылку
            message += f"<a href='{url}'>Открыть в Taiga</a>"
        except Exception as e:
            self.logger.error(f"Error formatting message: {str(e)}")
            # Fallback to raw payload if formatting fails
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
            message = f"<code>{payload_str}</code>"

        # Получаем telegram_id автора изменений (если он есть)
        author_telegram_id = None
        if "id" in user and user["id"]:
            user_id = user["id"]
            taiga_user = self.data_storage.get_taiga_user_by_id(user_id)
            if taiga_user and taiga_user.get("telegram_id"):
                author_telegram_id = taiga_user["telegram_id"]
                self.logger.info(f"Author telegram_id: {author_telegram_id}")

        # Send to each scrum master
        for telegram_id in telegram_ids:
            # Не отправляем уведомление автору изменений
            if author_telegram_id and telegram_id == author_telegram_id:
                self.logger.info(f"Skipping notification to author {telegram_id}")
                continue

            try:
                self.bot.send_message(
                    chat_id=telegram_id, text=message, parse_mode="HTML"
                )
                self.logger.info(f"Notification sent to user {telegram_id}")
            except Exception as e:
                self.logger.error(
                    f"Failed to send notification to {telegram_id}: {str(e)}"
                )
