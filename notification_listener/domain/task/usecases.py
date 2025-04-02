# Standard Library

# Local Application
from notification_listener.domain.task.models import Task
from notification_listener.domain.project.models import Project
from notification_listener.domain.user.models import TaigaUser
from notification_listener.domain.event.models import EventData
from notification_listener.domain.common.notifications import INotificationFormatter, INotificationSender


class NotifyTaskChangeUseCase:
    """Use case for notifying about task changes"""
    
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
        task: Task, 
        project: Project, 
        event: EventData, 
        user: TaigaUser,
        skip_author: bool = True
    ) -> None:
        """Execute notification use case
        
        Args:
            task: Task data
            project: Project data
            event: Event data
            user: User who triggered the event
            skip_author: Whether to skip sending notification to the author
        """
        # Format the notification message
        message = self.formatter.format_task_notification(task, project, event, user)
        
        # Get recipients
        recipients = self.sender.get_recipients()
        
        # Skip author if needed
        author_telegram_id = getattr(user, 'telegram_id', None)
        
        # Send to each recipient
        for recipient_id in recipients:
            if skip_author and author_telegram_id and recipient_id == author_telegram_id:
                continue
            
            self.sender.send_message(recipient_id, message)
