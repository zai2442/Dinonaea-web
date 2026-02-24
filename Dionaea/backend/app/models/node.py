from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from typing import Optional, List
from app.models.base import BaseModel
from app.db.database import Base

class Node(BaseModel):
    __tablename__ = "nodes"

    ip_address: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=80)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    group: Mapped[Optional[str]] = mapped_column(String(50), default="default")
    
    # Status monitoring fields
    status: Mapped[str] = mapped_column(String(20), default="offline")  # online, offline, warning
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    cpu_usage_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON string for user/kernel/idle
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) 

    history: Mapped[List["NodeHistory"]] = relationship("NodeHistory", back_populates="node", cascade="all, delete-orphan")

class NodeHistory(BaseModel):
    __tablename__ = "node_history"

    node_id: Mapped[int] = mapped_column(Integer, ForeignKey("nodes.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    node: Mapped["Node"] = relationship("Node", back_populates="history")
