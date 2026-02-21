from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.user_service import UserService

class AuthService:
    @staticmethod
    def login(db: Session, username: str, password: str) -> Token:
        user = UserService.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
            
        if user.status != "active":
            raise HTTPException(status_code=403, detail="User is inactive")
            
        access_token = create_access_token(data={"sub": user.username, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.username, "id": user.id})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
