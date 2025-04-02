# Standard Library
from typing import Dict, Any, Protocol, Optional

# Local Application
from notification_listener.domain.userstory.models import UserStory


class IUserStoryRepository(Protocol):
    """Interface for user story repository"""
    
    def get_userstory_by_id(self, userstory_id: int) -> Optional[UserStory]:
        """Get user story by its ID
        
        Args:
            userstory_id: User story identifier
            
        Returns:
            UserStory instance or None if not found
        """
        ...


class IUserStoryEventHandler(Protocol):
    """Interface for user story event handler"""
    
    def handle_userstory_created(self, userstory: UserStory, event_data: Dict[str, Any]) -> None:
        """Handle user story created event
        
        Args:
            userstory: User story data
            event_data: Raw event data
        """
        ...
    
    def handle_userstory_changed(self, userstory: UserStory, event_data: Dict[str, Any]) -> None:
        """Handle user story changed event
        
        Args:
            userstory: User story data
            event_data: Raw event data
        """
        ...
    
    def handle_userstory_deleted(self, userstory_id: int, event_data: Dict[str, Any]) -> None:
        """Handle user story deleted event
        
        Args:
            userstory_id: ID of deleted user story
            event_data: Raw event data
        """
        ...
