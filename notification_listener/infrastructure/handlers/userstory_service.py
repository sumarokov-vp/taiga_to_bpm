# Standard Library
import logging
from typing import Dict, Any

# Local Application
from notification_listener.domain.userstory.interfaces import IUserStoryEventHandler
from notification_listener.domain.userstory.models import UserStory


class UserStoryEventService(IUserStoryEventHandler):
    """Default implementation of user story event handler"""
    
    def __init__(self) -> None:
        """Initialize service"""
        self.logger = logging.getLogger("userstory_event_service")
    
    def handle_userstory_created(self, userstory: UserStory, event_data: Dict[str, Any]) -> None:
        """Handle user story created event
        
        Args:
            userstory: User story data
            event_data: Raw event data
        """
        self.logger.info(f"User story created: #{userstory.ref} {userstory.subject}")
        # Implement any business logic for user story creation here
    
    def handle_userstory_changed(self, userstory: UserStory, event_data: Dict[str, Any]) -> None:
        """Handle user story changed event
        
        Args:
            userstory: User story data
            event_data: Raw event data
        """
        self.logger.info(f"User story changed: #{userstory.ref} {userstory.subject}")
        
        # Extract changes information
        values_diff = event_data.get("values_diff", {})
        
        # Check status changes for specific business logic
        if "status" in values_diff:
            status_change = values_diff["status"]
            if isinstance(status_change, list) and len(status_change) >= 2:
                old_status = status_change[0]
                new_status = status_change[1]
                self.logger.info(f"User story status changed: {old_status} -> {new_status}")
                # Add business logic for status changes here
    
    def handle_userstory_deleted(self, userstory_id: int, event_data: Dict[str, Any]) -> None:
        """Handle user story deleted event
        
        Args:
            userstory_id: ID of deleted user story
            event_data: Raw event data
        """
        self.logger.info(f"User story deleted: ID {userstory_id}")
        # Implement any business logic for user story deletion here
