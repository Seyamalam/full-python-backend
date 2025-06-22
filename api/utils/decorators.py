"""
Custom decorators for the API
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from api.models import User

def admin_required(fn):
    """
    Decorator to check if the current user is an admin
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Get current user identity
        current_user_id = get_jwt_identity()
        
        # Find user by ID
        user = User.query.get(current_user_id)
        
        # Check if user is admin
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        
        # Call the original function
        return fn(*args, **kwargs)
    
    return wrapper