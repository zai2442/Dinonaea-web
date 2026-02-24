from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash
from app.main import app

def create_role(db: Session, code: str, name: str):
    role = db.query(Role).filter(Role.code == code).first()
    if not role:
        role = Role(name=name, code=code)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

def create_user(db: Session, username: str, role_code: str):
    role = create_role(db, role_code, role_code.capitalize())
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=get_password_hash("password"),
            status="active",
            version=1
        )
        user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_token(client: TestClient, username: str):
    response = client.post("/api/v1/auth/login", data={"username": username, "password": "password"})
    return response.json()["access_token"]

def test_super_admin_operations(client: TestClient, db: Session):
    # Setup Super Admin
    admin = create_user(db, "superadmin", "super_admin")
    token = get_token(client, "superadmin")
    headers = {"Authorization": f"Bearer {token}"}

    # Create Target User
    target_user = User(
        username="target",
        email="target@example.com",
        password_hash=get_password_hash("password"),
        status="active",
        version=1
    )
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    target_id = target_user.id
    target_version = target_user.version

    # 1. Update User (Success)
    update_payload = {
        "username": "target_updated",
        "email": "target_updated@example.com",
        "version": target_version
    }
    response = client.put(f"/api/v1/users/{target_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "target_updated"
    assert data["version"] == target_version + 1
    new_version = data["version"]

    # 2. Update User (Conflict)
    conflict_payload = {
        "username": "target_conflict",
        "version": target_version # Old version
    }
    response = client.put(f"/api/v1/users/{target_id}", json=conflict_payload, headers=headers)
    assert response.status_code == 409

    # 3. Update User (Uniqueness Error)
    # Create another user to conflict with
    other_user = User(
        username="other",
        email="other@example.com",
        password_hash=get_password_hash("password"),
        status="active",
        version=1
    )
    db.add(other_user)
    db.commit()
    
    unique_payload = {
        "username": "other", # Conflict
        "version": new_version
    }
    response = client.put(f"/api/v1/users/{target_id}", json=unique_payload, headers=headers)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

    # 4. Delete User (Success)
    response = client.delete(f"/api/v1/users/{target_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify Hard Delete
    deleted_user = db.get(User, target_id)
    assert deleted_user is None

def test_admin_protection(client: TestClient, db: Session):
    # Setup Admin User
    admin = create_user(db, "admin", "super_admin")
    admin.version = 1
    db.commit()
    # Refresh to ensure it's bound, but then get ID immediately
    db.refresh(admin)
    admin_id = admin.id
    
    # Setup Super Admin (Attacker)
    attacker = create_user(db, "attacker", "super_admin")
    token = get_token(client, "attacker")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try Update 'admin'
    response = client.put(f"/api/v1/users/{admin_id}", json={"username": "hacked", "version": 1}, headers=headers)
    assert response.status_code == 403
    assert "Cannot modify the built-in admin user" in response.json()["detail"]
    
    # Try Delete 'admin'
    response = client.delete(f"/api/v1/users/{admin_id}", headers=headers)
    assert response.status_code == 403
    assert "Cannot delete the built-in admin user" in response.json()["detail"]

def test_soft_deleted_collision(client: TestClient, db: Session):
    # Setup Super Admin
    token = get_token(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create a user manually with deleted=True (simulate legacy soft delete)
    # Note: Using SQLAlchemy to bypass any logic in create_user
    legacy_user = User(
        username="legacy_user",
        email="legacy@example.com",
        password_hash=get_password_hash("password"),
        status="active",
        version=1,
        deleted=True # Simulate soft deleted
    )
    db.add(legacy_user)
    db.commit()
    
    # 2. Try to create a NEW user with SAME username via API
    payload = {
        "username": "legacy_user",
        "email": "new_email@example.com",
        "password": "password",
        "status": "active"
    }
    
    # This should FAIL with 500 or IntegrityError if not handled, 
    # OR succeed if handled correctly (our goal)
    try:
        response = client.post("/api/v1/users/", json=payload, headers=headers)
        if response.status_code == 200:
            print("Successfully handled collision!")
            # Verify data
            new_user = response.json()
            assert new_user["username"] == "legacy_user"
            assert new_user["email"] == "new_email@example.com"
        else:
            print(f"Failed with status {response.status_code}: {response.text}")
            assert response.status_code == 200
    except Exception as e:
        print(f"Exception: {e}")
        raise e

def test_regular_user_denied(client: TestClient, db: Session):
    # Setup Regular User
    user = create_user(db, "regular", "user")
    token = get_token(client, "regular")
    headers = {"Authorization": f"Bearer {token}"}

    # Create Target User
    target_user = User(
        username="target2",
        email="target2@example.com",
        password_hash=get_password_hash("password"),
        status="active",
        version=1
    )
    db.add(target_user)
    db.commit()
    db.refresh(target_user)
    
    # Try Update
    response = client.put(f"/api/v1/users/{target_user.id}", json={"username": "hacked", "version": 1}, headers=headers)
    assert response.status_code == 403

    # Try Delete
    response = client.delete(f"/api/v1/users/{target_user.id}", headers=headers)
    assert response.status_code == 403