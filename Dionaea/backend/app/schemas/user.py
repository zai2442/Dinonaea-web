from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.role import RoleResponse

class UserBase(BaseModel):
    username: str
    email: EmailStr
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[int]] = []

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    status: Optional[str] = None
    password: Optional[str] = None
    role_ids: Optional[List[int]] = None
    version: int

class UserResponse(UserBase):
    id: int
    create_time: datetime
    update_time: datetime
    version: int
    deleted: bool
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True

class UserList(BaseModel):
    total: int
    items: List[UserResponse]
