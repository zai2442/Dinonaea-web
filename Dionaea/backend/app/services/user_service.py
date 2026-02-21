from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from fastapi import HTTPException
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserList
from app.core.security import get_password_hash
from app.models.audit import AuditLog
import json

class UserService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        # Check username
        if UserService.get_by_username(db, user_in.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check email (assuming unique email constraint exists or should be checked)
        existing_email = db.scalar(select(User).where(User.email == user_in.email))
        if existing_email:
             raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            status="active", # Default active for now, could be 'pending' if email verification needed
            create_by=None, # Self registration
            update_by=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Audit
        audit = AuditLog(
            user_id=None, # System or Anonymous
            action="REGISTER_USER",
            resource_id=str(user.id),
            params=user_in.model_dump_json(),
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()
        
        return user

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, username: str = None, status: str = None) -> dict:
        query = select(User).where(User.deleted == False)
        if username:
            query = query.where(User.username.ilike(f"%{username}%"))
        if status:
            query = query.where(User.status == status)
            
        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = db.scalar(count_query)
        
        # Items query
        items = db.scalars(query.offset(skip).limit(limit)).all()
        
        return {"total": total, "items": items}

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        return db.get(User, user_id)

    @staticmethod
    def get_by_username(db: Session, username: str) -> User:
        return db.scalar(select(User).where(User.username == username, User.deleted == False))

    @staticmethod
    def create_user(db: Session, user_in: UserCreate, current_user_id: int) -> User:
        if UserService.get_by_username(db, user_in.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            status=user_in.status,
            create_by=current_user_id,
            update_by=current_user_id
        )

        if user_in.role_ids:
            roles = db.scalars(select(Role).where(Role.id.in_(user_in.role_ids))).all()
            user.roles = roles

        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Audit
        audit = AuditLog(
            user_id=current_user_id,
            action="CREATE_USER",
            resource_id=str(user.id),
            params=user_in.model_dump_json(),
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()
        
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate, current_user_id: int) -> User:
        user = db.get(User, user_id)
        if not user or user.deleted:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user_in.version is not None and user.version != user_in.version:
            raise HTTPException(status_code=409, detail="Conflict: Data has been modified by another user")

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        if "role_ids" in update_data:
            role_ids = update_data.pop("role_ids")
            if role_ids is not None:
                roles = db.scalars(select(Role).where(Role.id.in_(role_ids))).all()
                user.roles = roles

        for field, value in update_data.items():
            setattr(user, field, value)
            
        user.update_by = current_user_id
        user.version += 1
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Audit
        audit = AuditLog(
            user_id=current_user_id,
            action="UPDATE_USER",
            resource_id=str(user.id),
            params=json.dumps(update_data),
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()
        
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, current_user_id: int):
        user = db.get(User, user_id)
        if not user or user.deleted:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.deleted = True
        user.update_by = current_user_id
        user.version += 1
        
        db.add(user)
        db.commit()
        
        # Audit
        audit = AuditLog(
            user_id=current_user_id,
            action="DELETE_USER",
            resource_id=str(user.id),
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()
