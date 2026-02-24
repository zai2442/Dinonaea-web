from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime

from app.db.database import get_db
from app.services.attack_log_service import AttackLogService
from app.schemas.attack_log import AttackLog, AttackLogFilter, AttackLogStats
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/logs", response_model=List[AttackLog])
def read_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    source_ip: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    attack_type: Optional[str] = None
) -> Any:
    """
    Retrieve attack logs with filtering.
    """
    filters = AttackLogFilter(
        offset=skip,
        limit=limit,
        start_time=start_time,
        end_time=end_time,
        source_ip=source_ip,
        username=username,
        password=password,
        attack_type=attack_type
    )
    service = AttackLogService(db)
    logs, total = service.get_logs(filters)
    return logs

@router.get("/stats/charts")
def get_stats_charts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get statistics for charts (Top IPs, Usernames, Passwords).
    Cached for 10 minutes.
    """
    service = AttackLogService(db)
    return service.get_statistics()

@router.get("/stats/summary")
def get_stats_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get summary statistics (Most frequent IP, Username, Password).
    Compatible with Login_statistics.sh output format conceptually.
    """
    service = AttackLogService(db)
    return service.get_summary()

@router.post("/refresh")
def refresh_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Force refresh statistics cache.
    Called by external scripts when logs change.
    """
    service = AttackLogService(db)
    return service.refresh_stats()

@router.get("/stats/traffic")
def get_traffic_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    source_ip: Optional[str] = None,
    attack_type: Optional[str] = None
) -> Any:
    """
    Get detailed traffic analysis statistics (Attack Distribution, Timeline).
    Supports filtering.
    """
    filters = AttackLogFilter(
        start_time=start_time,
        end_time=end_time,
        source_ip=source_ip,
        attack_type=attack_type
    )
    service = AttackLogService(db)
    return service.get_traffic_stats(filters)
