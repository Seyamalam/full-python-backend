"""
Tests for authentication routes
"""
import json
import pytest

def test_register(client):
    """Test user registration"""
    # Test successful registration
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "username": "testuser1",
            "email": "test@example1.com",
            "password": "Test123!",
            "password_confirm": "Test123!"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "testuser"
    
    # Test duplicate username
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "username": "testuser1",
            "email": "another@example1.com",
            "password": "Test123!",
            "password_confirm": "Test123!"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 409
    
    # Test password mismatch
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "username": "anotheruser1",
            "email": "another@example1.com",
            "password": "Test123!",
            "password_confirm": "Different123!"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400

def test_login(client, app):
    """Test user login"""
    # Get the admin user from the app context
    with app.app_context():
        from tests.conftest import TEST_ADMIN_ID
        admin = User.query.get(TEST_ADMIN_ID)
        
        # Test successful login with username
        response = client.post(
            "/api/auth/login",
            data=json.dumps({
                "username": admin.username,
                "password": "Admin123!"
            }),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "access_token" in data
        assert "refresh_token" in data
        
        # Test successful login with email
        response = client.post(
            "/api/auth/login",
            data=json.dumps({
                "email": admin.email,
                "password": "Admin123!"
            }),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        
        # Test invalid credentials
        response = client.post(
            "/api/auth/login",
            data=json.dumps({
                "username": admin.username,
                "password": "wrong_password"
            }),
            content_type="application/json"
        )
    
    assert response.status_code == 401

def test_me(client, admin_token, app):
    """Test get current user info"""
    # Get the admin user from the app context
    with app.app_context():
        from tests.conftest import TEST_ADMIN_ID
        admin = User.query.get(TEST_ADMIN_ID)
        
        # Test with valid token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["user"]["username"] == admin.username
    
    # Test with invalid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 422