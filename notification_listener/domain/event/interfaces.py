# Standard Library
from typing import Dict, Any, Protocol

# Local Application
from notification_listener.domain.event.models import EventData


class IEventFactory(Protocol):
    """Interface for event factory"""
    
    def create_event(self, payload: Dict[str, Any]) -> EventData:
        """Create an event from notification payload
        
        Args:
            payload: Notification payload
            
        Returns:
            EventData instance
        """
        ...


class IEventHandler(Protocol):
    """Interface for event handlers"""
    
    def can_handle(self, event: EventData) -> bool:
        """Check if this handler can process the event
        
        Args:
            event: Event data
            
        Returns:
            True if this handler can process the event
        """
        ...
    
    def handle(self, event: EventData) -> None:
        """Handle an event
        
        Args:
            event: Event data
        """
        ...
