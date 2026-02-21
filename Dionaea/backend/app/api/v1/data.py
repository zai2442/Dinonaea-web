from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.generic_service import GenericService
from app.core.models_registry import get_model
from app.core.dependencies import get_current_active_user
from app.models.user import User
from typing import Optional, List, Any
import json

router = APIRouter()

@router.get("/{resource}")
def read_resource(
    resource: str,
    skip: int = 0,
    limit: int = 100,
    sort: Optional[str] = None,
    filter: Optional[str] = Query(None, description="Format: field:op:value, e.g. age:gt:18"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    model = get_model(resource)
    if not model:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    filters = {}
    if filter:
        # Simple parsing logic for filter query param
        # Assume filter=field:op:value or multiple filters comma separated?
        # Let's assume one filter string for simplicity or multiple query params
        # But filter param is single string here.
        # Format: field1:op1:val1,field2:op2:val2
        parts = filter.split(",")
        for part in parts:
            if ":" in part:
                field, op, val = part.split(":", 2)
                filters[field] = f"{op}:{val}"
    
    service = GenericService(model)
    return service.get_multi(db, skip=skip, limit=limit, filters=filters, sort_by=sort)

@router.post("/{resource}")
def create_resource(
    resource: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    model = get_model(resource)
    if not model:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    service = GenericService(model)
    return service.create(db, payload, current_user.id)

@router.put("/{resource}/{id}")
def update_resource(
    resource: str,
    id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    model = get_model(resource)
    if not model:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    service = GenericService(model)
    return service.update(db, id, payload, current_user.id)

@router.delete("/{resource}/{id}")
def delete_resource(
    resource: str,
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    model = get_model(resource)
    if not model:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    service = GenericService(model)
    service.delete(db, id, current_user.id)
    return {"status": "success"}
