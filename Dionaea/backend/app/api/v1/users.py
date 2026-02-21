from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from app.services.user_service import UserService
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.core.permissions import PermissionChecker

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/", response_model=UserList, dependencies=[Depends(PermissionChecker("user:list"))])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    username: str = None, 
    status: str = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    return UserService.get_users(db, skip=skip, limit=limit, username=username, status=status)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return UserService.create_user(db, user, current_user_id=current_user.id)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return UserService.update_user(db, user_id, user, current_user_id=current_user.id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    UserService.delete_user(db, user_id, current_user_id=current_user.id)
    return None
