from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_log"

    user_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    resource_id: Mapped[str] = mapped_column(String, nullable=True)
    params: Mapped[dict] = mapped_column(JSON, nullable=True)
    result: Mapped[str] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
