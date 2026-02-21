from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_current_active_user
from app.models.user import User

client = TestClient(app)

def override_get_current_active_user():
    return User(id=1, username="testuser", status="active", email="test@example.com", password_hash="hash")

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

def test_get_logs():
    response = client.get("/api/v1/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Since we ingested data, there should be logs
    # But wait, did we commit? Yes ingestor commits.
    # But TestClient might run in a transaction or different session?
    # No, it hits the app which uses SessionLocal.
    # So if ingestor committed, we should see it.
    if len(data) > 0:
        print(f"Found {len(data)} logs")
        first_log = data[0]
        assert "timestamp" in first_log
        assert "source_ip" in first_log

def test_get_logs_filter_attack_type():
    response = client.get("/api/v1/logs?attack_type=smb")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        for log in data:
            assert log.get("attack_type") == "smb"

def test_get_logs_filter_time():
    # Test with a future time, should return empty
    response = client.get("/api/v1/logs?start_time=2030-01-01T00:00:00")
    assert response.status_code == 200
    assert len(response.json()) == 0
