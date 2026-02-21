import sys
import os
import requests

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import SessionLocal
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import create_access_token

def create_user_and_get_token():
    db = SessionLocal()
    try:
        # 1. Create User
        username = "stress_test_user"
        password = "password123"
        email = "stress@example.com"
        
        user = UserService.get_by_username(db, username)
        if not user:
            print(f"Creating user {username}...")
            # We need to construct a UserCreate schema or just use the model directly if service allows
            # Service expects UserCreate schema usually, let's check.
            # UserService.create_user(db, user_in: UserCreate, ...)
            # Let's just do it manually via DB for simplicity or import schema
            from app.schemas.user import UserCreate
            user_in = UserCreate(username=username, password=password, email=email, status="active")
            user = UserService.create_user(db, user_in, current_user_id=0)
        else:
            print(f"User {username} exists.")
            
        # 2. Generate Token
        # We can use the login endpoint or just generate it using internal util
        # Login endpoint: POST /api/v1/auth/login
        
        # Let's try to login via requests to verify the full flow
        login_url = "http://localhost:8001/api/v1/auth/login"
        response = requests.post(login_url, data={"username": username, "password": password})
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"TOKEN={token}")
            
            # Write token to a file for ab to use (ab doesn't read file easily for headers, we might need to copy paste)
            # Actually ab -H "Authorization: Bearer <token>" works.
            with open("token.txt", "w") as f:
                f.write(token)
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user_and_get_token()
