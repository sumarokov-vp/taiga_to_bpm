# Standard Library
from typing import Dict, Any, Protocol


class IProcessDBNotification(Protocol):
    """Interface for processing database notifications"""

    def process(self, payload: Dict[str, Any]) -> None:
        """Process a notification payload

        Args:
            payload: The notification payload as a dictionary
        """
        ...


class INotificationListener(Protocol):
    """Interface for notification listeners"""

    def start(self) -> None:
        """Start listening for notifications"""
        ...

    def stop(self) -> None:
        """Stop listening for notifications"""
        ...
