from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.role import Role, Permission
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    @staticmethod
    def create_role(db: Session, role_in: RoleCreate) -> Role:
        existing_role = db.scalar(select(Role).where((Role.code == role_in.code) | (Role.name == role_in.name)))
        if existing_role:
            raise HTTPException(status_code=400, detail="Role with this code or name already exists")
        
        role = Role(
            name=role_in.name,
            code=role_in.code,
            description=role_in.description
        )
        
        if role_in.permission_ids:
            permissions = db.scalars(select(Permission).where(Permission.id.in_(role_in.permission_ids))).all()
            role.permissions = permissions
            
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def update_role(db: Session, role_id: int, role_in: RoleUpdate) -> Role:
        role = db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
            
        if role_in.name:
            role.name = role_in.name
        if role_in.description:
            role.description = role_in.description
            
        if role_in.permission_ids is not None:
            permissions = db.scalars(select(Permission).where(Permission.id.in_(role_in.permission_ids))).all()
            role.permissions = permissions
            
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role(db: Session, role_id: int) -> Role:
        return db.get(Role, role_id)

    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
        return db.scalars(select(Role).offset(skip).limit(limit)).all()

    @staticmethod
    def delete_role(db: Session, role_id: int):
        role = db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        db.delete(role)
        db.commit()
