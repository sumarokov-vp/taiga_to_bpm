# Standard Library
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Project:
    """Project data model"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project instance from dictionary"""
        project_id = data.get('id')
        if project_id is None:
            raise ValueError("Project ID cannot be None")
        return cls(
            id=int(project_id),
            name=data.get('name', 'Проект'),
            slug=data.get('slug', ''),
            description=data.get('description')
        )
