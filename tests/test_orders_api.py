"""
Tests for order management API endpoints
"""
import json
import pytest

def test_get_orders(client, admin_token, user_token):
    """Test getting all orders"""
    # Admin can see all orders
    admin_response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert admin_response.status_code == 200
    admin_data = json.loads(admin_response.data)
    assert "orders" in admin_data
    assert isinstance(admin_data["orders"], list)
    
    # User can only see their own orders
    user_response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert user_response.status_code == 200
    user_data = json.loads(user_response.data)
    assert "orders" in user_data
    
    # Admin should see more orders than a regular user
    if admin_data["total"] > 0 and user_data["total"] > 0:
        assert admin_data["total"] >= user_data["total"]

def test_get_orders_with_filters(client, admin_token):
    """Test getting orders with filters"""
    # Test status filter
    response = client.get(
        "/api/orders?status=pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    if data["total"] > 0:
        assert data["orders"][0]["status"] == "pending"

def test_get_order_by_id(client, admin_token, user_token):
    """Test getting an order by ID"""
    # First get all orders for admin
    admin_response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    admin_data = json.loads(admin_response.data)
    
    if admin_data["total"] > 0:
        order_id = admin_data["orders"][0]["id"]
        
        # Admin can get any order
        response = client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # User can only get their own orders
        user_response = client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        # Either 200 (if it's their order) or 403 (if not)
        assert user_response.status_code in [200, 403]
    
    # Test with non-existent ID
    response = client.get(
        "/api/orders/non-existent-id",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404

def test_create_order(client, user_token):
    """Test creating an order"""
    # First get some products
    products_response = client.get("/api/products")
    products_data = json.loads(products_response.data)
    
    if products_data["total"] > 0:
        product_id = products_data["products"][0]["id"]
        
        # Create order data
        order_data = {
            "shipping_address": "123 Test St, Test City, Test Country",
            "payment_method": "credit_card",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        }
        
        response = client.post(
            "/api/orders",
            data=json.dumps(order_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "order" in data
        assert data["order"]["shipping_address"] == "123 Test St, Test City, Test Country"
        assert data["order"]["payment_method"] == "credit_card"
        assert len(data["order"]["items"]) == 1
        
        # Test with invalid data
        invalid_data = {
            "shipping_address": "123 Test St",
            "payment_method": "invalid_method",  # Invalid payment method
            "items": []  # No items
        }
        
        response = client.post(
            "/api/orders",
            data=json.dumps(invalid_data),
            content_type="application/json",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 400