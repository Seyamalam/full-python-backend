"""
Tests for user management API endpoints
"""
import json
import pytest

def test_get_users_as_admin(client, admin_token):
    """Test getting all users as admin"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert isinstance(data["users"], list)
    assert "total" in data
    assert "pages" in data

def test_get_users_as_regular_user(client, user_token):
    """Test getting all users as regular user (should fail)"""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403

def test_get_user_by_id(client, admin_token, user_token):
    """Test getting a user by ID"""
    # Get current admin user
    admin_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_id = json.loads(admin_response.data)["user"]["id"]
    
    # Get current regular user
    user_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    user_id = json.loads(user_response.data)["user"]["id"]
    
    # Admin can get any user
    response = client.get(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # User can get their own profile
    response = client.get(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    
    # User cannot get another user's profile
    response = client.get(
        f"/api/users/{admin_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_update_user(client, admin_token, user_token):
    """Test updating a user"""
    # Get current regular user
    user_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    user_id = json.loads(user_response.data)["user"]["id"]
    
    # User can update their own profile
    update_data = {
        "first_name": "Updated",
        "last_name": "User"
    }
    
    response = client.put(
        f"/api/users/{user_id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["first_name"] == "Updated"
    assert data["user"]["last_name"] == "User"
    
    # Admin can update any user
    admin_update_data = {
        "first_name": "Admin",
        "last_name": "Updated"
    }
    
    response = client.put(
        f"/api/users/{user_id}",
        data=json.dumps(admin_update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["user"]["first_name"] == "Admin"
    assert data["user"]["last_name"] == "Updated"

def test_delete_user(client, admin_token, user_token):
    """Test deleting a user"""
    # Create a user to delete
    register_data = {
        "username": "delete_test",
        "email": "delete@example.com",
        "password": "Delete123!",
        "password_confirm": "Delete123!"
    }
    
    register_response = client.post(
        "/api/auth/register",
        data=json.dumps(register_data),
        content_type="application/json"
    )
    
    user_id = json.loads(register_response.data)["user"]["id"]
    
    # Regular user cannot delete users
    response = client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Admin can delete users
    response = client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify user is deleted
    response = client.get(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404