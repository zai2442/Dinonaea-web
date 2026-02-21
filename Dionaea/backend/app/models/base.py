from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Boolean, Integer, String
from datetime import datetime
from app.db.database import Base
from typing import Optional

class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    create_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    update_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, default=1)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
