# Standard Library
import logging
from typing import (
    Any,
    Dict,
)

# My Stuff
# Local Application
from notification_listener.interfaces import (
    IProcessDBNotification,
)


class DefaultNotificationProcessor(IProcessDBNotification):
    """Default implementation of notification processor"""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize processor with logger

        Args:
            logger: Logger instance for recording processing activity
        """
        self.logger = logger

    def process(self, payload: Dict[str, Any]) -> None:
        """Process a notification payload

        Args:
            payload: The notification payload as a dictionary
        """
        self.logger.info(f"Processing notification: {payload}")
        # Add your specific processing logic here
        # For example:
        # - Update a cache
        # - Call a webhook
        # - Send to message queue
        # - Update application state
