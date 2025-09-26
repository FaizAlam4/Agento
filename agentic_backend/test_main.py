import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["message"] == "Backend service is running"
    assert "timestamp" in data
    assert "environment" in data

def test_api_test_endpoint():
    """Test the API test endpoint"""
    response = client.get("/api/test")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello from Agentic Backend!"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data

def test_get_users():
    """Test getting users"""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Initial users

def test_create_user():
    """Test creating a new user"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data

def test_not_found():
    """Test 404 handling"""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "Not Found"