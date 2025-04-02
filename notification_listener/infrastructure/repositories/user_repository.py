# Standard Library
import logging
from typing import Dict, Any, List, Optional

# Local Application
from notification_listener.domain.user.models import TaigaUser
from notification_listener.domain.common.interfaces import IUserRepository


class UserRepository(IUserRepository):
    """Repository for user data"""
    
    def __init__(self, data_storage) -> None:
        """Initialize repository with data storage
        
        Args:
            data_storage: Data storage implementation for database access
        """
        self.logger = logging.getLogger("user_repository")
        self.data_storage = data_storage
    
    def get_users_by_role_id(self, role_id: int) -> List[Dict[str, Any]]:
        """Get users with specific role
        
        Args:
            role_id: Role identifier
            
        Returns:
            List of user records
        """
        users = self.data_storage.get_users_by_role_id(role_id)
        if not users:
            self.logger.warning(f"No users found with role_id={role_id}")
            return []
        return users
    
    def get_taiga_user_by_id(self, user_id: int) -> Optional[TaigaUser]:
        """Get Taiga user by their id
        
        Args:
            user_id: Taiga user identifier
            
        Returns:
            TaigaUser instance or None if not found
        """
        try:
            # First try direct query to users_user table
            direct_query = """
            SELECT id, username, full_name, username as name
            FROM users_user
            WHERE id = %(user_id)s
            """
            args = {"user_id": user_id}
            self.logger.debug(f"Trying direct query for user_id={user_id}")
            direct_user = self.data_storage.get_one(direct_query, args)
            
            if direct_user:
                # Create TaigaUser from direct query result
                user = TaigaUser(
                    id=direct_user.get('id'),
                    username=direct_user.get('username', ''),
                    full_name=direct_user.get('full_name')
                )
                
                # Now try to get telegram_id from bot_users
                taiga_user = self.data_storage.get_taiga_user_by_id(user_id)
                if taiga_user and taiga_user.get("telegram_id"):
                    user.telegram_id = taiga_user.get("telegram_id")
                
                return user
            else:
                # Fallback to get_taiga_user_by_id
                taiga_user = self.data_storage.get_taiga_user_by_id(user_id)
                if taiga_user:
                    return TaigaUser.from_dict(taiga_user)
                
                self.logger.warning(f"User with id {user_id} not found in database")
                return None
        except Exception as e:
            self.logger.error(f"Error getting user with id {user_id}: {str(e)}")
            return None
