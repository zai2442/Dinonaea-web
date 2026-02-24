from sqlalchemy import String, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from app.models.base import BaseModel
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User

# Association Table for Role-Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", index=True)

    users: Mapped[List["User"]] = relationship("User", secondary="user_roles", back_populates="roles")
    permissions: Mapped[List["Permission"]] = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(BaseModel):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String, nullable=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    resource_type: Mapped[str] = mapped_column(String, nullable=True)

    roles: Mapped[List["Role"]] = relationship("Role", secondary=role_permissions, back_populates="permissions")
