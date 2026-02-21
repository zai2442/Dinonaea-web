from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttackLogBase(BaseModel):
    timestamp: datetime
    username: Optional[str] = None
    password: Optional[str] = None
    source_ip: Optional[str] = None
    target_port: Optional[int] = None
    protocol: Optional[str] = None
    connection_status: Optional[str] = None
    sensor_name: Optional[str] = None
    raw_log: Optional[str] = None
    attack_type: Optional[str] = None

class AttackLogCreate(AttackLogBase):
    pass

class AttackLog(AttackLogBase):
    id: int

    class Config:
        from_attributes = True

class AttackLogStats(BaseModel):
    top_ips: list[dict]
    top_usernames: list[dict]
    top_passwords: list[dict]
    total_count: int

class AttackLogFilter(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source_ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    attack_type: Optional[str] = None
    limit: int = 50
    offset: int = 0
