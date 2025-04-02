# Standard Library
import logging

# Local Application
from notification_listener.domain.event.models import EventData
from notification_listener.domain.event.interfaces import IEventHandler
from notification_listener.domain.task.interfaces import ITaskEventHandler
from notification_listener.domain.task.models import Task
from notification_listener.domain.project.models import Project
from notification_listener.domain.task.usecases import NotifyTaskChangeUseCase
from notification_listener.domain.common.interfaces import IUserRepository


class TaskEventHandler(IEventHandler):
    """Handler for task-related events"""
    
    def __init__(
        self,
        task_handler: ITaskEventHandler,
        user_repository: IUserRepository,
        notification_usecase: NotifyTaskChangeUseCase,
    ) -> None:
        """Initialize handler
        
        Args:
            task_handler: Task event handler
            user_repository: User repository
            notification_usecase: Notification use case
        """
        self.logger = logging.getLogger("task_event_handler")
        self.task_handler = task_handler
        self.user_repository = user_repository
        self.notification_usecase = notification_usecase
    
    def can_handle(self, event: EventData) -> bool:
        """Check if this handler can process the event
        
        Args:
            event: Event data
            
        Returns:
            True if this handler can process the event
        """
        return event.event_type.startswith("tasks.task.")
    
    def handle(self, event: EventData) -> None:
        """Handle task event
        
        Args:
            event: Event data
        """
        try:
            event_type = event.event_type
            timeline_data = event.data
            
            # Extract task data
            task_data = timeline_data.get("task", {})
            if not task_data:
                self.logger.warning("No task data found in event")
                return
            
            # Extract project data
            project_data = timeline_data.get("project", {})
            if not project_data:
                self.logger.warning("No project data found in event")
                return
            
            # Extract user data
            user_data = timeline_data.get("user", {})
            if not user_data:
                self.logger.warning("No user data found in event")
                return
            
            # Convert to domain models
            task = Task.from_dict(task_data)
            project = Project.from_dict(project_data)
            
            # Get user from repository
            user_id = user_data.get("id")
            if not user_id:
                self.logger.warning("No user ID found in event")
                return
                
            user = self.user_repository.get_taiga_user_by_id(user_id)
            if not user:
                self.logger.warning(f"User with ID {user_id} not found")
                return
            
            # Process based on event type
            if event_type == "tasks.task.create":
                self.task_handler.handle_task_created(task, timeline_data)
            elif event_type == "tasks.task.change":
                self.task_handler.handle_task_changed(task, timeline_data)
            elif event_type == "tasks.task.delete":
                self.task_handler.handle_task_deleted(task.id, timeline_data)
            
            # Send notification
            self.notification_usecase.execute(task, project, event, user)
        except Exception as e:
            self.logger.error(f"Error handling task event: {str(e)}")
