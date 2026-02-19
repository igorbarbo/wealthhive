"""
User domain entity
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """User entity"""
    email: str
    full_name: str
    hashed_password: str
    id: UUID = field(default_factory=uuid4)
    role: str = "user"  # user, admin
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def change_role(self, new_role: str) -> None:
        """Change user role"""
        self.role = new_role
        self.updated_at = datetime.utcnow()
    
    def verify(self) -> None:
        """Mark email as verified"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()
      
