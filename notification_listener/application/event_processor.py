# Standard Library
import logging
from typing import Dict, Any, List

# Local Application
from notification_listener.domain.event.interfaces import IEventHandler, IEventFactory
from notification_listener.domain.event.usecases import ProcessEventUseCase


class EventProcessor:
    """Application service for processing events"""
    
    def __init__(
        self,
        event_factory: IEventFactory,
        event_handlers: List[IEventHandler]
    ) -> None:
        """Initialize event processor
        
        Args:
            event_factory: Factory for creating events
            event_handlers: List of event handlers
        """
        self.logger = logging.getLogger("event_processor")
        self.event_factory = event_factory
        self.process_event_usecase = ProcessEventUseCase(event_handlers)
    
    def process(self, payload: Dict[str, Any]) -> None:
        """Process a notification payload
        
        Args:
            payload: Notification payload as dictionary
        """
        try:
            # Create event from payload
            event = self.event_factory.create_event(payload)
            
            # Log event processing
            self.logger.info(f"Processing event: {event.event_type}")
            
            # Process event with appropriate handlers
            self.process_event_usecase.execute(event)
        except Exception as e:
            self.logger.error(f"Error processing event: {str(e)}")
