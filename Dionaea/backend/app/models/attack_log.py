from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from datetime import datetime
from typing import Optional

class AttackLog(BaseModel):
    __tablename__ = "attack_logs"

    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True, index=True)
    password: Mapped[str] = mapped_column(String, nullable=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=True, index=True)
    protocol: Mapped[str] = mapped_column(String, nullable=True)
    sensor_name: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_attack_log_time_user_ip", "timestamp", "username", "source_ip"),
    )
