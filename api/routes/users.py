"""
User management routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from api.extensions import db, limiter
from api.models import User
from api.schemas import UserSchema
from api.utils.decorators import admin_required

users_bp = Blueprint("users", __name__)

@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_required
@limiter.limit("30 per minute")
def get_users():
    """
    Get all users (admin only)
    ---
    tags:
      - Users
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
        name: role
        schema:
          type: string
    responses:
      200:
        description: List of users
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)
        role = request.args.get("role")
        
        # Build query
        query = User.query
        if role:
            query = query.filter_by(role=role)
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Return paginated results
        return jsonify({
            "users": [user.to_dict() for user in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: User details
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not allowed to access this user
      404:
        description: User not found
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if current user is admin or the requested user
        current_user = User.query.get(current_user_id)
        if current_user.role != "admin" and current_user_id != user_id:
            return jsonify({"error": "Not authorized to access this user"}), 403
        
        # Return user details
        return jsonify({
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Update user by ID
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        schema:
          type: string
        required: true
      - in: body
        name: user
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            password:
              type: string
    responses:
      200:
        description: User updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not allowed to update this user
      404:
        description: User not found
      409:
        description: Username or email already exists
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if current user is admin or the requested user
        current_user = User.query.get(current_user_id)
        if current_user.role != "admin" and current_user_id != user_id:
            return jsonify({"error": "Not authorized to update this user"}), 403
        
        # Validate request data
        schema = UserSchema(partial=True)
        data = schema.load(request.json)
        
        # Check if username or email already exists
        if "username" in data and data["username"] != user.username:
            if User.query.filter_by(username=data["username"]).first():
                return jsonify({"error": "Username already exists"}), 409
        
        if "email" in data and data["email"] != user.email:
            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "Email already exists"}), 409
        
        # Update user fields
        for key, value in data.items():
            if key == "password":
                user.password = value
            else:
                setattr(user, key, value)
        
        # Save to database
        db.session.commit()
        
        # Return updated user
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Delete user by ID (admin only)
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: User deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: User not found
    """
    try:
        # Find user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        # Return success message
        return jsonify({
            "message": "User deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500