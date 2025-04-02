# Standard Library
import logging
from typing import Dict, Any, List, Optional

# Local Application
from notification_listener.domain.common.notifications import INotificationFormatter
from notification_listener.domain.event.models import EventData
from notification_listener.domain.project.models import Project
from notification_listener.domain.task.models import Task
from notification_listener.domain.userstory.models import UserStory
from notification_listener.domain.user.models import TaigaUser


class TelegramNotificationFormatter(INotificationFormatter):
    """Formatter for Telegram notifications"""

    def __init__(self, base_url: str = "https://taiga.smartist.dev") -> None:
        """Initialize formatter

        Args:
            base_url: Base URL for Taiga instance to generate links
        """
        self.logger = logging.getLogger("telegram_formatter")
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

    def _get_event_description(self, event_type: str) -> str:
        """Get human-readable event description

        Args:
            event_type: Event type identifier

        Returns:
            Translated event description
        """
        return self.event_translations.get(event_type, f"Событие: {event_type}")

    def _generate_url(self, project_slug: str, content_type: str, ref: int) -> str:
        """Generate URL to Taiga object

        Args:
            project_slug: Project slug
            content_type: Content type (us, task, etc.)
            ref: Object reference number

        Returns:
            URL to the object
        """
        if project_slug and ref:
            return f"{self.base_url}/project/{project_slug}/{content_type}/{ref}"
        elif project_slug:
            return f"{self.base_url}/project/{project_slug}"
        return self.base_url

    def format_task_notification(
        self, task: Task, project: Project, event: EventData, user: TaigaUser
    ) -> str:
        """Format notification for task event

        Args:
            task: Task data
            project: Project data
            event: Event data
            user: User who triggered the event

        Returns:
            Formatted notification message
        """
        try:
            # Get event description
            event_type = event.event_type
            event_description = self._get_event_description(event_type)

            # Generate URL
            url = self._generate_url(project.slug, "task", task.ref)

            # Format changes description
            changes_description = self.format_changes_description(event, user)

            # Format message
            message = (
                f"<b>Проект {project.name}</b>\n"
                f"<b>{event_description}</b>\n"
                f"<i>#{task.ref}: {task.subject}</i>\n"
            )

            # Add changes description if available
            if changes_description:
                message += f"\n{chr(10).join(changes_description)}\n"

            # Add link
            message += f"<a href='{url}'>Открыть в Taiga</a>"

            return message
        except Exception as e:
            self.logger.error(f"Error formatting task notification: {str(e)}")
            return f"Событие в Taiga: {event.event_type}"

    def format_userstory_notification(
        self, userstory: UserStory, project: Project, event: EventData, user: TaigaUser
    ) -> str:
        """Format notification for user story event

        Args:
            userstory: User story data
            project: Project data
            event: Event data
            user: User who triggered the event

        Returns:
            Formatted notification message
        """
        try:
            # Get event description
            event_type = event.event_type
            event_description = self._get_event_description(event_type)

            # Generate URL
            url = self._generate_url(project.slug, "us", userstory.ref)

            # Format changes description
            changes_description = self.format_changes_description(event, user)

            # Format message
            message = (
                f"<b>Проект {project.name}</b>\n"
                f"<b>{event_description}</b>\n"
                f"<i>#{userstory.ref}: {userstory.subject}</i>\n"
            )

            # Add changes description if available
            if changes_description:
                message += f"\n{chr(10).join(changes_description)}\n"

            # Add link
            message += f"<a href='{url}'>Открыть в Taiga</a>"

            return message
        except Exception as e:
            self.logger.error(f"Error formatting user story notification: {str(e)}")
            return f"Событие в Taiga: {event.event_type}"

    def format_changes_description(
        self, event: EventData, user: TaigaUser
    ) -> List[str]:
        """Format description of changes from event data

        Args:
            event: Event data
            user: User who triggered the event

        Returns:
            List of formatted change descriptions
        """
        changes_description = []
        timeline_data = event.data

        # Добавляем информацию о пользователе, внесшем изменения
        user_name = user.get_display_name()
        if user_name != "Неизвестный пользователь":
            changes_description.append(f"👤 Изменения внёс: {user_name}")

        # Проверяем наличие комментария
        comment_html = timeline_data.get("comment_html", "")
        if comment_html and comment_html.strip():
            # Удаляем HTML-теги для простого отображения
            comment_text = comment_html.replace("<p>", "").replace("</p>", "")
            comment_text = comment_text.strip()

            # Проверяем, был ли комментарий удален или изменен
            comment_deleted = timeline_data.get("comment_deleted", False)
            comment_edited = timeline_data.get("comment_edited", False)

            if comment_text:
                if comment_deleted:
                    comment_line = f"💬 <b>{user_name}</b> удалил комментарий:"
                elif comment_edited:
                    comment_line = f"💬 <b>{user_name}</b> изменил комментарий:"
                else:
                    comment_line = f"💬 <b>{user_name}</b> прокомментировал:"
                changes_description.append(f"{comment_line} {comment_text}")

        # Проверяем наличие изменений в values_diff
        values_diff = timeline_data.get("values_diff", {})
        if values_diff:
            # Изменение статуса
            if "status" in values_diff:
                status_change = values_diff["status"]
                if isinstance(status_change, list) and len(status_change) >= 2:
                    old_status = status_change[0] or "--"
                    new_status = status_change[1] or "--"
                    changes_description.append(
                        f"🔄 Статус: {old_status} → {new_status}"
                    )

            # Изменение спринта
            if "milestone" in values_diff:
                milestone_change = values_diff["milestone"]
                if isinstance(milestone_change, list) and len(milestone_change) >= 2:
                    old_milestone = milestone_change[0] or "Не в спринте"
                    new_milestone = milestone_change[1] or "Не в спринте"

                    # Если old_milestone или new_milestone - объекты, извлекаем имя
                    if isinstance(old_milestone, dict) and "name" in old_milestone:
                        old_milestone = old_milestone["name"]
                    if isinstance(new_milestone, dict) and "name" in new_milestone:
                        new_milestone = new_milestone["name"]

                    changes_description.append(
                        f"📅 Спринт: {old_milestone} → {new_milestone}"
                    )

            # Изменение исполнителя
            if "assigned_to" in values_diff:
                assigned_change = values_diff["assigned_to"]
                if isinstance(assigned_change, list) and len(assigned_change) >= 2:
                    old_assigned_name = "Не назначен"
                    new_assigned_name = "Не назначен"

                    # Извлекаем имена, если объекты
                    if assigned_change[0]:
                        if (
                            isinstance(assigned_change[0], dict)
                            and "name" in assigned_change[0]
                        ):
                            old_assigned_name = assigned_change[0]["name"]

                    if assigned_change[1]:
                        if (
                            isinstance(assigned_change[1], dict)
                            and "name" in assigned_change[1]
                        ):
                            new_assigned_name = assigned_change[1]["name"]

                    changes_description.append(
                        f"👤 Исполнитель: {old_assigned_name} → {new_assigned_name}"
                    )

            # Изменения в описании
            desc_in_values = "description_diff" in values_diff
            desc_in_timeline = "description_diff" in timeline_data

            if desc_in_values or desc_in_timeline:
                # Получаем данные об изменении описания
                if desc_in_values:
                    description_diff = values_diff.get("description_diff")
                else:
                    description_diff = timeline_data.get("description_diff")

                if description_diff:
                    desc_line = f"📝 <b>{user_name}</b> изменил описание:"
                    changes_description.append(f"{desc_line} {description_diff}")

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
                            old_val = "-" if value_diff[0] is None else value_diff[0]
                            new_val = "-" if value_diff[1] is None else value_diff[1]
                            changes_description.append(
                                f"📝 {attr_name}: {old_val} → {new_val}"
                            )
                        else:
                            # Если есть только новое значение
                            changes_description.append(f"📝 {attr_name}: {attr_value}")

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

        return changes_description
