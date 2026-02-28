from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime, time

from app.db.database import get_db
from app.services.attack_log_service import AttackLogService
from app.schemas.attack_log import AttackLog, AttackLogFilter, AttackLogStats
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

def parse_date_string(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parses a date string in format MM/DD, YYYY-MM-DD, etc.
    If only MM/DD is provided, assumes current year.
    """
    if not date_str:
        return None
    
    # Try common formats
    formats = [
        "%Y/%m/%d",    # 2026/02/27
        "%Y-%m-%d",    # 2026-02-27
        "%m/%d",       # 02/27
        "%m-%d",       # 02-27
    ]
    
    current_year = datetime.now().year
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if "%Y" not in fmt:
                dt = dt.replace(year=current_year)
            return dt
        except ValueError:
            continue
            
    # If it's already an ISO format string, Pydantic might have handled it, 
    # but we are receiving strings from Query params sometimes.
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return None

@router.get("/logs", response_model=List[AttackLog])
def read_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50,
    start_time: Optional[str] = Query(None, description="Start time (e.g. 02/27 or 2026-02-27)"),
    end_time: Optional[str] = Query(None, description="End time (e.g. 02/28 or 2026-02-28)"),
    source_ip: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    attack_type: Optional[str] = None
) -> Any:
    """
    Retrieve attack logs with filtering.
    """
    # Parse start_time
    parsed_start = parse_date_string(start_time)
    if parsed_start:
        # If it was a simple date (no time component), or if we want to ensure full day
        # we combine with time.min/max. 
        # Note: if it came from ISO with T00:00:00Z, .date() is safer for naive DB
        parsed_start = datetime.combine(parsed_start.date(), time.min)
        
    # Parse end_time
    parsed_end = parse_date_string(end_time)
    if parsed_end:
        parsed_end = datetime.combine(parsed_end.date(), time.max)

    import logging
    logger = logging.getLogger("app.api.v1.data")
    logger.info(f"Query logs: start_time={start_time} -> {parsed_start}, end_time={end_time} -> {parsed_end}")

    filters = AttackLogFilter(
        offset=skip,
        limit=limit,
        start_time=parsed_start,
        end_time=parsed_end,
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
    start_time: Optional[str] = Query(None, description="Start time (e.g. 02/27 or 2026-02-27)"),
    end_time: Optional[str] = Query(None, description="End time (e.g. 02/28 or 2026-02-28)"),
    source_ip: Optional[str] = None,
    attack_type: Optional[str] = None
) -> Any:
    """
    Get detailed traffic analysis statistics (Attack Distribution, Timeline).
    Supports filtering.
    """
    # Parse dates
    parsed_start = parse_date_string(start_time)
    if parsed_start:
        parsed_start = datetime.combine(parsed_start.date(), time.min)
        
    parsed_end = parse_date_string(end_time)
    if parsed_end:
        parsed_end = datetime.combine(parsed_end.date(), time.max)

    filters = AttackLogFilter(
        start_time=parsed_start,
        end_time=parsed_end,
        source_ip=source_ip,
        attack_type=attack_type
    )
    service = AttackLogService(db)
    return service.get_traffic_stats(filters)
