"""
Order management routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from api.extensions import db
from api.models import Order, OrderItem, Product, User
from api.schemas import OrderSchema
from api.utils.decorators import admin_required

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders for current user (or all orders for admin)
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: page
        schema:
          type: integer
          default: 1
      - in: query
        name: per_page
        schema:
          type: integer
          default: 10
      - in: query
        name: status
        schema:
          type: string
    responses:
      200:
        description: List of orders
      401:
        description: Unauthorized
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)
        status = request.args.get("status")
        
        # Build query
        query = Order.query
        
        # Filter by user if not admin
        if current_user.role != "admin":
            query = query.filter_by(user_id=current_user_id)
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        # Order by created_at desc
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Return paginated results
        return jsonify({
            "orders": [order.to_dict() for order in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/<order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """
    Get order by ID
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: order_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Order details
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not allowed to access this order
      404:
        description: Order not found
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Find order by ID
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check if current user is admin or the order owner
        if current_user.role != "admin" and current_user_id != order.user_id:
            return jsonify({"error": "Not authorized to access this order"}), 403
        
        # Return order details
        return jsonify({
            "order": order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: order
        schema:
          type: object
          required:
            - shipping_address
            - payment_method
            - items
          properties:
            shipping_address:
              type: string
            payment_method:
              type: string
              enum: [credit_card, paypal, bank_transfer]
            items:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - quantity
                properties:
                  product_id:
                    type: string
                  quantity:
                    type: integer
    responses:
      201:
        description: Order created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      404:
        description: Product not found
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        
        # Validate request data
        schema = OrderSchema()
        data = schema.load(request.json)
        
        # Calculate total amount and check product availability
        total_amount = 0
        order_items = []
        
        for item_data in data["items"]:
            # Find product
            product = Product.query.get(item_data["product_id"])
            if not product:
                return jsonify({"error": f"Product with ID {item_data['product_id']} not found"}), 404
            
            # Check if product is active
            if not product.is_active:
                return jsonify({"error": f"Product {product.name} is not available"}), 400
            
            # Check stock
            if product.stock < item_data["quantity"]:
                return jsonify({"error": f"Not enough stock for {product.name}"}), 400
            
            # Calculate item price
            item_price = product.price * item_data["quantity"]
            total_amount += item_price
            
            # Create order item
            order_item = OrderItem(
                product_id=product.id,
                quantity=item_data["quantity"],
                price=product.price
            )
            
            order_items.append(order_item)
            
            # Update product stock
            product.stock -= item_data["quantity"]
        
        # Create order
        order = Order(
            user_id=current_user_id,
            status="pending",
            total_amount=total_amount,
            shipping_address=data["shipping_address"],
            payment_method=data["payment_method"],
            payment_status="unpaid"
        )
        
        # Add order items to order
        order.items = order_items
        
        # Save to database
        db.session.add(order)
        db.session.commit()
        
        # Return created order
        return jsonify({
            "message": "Order created successfully",
            "order": order.to_dict()
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/<order_id>/status", methods=["PUT"])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """
    Update order status (admin only)
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: order_id
        schema:
          type: string
        required: true
      - in: body
        name: status
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [pending, processing, completed, cancelled]
    responses:
      200:
        description: Order status updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Order not found
    """
    try:
        # Find order by ID
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Get status from request
        status = request.json.get("status")
        if not status:
            return jsonify({"error": "Status is required"}), 400
        
        # Validate status
        valid_statuses = ["pending", "processing", "completed", "cancelled"]
        if status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Handle cancellation
        if status == "cancelled" and order.status != "cancelled":
            # Restore product stock
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock += item.quantity
        
        # Update order status
        order.status = status
        
        # Save to database
        db.session.commit()
        
        # Return updated order
        return jsonify({
            "message": "Order status updated successfully",
            "order": order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/<order_id>/payment", methods=["PUT"])
@jwt_required()
@admin_required
def update_payment_status(order_id):
    """
    Update order payment status (admin only)
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: order_id
        schema:
          type: string
        required: true
      - in: body
        name: payment_status
        schema:
          type: object
          required:
            - payment_status
          properties:
            payment_status:
              type: string
              enum: [unpaid, paid, refunded]
    responses:
      200:
        description: Payment status updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Order not found
    """
    try:
        # Find order by ID
        order = Order.query.get(order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Get payment status from request
        payment_status = request.json.get("payment_status")
        if not payment_status:
            return jsonify({"error": "Payment status is required"}), 400
        
        # Validate payment status
        valid_statuses = ["unpaid", "paid", "refunded"]
        if payment_status not in valid_statuses:
            return jsonify({"error": f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        # Update payment status
        order.payment_status = payment_status
        
        # Save to database
        db.session.commit()
        
        # Return updated order
        return jsonify({
            "message": "Payment status updated successfully",
            "order": order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500