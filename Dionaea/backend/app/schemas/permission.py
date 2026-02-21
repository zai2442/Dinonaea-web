from pydantic import BaseModel
from typing import Optional

class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None
    resource_type: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    description: Optional[str] = None
    resource_type: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int

    class Config:
        from_attributes = True
