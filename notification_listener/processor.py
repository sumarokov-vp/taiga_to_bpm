# Standard Library
import logging
from typing import Dict, Any

# Local Application
from notification_listener.interfaces import IProcessDBNotification
from notification_listener.application.notification_sender import (
    NotificationSenderFactory,
    create_legacy_sender,
)


class Processor(IProcessDBNotification):
    """Processes database notifications"""

    def __init__(
        self, data_storage, bot, base_url: str = "https://taiga.smartist.dev"
    ) -> None:
        """Initialize processor with data storage and bot

        Args:
            data_storage: Data storage for database access
            bot: Telegram bot instance
            base_url: Base URL for Taiga instance
        """
        self.logger = logging.getLogger("processor")
        self.data_storage = data_storage

        # Create modern event processor
        self.event_processor = NotificationSenderFactory.create_processor(
            data_storage, bot, base_url
        )

        # For backward compatibility
        self.legacy_sender = create_legacy_sender(data_storage, bot, base_url)

    def process(self, payload: Dict[str, Any]) -> None:
        """Process a notification payload

        Args:
            payload: The notification payload as a dictionary
        """
        self.logger.info("Processing notification payload")
        try:
            # Process event using new architecture
            self.event_processor.process(payload)

            # For backward compatibility, also send directly through legacy sender
            # This can be removed when the transition is complete
            # self.legacy_sender.send_notification(payload)
        except Exception as e:
            self.logger.exception(f"Error processing notification: {str(e)}")
