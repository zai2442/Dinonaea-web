from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.role import Role, Permission
from app.models.user import User
from app.core.security import get_password_hash

def get_token(client: TestClient, username: str):
    response = client.post("/api/v1/auth/login", data={"username": username, "password": "password"})
    return response.json()["access_token"]

def create_permission(db: Session, code: str, name: str):
    perm = Permission(code=code, name=name, description="Test Perm")
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm

def test_role_management_flow(client: TestClient, db: Session):
    # 1. Setup Super Admin
    # Ensure super admin role exists
    sa_role = db.query(Role).filter(Role.code == "super_admin").first()
    if not sa_role:
        sa_role = Role(name="Super Admin", code="super_admin")
        db.add(sa_role)
        db.commit()
        
    admin_user = db.query(User).filter(User.username == "superadmin_role_test").first()
    if not admin_user:
        admin_user = User(
            username="superadmin_role_test",
            email="sa_role@test.com",
            password_hash=get_password_hash("password"),
            status="active"
        )
        admin_user.roles.append(sa_role)
        db.add(admin_user)
        db.commit()
    
    token = get_token(client, "superadmin_role_test")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Permissions
    p1 = create_permission(db, "test:read", "Read Test")
    p2 = create_permission(db, "test:write", "Write Test")
    
    # 3. Create Role with Permissions
    role_payload = {
        "name": "Test Role",
        "code": "test_role",
        "description": "A test role",
        "status": "active",
        "permission_ids": [p1.id, p2.id]
    }
    
    response = client.post("/api/v1/roles/", json=role_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Role"
    assert len(data["permissions"]) == 2
    role_id = data["id"]
    
    # 4. Update Role (Remove one permission, change status)
    update_payload = {
        "status": "disabled",
        "permission_ids": [p1.id]
    }
    response = client.put(f"/api/v1/roles/{role_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disabled"
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["code"] == "test:read"
    
    # 5. Delete Role
    response = client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify deletion
    deleted_role = db.get(Role, role_id)
    assert deleted_role is None

def test_system_role_protection(client: TestClient, db: Session):
    # Setup Super Admin
    token = get_token(client, "superadmin_role_test")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Super Admin Role ID
    sa_role = db.query(Role).filter(Role.code == "super_admin").first()
    
    # Try to delete system role
    response = client.delete(f"/api/v1/roles/{sa_role.id}", headers=headers)
    assert response.status_code == 403
