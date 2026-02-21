import sys
import os
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine, Base
from app.models.role import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash

def init_db(db: Session) -> None:
    # Create Tables
    Base.metadata.create_all(bind=engine)

    # 1. Create Permissions
    permissions_data = [
        {"code": "user:list", "description": "List users", "resource_type": "user"},
        {"code": "user:create", "description": "Create user", "resource_type": "user"},
        {"code": "user:read", "description": "Read user details", "resource_type": "user"},
        {"code": "user:update", "description": "Update user", "resource_type": "user"},
        {"code": "user:delete", "description": "Delete user", "resource_type": "user"},
        
        {"code": "role:list", "description": "List roles", "resource_type": "role"},
        {"code": "role:create", "description": "Create role", "resource_type": "role"},
        {"code": "role:read", "description": "Read role details", "resource_type": "role"},
        {"code": "role:update", "description": "Update role", "resource_type": "role"},
        {"code": "role:delete", "description": "Delete role", "resource_type": "role"},
        
        {"code": "data:stats", "description": "View statistics", "resource_type": "data"},
        {"code": "system:monitor", "description": "Monitor system status", "resource_type": "system"},
    ]

    permissions = {}
    for p_data in permissions_data:
        p = db.query(Permission).filter(Permission.code == p_data["code"]).first()
        if not p:
            p = Permission(**p_data)
            db.add(p)
            db.commit()
            db.refresh(p)
            print(f"Created Permission: {p.code}")
        permissions[p.code] = p

    # 2. Create Roles
    roles_data = [
        {"name": "Super Admin", "code": "super_admin", "description": "System Administrator with full access"},
        {"name": "Admin", "code": "admin", "description": "Administrator with limited access"},
        {"name": "User", "code": "user", "description": "Standard User"},
    ]

    roles = {}
    for r_data in roles_data:
        r = db.query(Role).filter(Role.code == r_data["code"]).first()
        if not r:
            r = Role(**r_data)
            db.add(r)
            db.commit()
            db.refresh(r)
            print(f"Created Role: {r.name}")
        roles[r.code] = r

    # 3. Assign Permissions to Roles
    # Super Admin gets all permissions (implicitly or explicitly)
    # Explicitly assign all for clarity
    roles["super_admin"].permissions = list(permissions.values())
    
    # Admin gets user management and stats
    admin_perms = [
        permissions["user:list"], permissions["user:read"], 
        permissions["data:stats"], permissions["system:monitor"]
    ]
    roles["admin"].permissions = admin_perms

    db.commit()
    print("Permissions assigned to roles.")

    # 4. Create Initial Users
    users_data = [
        {"username": "admin", "email": "admin@example.com", "password": "password", "role": "super_admin"},
        {"username": "manager", "email": "manager@example.com", "password": "password", "role": "admin"},
        {"username": "user", "email": "user@example.com", "password": "password", "role": "user"},
    ]

    for u_data in users_data:
        user = db.query(User).filter(User.username == u_data["username"]).first()
        role = roles.get(u_data["role"])
        
        if not user:
            user = User(
                username=u_data["username"],
                email=u_data["email"],
                password_hash=get_password_hash(u_data["password"]),
                status="active"
            )
            if role:
                user.roles.append(role)
            db.add(user)
            db.commit()
            print(f"Created User: {user.username}")
        else:
            # Ensure role is assigned
            if role and role not in user.roles:
                user.roles.append(role)
                db.commit()
                print(f"Updated User Role: {user.username} -> {role.name}")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
