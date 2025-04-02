# Standard Library
import logging
from typing import Dict, Any, Optional

# Local Application
from notification_listener.domain.task.interfaces import ITaskEventHandler
from notification_listener.domain.task.models import Task


class TaskEventService(ITaskEventHandler):
    """Default implementation of task event handler"""
    
    def __init__(self) -> None:
        """Initialize service"""
        self.logger = logging.getLogger("task_event_service")
    
    def handle_task_created(self, task: Task, event_data: Dict[str, Any]) -> None:
        """Handle task created event
        
        Args:
            task: Task data
            event_data: Raw event data
        """
        self.logger.info(f"Task created: #{task.ref} {task.subject}")
        # Implement any business logic for task creation here
    
    def handle_task_changed(self, task: Task, event_data: Dict[str, Any]) -> None:
        """Handle task changed event
        
        Args:
            task: Task data
            event_data: Raw event data
        """
        self.logger.info(f"Task changed: #{task.ref} {task.subject}")
        
        # Extract changes information
        values_diff = event_data.get("values_diff", {})
        
        # Check status changes for specific business logic
        if "status" in values_diff:
            status_change = values_diff["status"]
            if isinstance(status_change, list) and len(status_change) >= 2:
                old_status = status_change[0]
                new_status = status_change[1]
                self.logger.info(f"Task status changed: {old_status} -> {new_status}")
                # Add business logic for status changes here
    
    def handle_task_deleted(self, task_id: int, event_data: Dict[str, Any]) -> None:
        """Handle task deleted event
        
        Args:
            task_id: ID of deleted task
            event_data: Raw event data
        """
        self.logger.info(f"Task deleted: ID {task_id}")
        # Implement any business logic for task deletion here
