"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from marshmallow import ValidationError

from api.extensions import db
from api.models import User
from api.schemas import UserLoginSchema, UserRegisterSchema

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: user
        schema:
          type: object
          required:
            - username
            - email
            - password
            - password_confirm
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            password_confirm:
              type: string
            first_name:
              type: string
            last_name:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Validation error
      409:
        description: User already exists
    """
    try:
        # Validate request data
        schema = UserRegisterSchema()
        data = schema.load(request.json)
        
        # Check if user already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "Username already exists"}), 409
        
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 409
        
        # Create new user
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )
        user.password = data["password"]
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
          required:
            - password
    responses:
      200:
        description: Login successful
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    try:
        # Validate request data
        schema = UserLoginSchema()
        data = schema.load(request.json)
        
        # Find user by username or email
        user = None
        if "username" in data:
            user = User.query.filter_by(username=data["username"]).first()
        elif "email" in data:
            user = User.query.filter_by(email=data["email"]).first()
        
        # Check if user exists and password is correct
        if not user or not user.verify_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({"error": "Account is disabled"}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "Login successful",
            "user": UserLoginSchema().dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: Token refreshed successfully
      401:
        description: Invalid token
    """
    try:
        # Get user identity from refresh token
        current_user_id = get_jwt_identity()
        
        # Generate new access token
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            "message": "Token refreshed successfully",
            "access_token": access_token
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    """
    Get current user information
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      200:
        description: User information retrieved successfully
      401:
        description: Invalid token
      404:
        description: User not found
    """
    try:
        # Get user identity from access token
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Return user information
        return jsonify({
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500