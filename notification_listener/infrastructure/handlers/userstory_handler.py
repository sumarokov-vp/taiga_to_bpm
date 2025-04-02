# Standard Library
import logging

# Local Application
from notification_listener.domain.event.models import EventData
from notification_listener.domain.event.interfaces import IEventHandler
from notification_listener.domain.userstory.interfaces import IUserStoryEventHandler
from notification_listener.domain.userstory.models import UserStory
from notification_listener.domain.project.models import Project
from notification_listener.domain.userstory.usecases import NotifyUserStoryChangeUseCase
from notification_listener.domain.common.interfaces import IUserRepository


class UserStoryEventHandler(IEventHandler):
    """Handler for user story-related events"""
    
    def __init__(
        self,
        userstory_handler: IUserStoryEventHandler,
        user_repository: IUserRepository,
        notification_usecase: NotifyUserStoryChangeUseCase,
    ) -> None:
        """Initialize handler
        
        Args:
            userstory_handler: User story event handler
            user_repository: User repository
            notification_usecase: Notification use case
        """
        self.logger = logging.getLogger("userstory_event_handler")
        self.userstory_handler = userstory_handler
        self.user_repository = user_repository
        self.notification_usecase = notification_usecase
    
    def can_handle(self, event: EventData) -> bool:
        """Check if this handler can process the event
        
        Args:
            event: Event data
            
        Returns:
            True if this handler can process the event
        """
        return event.event_type.startswith("userstories.userstory.")
    
    def handle(self, event: EventData) -> None:
        """Handle user story event
        
        Args:
            event: Event data
        """
        try:
            event_type = event.event_type
            timeline_data = event.data
            
            # Extract user story data
            userstory_data = timeline_data.get("userstory", {})
            if not userstory_data:
                self.logger.warning("No user story data found in event")
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
            userstory = UserStory.from_dict(userstory_data)
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
            if event_type == "userstories.userstory.create":
                self.userstory_handler.handle_userstory_created(userstory, timeline_data)
            elif event_type == "userstories.userstory.change":
                self.userstory_handler.handle_userstory_changed(userstory, timeline_data)
            elif event_type == "userstories.userstory.delete":
                self.userstory_handler.handle_userstory_deleted(userstory.id, timeline_data)
            
            # Send notification
            self.notification_usecase.execute(userstory, project, event, user)
        except Exception as e:
            self.logger.error(f"Error handling user story event: {str(e)}")
