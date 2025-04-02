# Standard Library
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class EventData:
    """Event data model"""
    event_type: str
    data: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> 'EventData':
        """Create EventData instance from payload dictionary"""
        event_type = payload.get('event_type', 'unknown')
        
        # Extract data from payload
        data = {}
        if 'data' in payload and payload['data']:
            if isinstance(payload['data'], str):
                import json
                try:
                    data = json.loads(payload['data'])
                except json.JSONDecodeError:
                    data = {}
            else:
                data = payload['data']
                
        return cls(
            event_type=event_type,
            data=data
        )
