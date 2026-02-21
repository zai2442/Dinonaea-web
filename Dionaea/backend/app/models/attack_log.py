from sqlalchemy import String, DateTime, Index, Integer
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
    target_port: Mapped[int] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String, nullable=True)
    connection_status: Mapped[str] = mapped_column(String, nullable=True)
    sensor_name: Mapped[str] = mapped_column(String, nullable=True)
    raw_log: Mapped[str] = mapped_column(String, nullable=True)
    attack_type: Mapped[str] = mapped_column(String, nullable=True, index=True)

    __table_args__ = (
        Index("idx_attack_log_time_user_ip", "timestamp", "username", "source_ip"),
    )
