"""
Tests for product management API endpoints
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
    assert "total" in data
    assert "pages" in data

def test_get_products_with_filters(client):
    """Test getting products with filters"""
    # Test category filter
    response = client.get("/api/products?category=Electronics")
    assert response.status_code == 200
    data = json.loads(response.data)
    
    if data["total"] > 0:
        assert data["products"][0]["category"] == "Electronics"
    
    # Test price range filter
    response = client.get("/api/products?min_price=50&max_price=200")
    assert response.status_code == 200
    data = json.loads(response.data)
    
    if data["total"] > 0:
        for product in data["products"]:
            assert product["price"] >= 50
            assert product["price"] <= 200
    
    # Test sorting
    response = client.get("/api/products?sort_by=price&sort_order=asc")
    assert response.status_code == 200
    data = json.loads(response.data)
    
    if len(data["products"]) > 1:
        assert data["products"][0]["price"] <= data["products"][1]["price"]

def test_get_product_by_id(client, admin_token):
    """Test getting a product by ID"""
    # First create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10,
        "category": "Test"
    }
    
    create_response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    product_id = json.loads(create_response.data)["product"]["id"]
    
    # Get the product
    response = client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["product"]["name"] == "Test Product"
    assert data["product"]["price"] == 99.99
    
    # Test with non-existent ID
    response = client.get("/api/products/non-existent-id")
    assert response.status_code == 404

def test_create_product(client, admin_token, user_token):
    """Test creating a product"""
    product_data = {
        "name": "New Test Product",
        "description": "This is a new test product",
        "price": 149.99,
        "stock": 20,
        "category": "Test"
    }
    
    # Test with regular user (should fail)
    response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["product"]["name"] == "New Test Product"
    assert data["product"]["price"] == 149.99
    
    # Test with invalid data
    invalid_data = {
        "name": "Invalid Product",
        "price": -10  # Invalid price
    }
    
    response = client.post(
        "/api/products",
        data=json.dumps(invalid_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400

def test_update_product(client, admin_token, user_token):
    """Test updating a product"""
    # First create a product
    product_data = {
        "name": "Product to Update",
        "description": "This product will be updated",
        "price": 79.99,
        "stock": 15,
        "category": "Test"
    }
    
    create_response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    product_id = json.loads(create_response.data)["product"]["id"]
    
    # Test with regular user (should fail)
    update_data = {
        "name": "Updated Product",
        "price": 89.99
    }
    
    response = client.put(
        f"/api/products/{product_id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.put(
        f"/api/products/{product_id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["product"]["name"] == "Updated Product"
    assert data["product"]["price"] == 89.99
    assert data["product"]["description"] == "This product will be updated"  # Unchanged field

def test_delete_product(client, admin_token, user_token):
    """Test deleting a product"""
    # First create a product
    product_data = {
        "name": "Product to Delete",
        "description": "This product will be deleted",
        "price": 59.99,
        "stock": 5,
        "category": "Test"
    }
    
    create_response = client.post(
        "/api/products",
        data=json.dumps(product_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    product_id = json.loads(create_response.data)["product"]["id"]
    
    # Test with regular user (should fail)
    response = client.delete(
        f"/api/products/{product_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
    
    # Test with admin user (should succeed)
    response = client.delete(
        f"/api/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify product is deleted
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 404

def test_get_categories(client):
    """Test getting all product categories"""
    response = client.get("/api/products/categories")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "categories" in data
    assert isinstance(data["categories"], list)