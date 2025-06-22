"""
Product management routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from api.extensions import db, limiter
from api.models import Product
from api.schemas import ProductSchema
from api.utils.decorators import admin_required

products_bp = Blueprint("products", __name__)

@products_bp.route("", methods=["GET"])
@limiter.limit("60 per minute")
def get_products():
    """
    Get all products
    ---
    tags:
      - Products
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
        name: category
        schema:
          type: string
      - in: query
        name: min_price
        schema:
          type: number
      - in: query
        name: max_price
        schema:
          type: number
      - in: query
        name: sort_by
        schema:
          type: string
          enum: [name, price, created_at]
      - in: query
        name: sort_order
        schema:
          type: string
          enum: [asc, desc]
    responses:
      200:
        description: List of products
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)
        category = request.args.get("category")
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Apply sorting
        if sort_by == "name":
            query = query.order_by(Product.name.asc() if sort_order == "asc" else Product.name.desc())
        elif sort_by == "price":
            query = query.order_by(Product.price.asc() if sort_order == "asc" else Product.price.desc())
        else:  # default: created_at
            query = query.order_by(Product.created_at.asc() if sort_order == "asc" else Product.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Return paginated results
        return jsonify({
            "products": [product.to_dict() for product in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    """
    Get product by ID
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Product details
      404:
        description: Product not found
    """
    try:
        # Find product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Check if product is active
        if not product.is_active:
            return jsonify({"error": "Product not available"}), 404
        
        # Return product details
        return jsonify({
            "product": product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_product():
    """
    Create a new product (admin only)
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: product
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            category:
              type: string
            image_url:
              type: string
            is_active:
              type: boolean
    responses:
      201:
        description: Product created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    try:
        # Validate request data
        schema = ProductSchema()
        data = schema.load(request.json)
        
        # Create new product
        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            stock=data.get("stock", 0),
            category=data.get("category"),
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True)
        )
        
        # Save to database
        db.session.add(product)
        db.session.commit()
        
        # Return created product
        return jsonify({
            "message": "Product created successfully",
            "product": product.to_dict()
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@products_bp.route("/<product_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_product(product_id):
    """
    Update product by ID (admin only)
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: product_id
        schema:
          type: string
        required: true
      - in: body
        name: product
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            category:
              type: string
            image_url:
              type: string
            is_active:
              type: boolean
    responses:
      200:
        description: Product updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Product not found
    """
    try:
        # Find product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Validate request data
        schema = ProductSchema(partial=True)
        data = schema.load(request.json)
        
        # Update product fields
        for key, value in data.items():
            setattr(product, key, value)
        
        # Save to database
        db.session.commit()
        
        # Return updated product
        return jsonify({
            "message": "Product updated successfully",
            "product": product.to_dict()
        }), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@products_bp.route("/<product_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_product(product_id):
    """
    Delete product by ID (admin only)
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: product_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Product deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Product not found
    """
    try:
        # Find product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Delete product
        db.session.delete(product)
        db.session.commit()
        
        # Return success message
        return jsonify({
            "message": "Product deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@products_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Get all product categories
    ---
    tags:
      - Products
    responses:
      200:
        description: List of product categories
    """
    try:
        # Get distinct categories
        categories = db.session.query(Product.category).distinct().filter(
            Product.category.isnot(None),
            Product.is_active.is_(True)
        ).all()
        
        # Extract category names
        category_list = [category[0] for category in categories if category[0]]
        
        # Return categories
        return jsonify({
            "categories": category_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500