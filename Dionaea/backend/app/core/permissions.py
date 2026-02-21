from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.dependencies import get_current_active_user
from sqlalchemy.orm import Session
from app.db.database import get_db

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
        # Check if user is super admin (bypass)
        # Assuming 'admin' role has all permissions or check specific role code
        for role in current_user.roles:
            if role.code == "super_admin":
                return True
            
            # Check permissions
            for permission in role.permissions:
                if permission.code == self.required_permission:
                    return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Required: {self.required_permission}"
        )
