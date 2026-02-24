from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Permission
from app.schemas.permission import PermissionCreate
import json
from app.core.config import settings
import redis

# Redis connection
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)
CACHE_KEY_PERMISSIONS = "dionaea:permissions:list"

class PermissionService:
    @staticmethod
    def create_permission(db: Session, permission_in: PermissionCreate) -> Permission:
        existing = db.scalar(select(Permission).where(Permission.code == permission_in.code))
        if existing:
            return existing
            
        permission = Permission(
            name=permission_in.name,
            code=permission_in.code,
            description=permission_in.description,
            resource_type=permission_in.resource_type
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        # Invalidate cache
        redis_client.delete(CACHE_KEY_PERMISSIONS)
        
        return permission

    @staticmethod
    def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> list[Permission]:
        # Try cache first (only for full list/default pagination)
        if skip == 0 and limit >= 100:
            cached = redis_client.get(CACHE_KEY_PERMISSIONS)
            if cached:
                # Need to deserialize and convert back to objects/dicts
                # This is a simplification. Ideally we cache the Pydantic models dump.
                # For now, let's just return DB query to be safe with object types
                # or implement proper caching strategy.
                pass 

        permissions = db.scalars(select(Permission).offset(skip).limit(limit)).all()
        return permissions
