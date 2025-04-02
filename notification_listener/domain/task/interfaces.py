# Standard Library
from typing import Dict, Any, Protocol, Optional

# Local Application
from notification_listener.domain.task.models import Task


class ITaskRepository(Protocol):
    """Interface for task repository"""
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by its ID
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task instance or None if not found
        """
        ...


class ITaskEventHandler(Protocol):
    """Interface for task event handler"""
    
    def handle_task_created(self, task: Task, event_data: Dict[str, Any]) -> None:
        """Handle task created event
        
        Args:
            task: Task data
            event_data: Raw event data
        """
        ...
    
    def handle_task_changed(self, task: Task, event_data: Dict[str, Any]) -> None:
        """Handle task changed event
        
        Args:
            task: Task data
            event_data: Raw event data
        """
        ...
    
    def handle_task_deleted(self, task_id: int, event_data: Dict[str, Any]) -> None:
        """Handle task deleted event
        
        Args:
            task_id: ID of deleted task
            event_data: Raw event data
        """
        ...
