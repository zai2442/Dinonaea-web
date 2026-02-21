import logging
import passlib.handlers.bcrypt
import bcrypt
from passlib.context import CryptContext

# Fix for passlib 1.7.4 with bcrypt 4.0+
try:
    # 1. Fix AttributeError: module 'bcrypt' has no attribute '__about__'
    if not hasattr(bcrypt, '__about__'):
        class About:
            __version__ = bcrypt.__version__
        bcrypt.__about__ = About()
        
    # 2. Fix ValueError: password cannot be longer than 72 bytes
    # This happens in passlib.handlers.bcrypt._detect_wrap_bug which calls hashpw with a long secret
    original_hashpw = bcrypt.hashpw
    def patched_hashpw(password, salt):
        try:
            return original_hashpw(password, salt)
        except ValueError as e:
            # If bcrypt raises "password cannot be longer than 72 bytes", we truncate it.
            # This mimics the old behavior that passlib expects.
            if "password cannot be longer than 72 bytes" in str(e):
                if isinstance(password, str):
                    password = password.encode('utf-8')
                # Truncate to 72 bytes
                if len(password) > 72:
                    password = password[:72]
                return original_hashpw(password, salt)
            raise e
    bcrypt.hashpw = patched_hashpw
    
except Exception as e:
    logging.warning(f"Failed to patch passlib/bcrypt: {e}")

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
