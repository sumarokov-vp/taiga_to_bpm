# Standard Library

# Third Party Stuff
from telebot import TeleBot  # type: ignore

# Local Application
from notification_listener.infrastructure.repositories.user_repository import (
    UserRepository,
)
from notification_listener.infrastructure.telegram.notification_sender import (
    TelegramNotificationSender,
)
from notification_listener.infrastructure.telegram.notification_formatter import (
    TelegramNotificationFormatter,
)
from notification_listener.infrastructure.handlers.task_service import TaskEventService
from notification_listener.infrastructure.handlers.userstory_service import (
    UserStoryEventService,
)
from notification_listener.infrastructure.handlers.task_handler import TaskEventHandler
from notification_listener.infrastructure.handlers.userstory_handler import (
    UserStoryEventHandler,
)
from notification_listener.infrastructure.event_factory import EventFactory
from notification_listener.domain.task.usecases import NotifyTaskChangeUseCase
from notification_listener.domain.userstory.usecases import NotifyUserStoryChangeUseCase
from notification_listener.application.event_processor import EventProcessor


class NotificationSenderFactory:
    """Factory for creating notification sender infrastructure"""

    @staticmethod
    def create_processor(
        data_storage, bot: TeleBot, base_url: str = "https://taiga.smartist.dev"
    ):
        """Create event processor with all required dependencies

        Args:
            data_storage: Data storage for database access
            bot: Telegram bot instance
            base_url: Base URL for Taiga instance

        Returns:
            Configured EventProcessor instance
        """
        # Create repositories
        user_repository = UserRepository(data_storage)

        # Create formatter
        formatter = TelegramNotificationFormatter(base_url)

        # Create notification sender
        notification_sender = TelegramNotificationSender(user_repository, bot)

        # Create use cases
        task_notification_usecase = NotifyTaskChangeUseCase(
            formatter, notification_sender
        )
        userstory_notification_usecase = NotifyUserStoryChangeUseCase(
            formatter, notification_sender
        )

        # Create domain services
        task_service = TaskEventService()
        userstory_service = UserStoryEventService()

        # Create event handlers
        task_handler = TaskEventHandler(
            task_service, user_repository, task_notification_usecase
        )
        userstory_handler = UserStoryEventHandler(
            userstory_service, user_repository, userstory_notification_usecase
        )

        # Create event factory
        event_factory = EventFactory()

        # Create event processor with all handlers
        return EventProcessor(event_factory, [task_handler, userstory_handler])


# For backwards compatibility - to be used in processor.py
def create_legacy_sender(
    data_storage, bot: TeleBot, base_url: str = "https://taiga.smartist.dev"
):
    """Create legacy notification sender for backward compatibility

    Args:
        data_storage: Data storage
        bot: Telegram bot instance
        base_url: Base URL for Taiga instance

    Returns:
        TelegramNotificationSender instance
    """
    return TelegramNotificationSender(UserRepository(data_storage), bot)
