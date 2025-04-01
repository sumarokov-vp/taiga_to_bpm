# Standard Library
import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

# My Stuff
# Local Application
from notification_listener.interfaces import (
    IProcessDBNotification,
    INotificationSender,
)


class DefaultNotificationProcessor(IProcessDBNotification):
    """Default implementation of notification processor"""

    def __init__(self, senders: Optional[List[INotificationSender]] = None) -> None:
        """Initialize processor with notification senders

        Args:
            senders: List of notification senders to use (optional)
        """
        self.logger = logging.getLogger("notification_processor")
        self.senders: List[INotificationSender] = senders or []

    def process(self, payload: Dict[str, Any]) -> None:
        """Process a notification payload

        Args:
            payload: The notification payload as a dictionary
        """
        self.logger.info(f"Processing notification: {payload}")

        # Distribute notification to all registered senders
        for sender in self.senders:
            try:
                sender.send_notification(payload)
            except Exception as e:
                self.logger.error(f"Error sending notification: {str(e)}")

        # Additional processing logic can be added here
        # - Update a cache
        # - Call a webhook
        # - Send to message queue
        # - Update application state
