from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.main import app
import pytest

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data # Ensure password is not returned

def test_register_duplicate_username():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "email": "unique@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "email": "other@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_register_duplicate_email():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_register_invalid_email():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user_invalid",
            "email": "invalid-email",
            "password": "testpassword",
        },
    )
    assert response.status_code == 422 # Validation Error
