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
            description=role_in.description,
            status=role_in.status
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
        
        # Check uniqueness if name is being updated
        if role_in.name and role_in.name != role.name:
            existing_role = db.scalar(select(Role).where(Role.name == role_in.name))
            if existing_role:
                 raise HTTPException(status_code=400, detail="Role with this name already exists")
            role.name = role_in.name

        if role_in.description is not None:
            role.description = role_in.description
            
        if role_in.status:
            role.status = role_in.status
            
        if role_in.permission_ids is not None:
            permissions = db.scalars(select(Permission).where(Permission.id.in_(role_in.permission_ids))).all()
            role.permissions = permissions
            
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_role(db: Session, role_id: int) -> Role:
        role = db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
        return db.scalars(select(Role).offset(skip).limit(limit)).unique().all()

    @staticmethod
    def delete_role(db: Session, role_id: int):
        role = db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Protect super_admin and user roles (basic roles)
        if role.code in ['super_admin', 'user', 'admin']:
             raise HTTPException(status_code=403, detail="Cannot delete system roles")
             
        db.delete(role)
        db.commit()
