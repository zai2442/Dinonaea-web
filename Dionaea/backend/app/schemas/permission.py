from pydantic import BaseModel
from typing import Optional

class PermissionBase(BaseModel):
    name: Optional[str] = None
    code: str
    description: Optional[str] = None
    resource_type: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int

    class Config:
        from_attributes = True
