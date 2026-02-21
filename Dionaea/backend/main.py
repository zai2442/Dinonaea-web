from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db, Base, engine
from models import AttackLog
from pydantic import BaseModel

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dionaea Log Manager", version="0.1.0")

# Pydantic Schemas
class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    username: Optional[str]
    password: Optional[str]
    source_ip: str
    created_at: datetime

    class Config:
        from_attributes = True

@app.get("/logs", response_model=List[LogResponse])
def get_logs(
    skip: int = 0, 
    limit: int = 100,
    username: Optional[str] = None,
    source_ip: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AttackLog)
    
    if username:
        query = query.filter(AttackLog.username.ilike(f"%{username}%"))
    if source_ip:
        query = query.filter(AttackLog.source_ip == source_ip)
    if start_date:
        query = query.filter(AttackLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AttackLog.timestamp <= end_date)
        
    logs = query.order_by(AttackLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@app.get("/logs/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(AttackLog).count()
    unique_ips = db.query(AttackLog.source_ip).distinct().count()
    return {
        "total_attacks": total,
        "unique_attackers": unique_ips
    }

@app.get("/")
def read_root():
    return {"message": "Dionaea Log Manager API is running"}
