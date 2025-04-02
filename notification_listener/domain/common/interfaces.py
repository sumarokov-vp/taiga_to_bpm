# Standard Library
from typing import Dict, Any, Protocol, List, Optional

# Local Application
from notification_listener.domain.user.models import TaigaUser


class IUserRepository(Protocol):
    """Interface for user data repository"""
    
    def get_users_by_role_id(self, role_id: int) -> List[Dict[str, Any]]:
        """Get users with specific role
        
        Args:
            role_id: Role identifier
            
        Returns:
            List of user records
        """
        ...
    
    def get_taiga_user_by_id(self, user_id: int) -> Optional[TaigaUser]:
        """Get Taiga user by their id
        
        Args:
            user_id: Taiga user identifier
            
        Returns:
            TaigaUser instance or None if not found
        """
        ...
