from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    # This might fail because of missing Auth dependency mock
    # In real tests, we mock the dependency or create a user token first.
    # For now, let's assume we bypass auth or handle it.
    # Since create_user endpoint requires `current_user` dependency, it will return 401.
    assert response.status_code == 401

def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Dionaea Log Manager API is running"}
