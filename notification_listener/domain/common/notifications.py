# Standard Library
from typing import Protocol, List

# Local Application
from notification_listener.domain.event.models import EventData
from notification_listener.domain.project.models import Project
from notification_listener.domain.task.models import Task
from notification_listener.domain.userstory.models import UserStory
from notification_listener.domain.user.models import TaigaUser


class INotificationFormatter(Protocol):
    """Interface for notification formatting"""
    
    def format_task_notification(self, task: Task, project: Project, event: EventData, user: TaigaUser) -> str:
        """Format notification for task event
        
        Args:
            task: Task data
            project: Project data
            event: Event data
            user: User who triggered the event
            
        Returns:
            Formatted notification message
        """
        ...
    
    def format_userstory_notification(self, userstory: UserStory, project: Project, event: EventData, user: TaigaUser) -> str:
        """Format notification for user story event
        
        Args:
            userstory: User story data
            project: Project data
            event: Event data
            user: User who triggered the event
            
        Returns:
            Formatted notification message
        """
        ...
    
    def format_changes_description(self, event: EventData, user: TaigaUser) -> List[str]:
        """Format description of changes from event data
        
        Args:
            event: Event data
            user: User who triggered the event
            
        Returns:
            List of formatted change descriptions
        """
        ...


class INotificationSender(Protocol):
    """Interface for notification senders"""
    
    def get_recipients(self) -> List[int]:
        """Get recipient IDs for notifications
        
        Returns:
            List of recipient identifiers
        """
        ...
    
    def send_message(self, recipient_id: int, message: str) -> None:
        """Send a message to a recipient
        
        Args:
            recipient_id: Recipient identifier
            message: Message to send
        """
        ...
