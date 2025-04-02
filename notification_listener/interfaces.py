# Standard Library
from typing import Dict, Any, Protocol, List


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


class INotificationSender(Protocol):
    """Interface for notification senders"""

    def send_notification(self, payload: Dict[str, Any]) -> None:
        """Send notification to recipients

        Args:
            payload: The notification payload as a dictionary
        """
        ...


class IDataStorage(Protocol):
    """Interface for data storage access"""

    def get_users_by_role_id(self, role_id: int) -> List[Dict[str, Any]]:
        """Get users with specific role

        Args:
            role_id: Role identifier

        Returns:
            List of user records
        """
        ...

    def get_taiga_user_by_id(self, user_id: int) -> Dict[str, Any] | None:
        """Get Taiga user by their id

        Args:
            user_id: Taiga user identifier

        Returns:
            User record or None if not found
        """
        ...

    def execute_query(self, query: str, args: Dict[str, Any] = None) -> None:
        """Execute a query without returning results

        Args:
            query: SQL query to execute
            args: Query parameters
        """
        ...

    def get_one(self, query: str, args: Dict[str, Any] = None) -> Dict[str, Any] | None:
        """Get a single record from database

        Args:
            query: SQL query to execute
            args: Query parameters

        Returns:
            Single record or None if not found
        """
        ...

    def get_all(self, query: str, args: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get multiple records from database

        Args:
            query: SQL query to execute
            args: Query parameters

        Returns:
            List of records
        """
        ...
