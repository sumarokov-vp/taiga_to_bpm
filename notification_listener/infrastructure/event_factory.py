# Standard Library
import logging
from typing import Dict, Any

# Local Application
from notification_listener.domain.event.models import EventData
from notification_listener.domain.event.interfaces import IEventFactory


class EventFactory(IEventFactory):
    """Factory for creating event objects from notification payloads"""
    
    def __init__(self) -> None:
        """Initialize event factory"""
        self.logger = logging.getLogger("event_factory")
    
    def create_event(self, payload: Dict[str, Any]) -> EventData:
        """Create an event from notification payload
        
        Args:
            payload: Notification payload
            
        Returns:
            EventData instance
        """
        try:
            return EventData.from_dict(payload)
        except Exception as e:
            self.logger.error(f"Error creating event from payload: {str(e)}")
            # Create a minimal event with default values
            return EventData(
                event_type="unknown",
                data={}
            )
