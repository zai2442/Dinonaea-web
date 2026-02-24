from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, List
from datetime import datetime

class NodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str
    port: int = Field(80, ge=1, le=65535)
    description: Optional[str] = None
    group: Optional[str] = "default"
    is_active: bool = True

class NodeCreate(NodeBase):
    pass

class NodeUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    description: Optional[str] = None
    group: Optional[str] = None
    is_active: Optional[bool] = None

class NodeStatusUpdate(BaseModel):
    status: str
    cpu_usage: float
    cpu_usage_detail: Optional[str] = None

class NodeResponse(NodeBase):
    id: int
    status: str
    cpu_usage: float
    cpu_usage_detail: Optional[str]
    last_seen: Optional[datetime]
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True

class NodeHistoryResponse(BaseModel):
    id: int
    node_id: int
    status: str
    cpu_usage: float
    details: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
