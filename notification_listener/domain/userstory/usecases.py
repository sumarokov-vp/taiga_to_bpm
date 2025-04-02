# Standard Library
from typing import Dict, Any, Optional

# Local Application
from notification_listener.domain.userstory.models import UserStory
from notification_listener.domain.project.models import Project
from notification_listener.domain.user.models import TaigaUser
from notification_listener.domain.event.models import EventData
from notification_listener.domain.common.notifications import INotificationFormatter, INotificationSender


class NotifyUserStoryChangeUseCase:
    """Use case for notifying about user story changes"""
    
    def __init__(
        self, 
        formatter: INotificationFormatter,
        sender: INotificationSender
    ) -> None:
        """Initialize use case
        
        Args:
            formatter: Notification formatter
            sender: Notification sender
        """
        self.formatter = formatter
        self.sender = sender
    
    def execute(
        self, 
        userstory: UserStory, 
        project: Project, 
        event: EventData, 
        user: TaigaUser,
        skip_author: bool = True
    ) -> None:
        """Execute notification use case
        
        Args:
            userstory: User story data
            project: Project data
            event: Event data
            user: User who triggered the event
            skip_author: Whether to skip sending notification to the author
        """
        # Format the notification message
        message = self.formatter.format_userstory_notification(userstory, project, event, user)
        
        # Get recipients
        recipients = self.sender.get_recipients()
        
        # Skip author if needed
        author_telegram_id = getattr(user, 'telegram_id', None)
        
        # Send to each recipient
        for recipient_id in recipients:
            if skip_author and author_telegram_id and recipient_id == author_telegram_id:
                continue
            
            self.sender.send_message(recipient_id, message)
