from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_current_active_user
from app.models.user import User

# Mock User
mock_user = User(id=1, username="testadmin", email="admin@example.com", status="active")

def override_get_current_active_user():
    return mock_user

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

def test_create_node(client: TestClient):
    response = client.post(
        "/api/v1/nodes/",
        json={"name": "Test Node", "ip_address": "192.168.1.100", "port": 80, "group": "default"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Node"
    assert data["ip_address"] == "192.168.1.100"
    assert data["status"] == "offline"

def test_read_nodes(client: TestClient):
    response = client.get("/api/v1/nodes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Node"

def test_update_node_status(client: TestClient):
    # First get the node ID
    nodes = client.get("/api/v1/nodes/").json()
    node_id = nodes[0]["id"]

    response = client.post(
        f"/api/v1/nodes/{node_id}/status",
        json={"status": "online", "cpu_usage": 45.5, "cpu_usage_detail": "{}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["cpu_usage"] == 45.5

def test_delete_node(client: TestClient):
    nodes = client.get("/api/v1/nodes/").json()
    node_id = nodes[0]["id"]
    
    response = client.delete(f"/api/v1/nodes/{node_id}")
    assert response.status_code == 204
    
    response = client.get(f"/api/v1/nodes/{node_id}")
    assert response.status_code == 404
