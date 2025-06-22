"""
API package initialization
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from api.config import config_by_name
from api.extensions import db, migrate, limiter
from api.models import User, Product, Order, BlogPost
from api.routes import register_routes

def create_app(config_name="development"):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app_config = config_by_name.get(config_name, "development")
    app.config.from_object(app_config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # Setup JWT
    jwt = JWTManager(app)
    
    # Register routes
    register_routes(app)
    
    # Setup Swagger documentation
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger = Swagger(app, config=swagger_config)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    @app.route("/health")
    def health_check():
        """Health check endpoint for the API"""
        return jsonify({"status": "healthy", "version": "1.0.0"})
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

