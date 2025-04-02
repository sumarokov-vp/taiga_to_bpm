# Standard Library
from typing import List

# Local Application
from notification_listener.domain.event.models import EventData
from notification_listener.domain.event.interfaces import IEventHandler


class ProcessEventUseCase:
    """Use case for processing events"""
    
    def __init__(self, handlers: List[IEventHandler]) -> None:
        """Initialize use case with event handlers
        
        Args:
            handlers: List of event handlers
        """
        self.handlers = handlers
    
    def execute(self, event: EventData) -> None:
        """Process an event with appropriate handlers
        
        Args:
            event: Event data to process
        """
        for handler in self.handlers:
            if handler.can_handle(event):
                handler.handle(event)
