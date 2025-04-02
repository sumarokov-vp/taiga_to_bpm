# Standard Library
import logging
from typing import List

# Third Party Stuff
from telebot import TeleBot  # type: ignore

# Local Application
from notification_listener.domain.common.notifications import INotificationSender
from notification_listener.domain.common.interfaces import IUserRepository


class TelegramNotificationSender(INotificationSender):
    """Telegram implementation of notification sender"""

    def __init__(
        self,
        user_repository: IUserRepository,
        bot: TeleBot,
    ) -> None:
        """Initialize sender with user repository and bot instance

        Args:
            user_repository: User repository for fetching recipient data
            bot: Telegram bot instance
        """
        self.logger = logging.getLogger("telegram_sender")
        self.user_repository = user_repository
        self.bot = bot

    def get_recipients(self) -> List[int]:
        """Get telegram_ids of all users with scrum_master role (id=1)

        Returns:
            List of telegram_ids
        """
        users = self.user_repository.get_users_by_role_id(1)  # scrum_master role_id=1
        if not users:
            self.logger.warning("No scrum masters found in database")
            return []

        telegram_ids = [
            user["telegram_id"] for user in users if user.get("telegram_id")
        ]
        return telegram_ids

    def send_message(self, recipient_id: int, message: str) -> None:
        """Send a message to a recipient via Telegram

        Args:
            recipient_id: Telegram user ID
            message: Message to send
        """
        try:
            self.bot.send_message(chat_id=recipient_id, text=message, parse_mode="HTML")
            self.logger.info(f"Notification sent to user {recipient_id}")
        except Exception as e:
            self.logger.error(
                f"Failed to send notification to {recipient_id}: {str(e)}"
            )
