from sqlalchemy.orm import Session
from sqlalchemy import select, text, func
from fastapi import HTTPException
from app.models.base import BaseModel
from app.models.audit import AuditLog
from typing import Type, List, Any
import json
from datetime import datetime

class GenericService:
    def __init__(self, model: Type[BaseModel]):
        self.model = model

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        filters: dict = None, 
        sort_by: str = None
    ) -> dict:
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if isinstance(value, str) and ":" in value:
                        # Format: field=op:value (e.g., age=gt:18)
                        op, val = value.split(":", 1)
                        if op == "gt":
                            query = query.where(column > val)
                        elif op == "lt":
                            query = query.where(column < val)
                        elif op == "gte":
                            query = query.where(column >= val)
                        elif op == "lte":
                            query = query.where(column <= val)
                        elif op == "like":
                            query = query.where(column.ilike(f"%{val}%"))
                        elif op == "eq":
                            query = query.where(column == val)
                    else:
                        query = query.where(column == value)
        
        # Apply sort
        if sort_by:
            desc = False
            if sort_by.startswith("-"):
                desc = True
                sort_by = sort_by[1:]
            
            if hasattr(self.model, sort_by):
                column = getattr(self.model, sort_by)
                query = query.order_by(column.desc() if desc else column.asc())
        else:
            # Default sort by id desc
            query = query.order_by(self.model.id.desc())
            
        # Count
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        
        # Pagination
        items = db.scalars(query.offset(skip).limit(limit)).all()
        
        return {"total": total, "items": items}

    def create(self, db: Session, obj_in: dict, current_user_id: int) -> BaseModel:
        obj_data = obj_in.copy()
        obj_data["create_by"] = current_user_id
        obj_data["update_by"] = current_user_id
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Audit
        self._audit(db, current_user_id, "CREATE", str(db_obj.id), obj_in)
        return db_obj

    def update(self, db: Session, id: Any, obj_in: dict, current_user_id: int) -> BaseModel:
        db_obj = db.get(self.model, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # Optimistic Locking
        if "version" in obj_in and obj_in["version"] != db_obj.version:
             raise HTTPException(status_code=409, detail="Conflict: Data modified by another user")

        update_data = obj_in.copy()
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db_obj.update_by = current_user_id
        db_obj.version += 1
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Audit
        self._audit(db, current_user_id, "UPDATE", str(id), update_data)
        return db_obj

    def delete(self, db: Session, id: Any, current_user_id: int):
        db_obj = db.get(self.model, id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # Soft delete if supported
        if hasattr(db_obj, "deleted"):
            db_obj.deleted = True
            db_obj.update_by = current_user_id
            db.add(db_obj)
        else:
            db.delete(db_obj)
            
        db.commit()
        
        # Audit
        self._audit(db, current_user_id, "DELETE", str(id), {})

    def _audit(self, db: Session, user_id: int, action: str, resource_id: str, params: dict):
        audit = AuditLog(
            user_id=user_id,
            action=f"{action}_{self.model.__tablename__.upper()}",
            resource_id=resource_id,
            params=params,
            result="SUCCESS"
        )
        db.add(audit)
        db.commit()
