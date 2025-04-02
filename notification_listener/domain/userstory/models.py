# Standard Library
from dataclasses import dataclass
from typing import Dict, Any, Optional

# Local Application
from notification_listener.domain.common.models import User


@dataclass
class UserStory:
    """User Story data model"""
    id: int
    ref: int
    subject: str
    status: Optional[str] = None
    project_id: Optional[int] = None
    assigned_to: Optional[User] = None
    owner: Optional[User] = None
    description: Optional[str] = None
    milestone: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStory':
        """Create UserStory instance from dictionary"""
        assigned_to = None
        if data.get('assigned_to'):
            if isinstance(data['assigned_to'], dict):
                assigned_to = User.from_dict(data['assigned_to'])
        
        owner = None
        if data.get('owner'):
            if isinstance(data['owner'], dict):
                owner = User.from_dict(data['owner'])
        
        milestone = None
        if data.get('milestone'):
            if isinstance(data['milestone'], dict) and 'name' in data['milestone']:
                milestone = data['milestone']['name']
            else:
                milestone = str(data['milestone'])
        
        userstory_id = data.get('id')
        userstory_ref = data.get('ref')
        
        if userstory_id is None:
            raise ValueError("UserStory ID cannot be None")
        
        if userstory_ref is None:
            raise ValueError("UserStory reference number cannot be None")
        
        # Получение project_id из вложенного словаря или напрямую
        project_id = None
        if isinstance(data.get('project'), dict) and data.get('project', {}).get('id') is not None:
            project_id = int(data.get('project', {}).get('id'))
        elif data.get('project_id') is not None:
            project_id_value = data.get('project_id')
            if project_id_value is not None:  # дополнительная проверка для mypy
                project_id = int(project_id_value)
        
        return cls(
            id=int(userstory_id),
            ref=int(userstory_ref),
            subject=data.get('subject', 'Без названия'),
            status=data.get('status'),
            project_id=project_id,
            assigned_to=assigned_to,
            owner=owner,
            description=data.get('description'),
            milestone=milestone
        )
