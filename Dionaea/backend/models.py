from sqlalchemy import Column, Integer, String, DateTime, Index
from database import Base
from datetime import datetime

class AttackLog(Base):
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    source_ip = Column(String(45), nullable=False)  # IPv6 support length
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_source_ip', 'source_ip'),
        Index('idx_username', 'username'),
    )

    def __repr__(self):
        return f"<AttackLog(time={self.timestamp}, ip={self.source_ip}, user={self.username})>"
