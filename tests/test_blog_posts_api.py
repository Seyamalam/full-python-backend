"""
Tests for blog post management API endpoints
"""
import json
import pytest

def test_get_blog_posts(client):
    """Test getting all blog posts"""
    response = client.get("/api/blog")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "blog_posts" in data
    assert isinstance(data["blog_posts"], list)
    assert "total" in data
    assert "pages" in data

def test_get_blog_posts_with_filters(client, admin_token):
    """Test getting blog posts with filters"""
    # Test status filter (admin only)
    response = client.get(
        "/api/blog?status=draft",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    if data["total"] > 0:
        assert data["blog_posts"][0]["status"] == "draft"
    
    # Test tag filter
    # First get all posts to find a tag
    all_posts = client.get("/api/blog")
    all_data = json.loads(all_posts.data)
    
    if all_data["total"] > 0 and all_data["blog_posts"][0]["tags"]:
        tag = all_data["blog_posts"][0]["tags"][0]
        
        response = client.get(f"/api/blog?tag={tag}")
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if data["total"] > 0:
            assert tag in data["blog_posts"][0]["tags"]
    
    # Test featured filter
    response = client.get("/api/blog?featured=true")
    assert response.status_code == 200

def test_get_blog_post_by_id(client, admin_token):
    """Test getting a blog post by ID"""
    # First create a blog post
    post_data = {
        "title": "Test Blog Post",
        "content": "This is a test blog post content.",
        "summary": "Test summary",
        "status": "published",
        "tags": ["test", "api"]
    }
    
    create_response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    post_id = json.loads(create_response.data)["blog_post"]["id"]
    
    # Get the blog post
    response = client.get(f"/api/blog/{post_id}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["blog_post"]["title"] == "Test Blog Post"
    assert data["blog_post"]["content"] == "This is a test blog post content."
    
    # Test with non-existent ID
    response = client.get("/api/blog/non-existent-id")
    assert response.status_code == 404

def test_create_blog_post(client, admin_token, user_token):
    """Test creating a blog post"""
    post_data = {
        "title": "New Test Blog Post",
        "content": "This is a new test blog post content.",
        "summary": "New test summary",
        "status": "draft",
        "tags": ["new", "test"]
    }
    
    # Test with regular user (should fail)
    response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["blog_post"]["title"] == "New Test Blog Post"
    assert data["blog_post"]["status"] == "draft"
    assert "new" in data["blog_post"]["tags"]
    
    # Test with invalid data
    invalid_data = {
        "title": "",  # Empty title
        "content": "Invalid blog post"
    }
    
    response = client.post(
        "/api/blog",
        data=json.dumps(invalid_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400

def test_update_blog_post(client, admin_token, user_token):
    """Test updating a blog post"""
    # First create a blog post
    post_data = {
        "title": "Blog Post to Update",
        "content": "This blog post will be updated.",
        "summary": "Update test summary",
        "status": "draft",
        "tags": ["update", "test"]
    }
    
    create_response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    post_id = json.loads(create_response.data)["blog_post"]["id"]
    
    # Test with regular user (should fail)
    update_data = {
        "title": "Updated Blog Post",
        "status": "published"
    }
    
    response = client.put(
        f"/api/blog/{post_id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.put(
        f"/api/blog/{post_id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["blog_post"]["title"] == "Updated Blog Post"
    assert data["blog_post"]["status"] == "published"
    assert data["blog_post"]["content"] == "This blog post will be updated."  # Unchanged field

def test_delete_blog_post(client, admin_token, user_token):
    """Test deleting a blog post"""
    # First create a blog post
    post_data = {
        "title": "Blog Post to Delete",
        "content": "This blog post will be deleted.",
        "summary": "Delete test summary",
        "status": "draft",
        "tags": ["delete", "test"]
    }
    
    create_response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    post_id = json.loads(create_response.data)["blog_post"]["id"]
    
    # Test with regular user (should fail)
    response = client.delete(
        f"/api/blog/{post_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.delete(
        f"/api/blog/{post_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify blog post is deleted
    response = client.get(f"/api/blog/{post_id}")
    assert response.status_code == 404

def test_get_tags(client):
    """Test getting all blog post tags"""
    response = client.get("/api/blog/tags")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "tags" in data
    assert isinstance(data["tags"], list)