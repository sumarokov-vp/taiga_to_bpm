# Standard Library
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class TaigaUser:
    """Taiga user data model"""
    id: int
    username: str
    full_name: Optional[str] = None
    telegram_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaigaUser':
        """Create TaigaUser instance from dictionary"""
        user_id = data.get('id')
        if user_id is None:
            raise ValueError("TaigaUser ID cannot be None")
        
        telegram_id = data.get('telegram_id')
        return cls(
            id=int(user_id),
            username=data.get('username', ''),
            full_name=data.get('full_name'),
            telegram_id=int(telegram_id) if telegram_id is not None else None
        )
    
    def get_display_name(self) -> str:
        """Get the display name to use in notifications"""
        if self.full_name:
            return self.full_name
        elif self.username:
            return self.username
        return f'Пользователь #{self.id}'
