from pydantic import BaseModel
from typing import Optional, List
from app.schemas.permission import PermissionResponse

class RoleBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    permission_ids: Optional[List[int]] = None

class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
