"""
Tests for blog post routes
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

def test_create_blog_post(client, admin_token, user_token):
    """Test creating a blog post"""
    # Test with admin token (should succeed)
    post_data = {
        "title": "Test Blog Post",
        "content": "This is a test blog post content.",
        "summary": "Test summary",
        "tags": ["test", "api"]
    }
    
    response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["blog_post"]["title"] == "Test Blog Post"
    assert "test-blog-post" in data["blog_post"]["slug"]
    
    # Test with user token (should fail)
    response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403

def test_get_blog_post(client, admin_token):
    """Test getting a single blog post"""
    # First create a blog post
    post_data = {
        "title": "Single Test Blog Post",
        "content": "This is a test blog post content for single retrieval.",
        "summary": "Test summary for single post",
        "status": "published"
    }
    
    create_response = client.post(
        "/api/blog",
        data=json.dumps(post_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    post_id = json.loads(create_response.data)["blog_post"]["id"]
    
    # Now get the blog post
    response = client.get(f"/api/blog/{post_id}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["blog_post"]["title"] == "Single Test Blog Post"
    
    # Test with non-existent ID
    response = client.get("/api/blog/non-existent-id")
    assert response.status_code == 404