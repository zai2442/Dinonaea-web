from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Permission
from app.schemas.permission import PermissionCreate

class PermissionService:
    @staticmethod
    def create_permission(db: Session, permission_in: PermissionCreate) -> Permission:
        existing = db.scalar(select(Permission).where(Permission.code == permission_in.code))
        if existing:
            return existing
            
        permission = Permission(
            code=permission_in.code,
            description=permission_in.description,
            resource_type=permission_in.resource_type
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> list[Permission]:
        return db.scalars(select(Permission).offset(skip).limit(limit)).all()
