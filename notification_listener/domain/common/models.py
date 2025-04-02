# Standard Library
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class User:
    """User data model"""
    id: int
    username: str
    full_name: Optional[str] = None
    telegram_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        user_id = data.get('id')
        if user_id is None:
            raise ValueError("User ID cannot be None")
        return cls(
            id=int(user_id),
            username=data.get('username', ''),
            full_name=data.get('full_name'),
            telegram_id=data.get('telegram_id')
        )
