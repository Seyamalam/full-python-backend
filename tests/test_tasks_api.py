"""
Tests for task management API endpoints
"""
import json
import pytest
import time

def test_create_task(client, admin_token, user_token):
    """Test creating a task"""
    task_data = {
        "name": "Test Task",
        "description": "This is a test task",
        "duration": 1  # Short duration for testing
    }
    
    # Test with user token
    response = client.post(
        "/api/tasks",
        data=json.dumps(task_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["task"]["name"] == "Test Task"
    assert data["task"]["status"] == "pending"
    
    # Test with admin token
    response = client.post(
        "/api/tasks",
        data=json.dumps(task_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    
    # Test with invalid data
    invalid_data = {
        "name": "Invalid Task",
        "duration": 0  # Invalid duration
    }
    
    response = client.post(
        "/api/tasks",
        data=json.dumps(invalid_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 400
    
    invalid_data = {
        "name": "Invalid Task",
        "duration": 61  # Invalid duration (too long)
    }
    
    response = client.post(
        "/api/tasks",
        data=json.dumps(invalid_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 400

def test_get_tasks(client, admin_token, user_token):
    """Test getting all tasks"""
    # Create tasks for both users
    admin_task = {
        "name": "Admin Task",
        "description": "This is an admin task",
        "duration": 1
    }
    
    user_task = {
        "name": "User Task",
        "description": "This is a user task",
        "duration": 1
    }
    
    client.post(
        "/api/tasks",
        data=json.dumps(admin_task),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    client.post(
        "/api/tasks",
        data=json.dumps(user_task),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    # Admin can see all tasks
    admin_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert admin_response.status_code == 200
    admin_data = json.loads(admin_response.data)
    assert "tasks" in admin_data
    assert isinstance(admin_data["tasks"], list)
    
    # User can only see their own tasks
    user_response = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert user_response.status_code == 200
    user_data = json.loads(user_response.data)
    assert "tasks" in user_data
    
    # Admin should see more tasks than a regular user
    assert len(admin_data["tasks"]) >= len(user_data["tasks"])
    
    # Verify user can only see their own tasks
    if len(user_data["tasks"]) > 0:
        user_task_names = [task["name"] for task in user_data["tasks"]]
        assert "Admin Task" not in user_task_names

def test_get_task_by_id(client, admin_token, user_token):
    """Test getting a task by ID"""
    # Create a task
    task_data = {
        "name": "Task to Get",
        "description": "This task will be retrieved by ID",
        "duration": 1
    }
    
    create_response = client.post(
        "/api/tasks",
        data=json.dumps(task_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    task_id = json.loads(create_response.data)["task"]["id"]
    
    # User can get their own task
    response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["task"]["name"] == "Task to Get"
    
    # Admin can get any task
    response = client.get(
        f"/api/tasks/{task_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Test with non-existent ID
    response = client.get(
        "/api/tasks/non-existent-id",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404

def test_cancel_task(client, admin_token, user_token):
    """Test cancelling a task"""
    # Create a task
    task_data = {
        "name": "Task to Cancel",
        "description": "This task will be cancelled",
        "duration": 5  # Longer duration so we can cancel it
    }
    
    create_response = client.post(
        "/api/tasks",
        data=json.dumps(task_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    task_id = json.loads(create_response.data)["task"]["id"]
    
    # Wait a moment for task to start processing
    time.sleep(0.5)
    
    # User can cancel their own task
    response = client.post(
        f"/api/tasks/{task_id}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["task"]["status"] == "cancelled"
    
    # Create another task for admin to cancel
    task_data = {
        "name": "Admin Cancel Task",
        "description": "This task will be cancelled by admin",
        "duration": 5
    }
    
    create_response = client.post(
        "/api/tasks",
        data=json.dumps(task_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    task_id = json.loads(create_response.data)["task"]["id"]
    
    # Wait a moment for task to start processing
    time.sleep(0.5)
    
    # Admin can cancel any task
    response = client.post(
        f"/api/tasks/{task_id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["task"]["status"] == "cancelled"