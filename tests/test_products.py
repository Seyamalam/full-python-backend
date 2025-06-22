"""
Tests for product routes
"""
import json
import pytest

def test_get_products(client):
    """Test getting all products"""
    response = client.get("/api/products")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "products" in data
    assert isinstance(data["products"], list)

def test_create_product(client, admin_token, user_token):
    """Test creating a product"""
    # Test with admin token (should succeed)
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10,
        "category": "Test Category"
    }
    
    response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["product"]["name"] == "Test Product"
    assert data["product"]["price"] == 99.99
    
    # Test with user token (should fail)
    response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403

def test_get_product(client, admin_token):
    """Test getting a single product"""
    # First create a product
    product_data = {
        "name": "Single Test Product",
        "description": "This is a test product",
        "price": 49.99,
        "stock": 5,
        "category": "Test Category"
    }
    
    create_response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    product_id = json.loads(create_response.data)["product"]["id"]
    
    # Now get the product
    response = client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["product"]["name"] == "Single Test Product"
    assert data["product"]["price"] == 49.99
    
    # Test with non-existent ID
    response = client.get("/api/products/non-existent-id")
    assert response.status_code == 404