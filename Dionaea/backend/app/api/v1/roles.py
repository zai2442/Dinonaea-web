from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.permission import PermissionResponse, PermissionCreate
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.core.permissions import PermissionChecker

router = APIRouter()

@router.get("/", response_model=List[RoleResponse], dependencies=[Depends(PermissionChecker("role:list"))])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RoleService.get_roles(db, skip=skip, limit=limit)

@router.post("/", response_model=RoleResponse, dependencies=[Depends(PermissionChecker("role:create"))])
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RoleService.create_role(db, role)

@router.get("/{role_id}", response_model=RoleResponse, dependencies=[Depends(PermissionChecker("role:read"))])
def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RoleService.get_role(db, role_id)

@router.put("/{role_id}", response_model=RoleResponse, dependencies=[Depends(PermissionChecker("role:update"))])
def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RoleService.update_role(db, role_id, role)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(PermissionChecker("role:delete"))])
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    RoleService.delete_role(db, role_id)
    return None

@router.get("/permissions/list", response_model=List[PermissionResponse], dependencies=[Depends(PermissionChecker("permission:list"))])
def read_permissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return PermissionService.get_permissions(db, skip=skip, limit=limit)

@router.post("/permissions/", response_model=PermissionResponse, dependencies=[Depends(PermissionChecker("permission:create"))])
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return PermissionService.create_permission(db, permission)
