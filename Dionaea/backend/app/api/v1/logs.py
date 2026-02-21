from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime

from app.db.database import get_db
from app.services.attack_log_service import AttackLogService
from app.schemas.attack_log import AttackLog, AttackLogFilter
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[AttackLog])
def get_logs(
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
    Get attack logs with filtering.
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
