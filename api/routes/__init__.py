"""
Routes package initialization
"""
from flask import Blueprint
from api.routes.auth import auth_bp
from api.routes.users import users_bp
from api.routes.products import products_bp
from api.routes.orders import orders_bp
from api.routes.blog_posts import blog_posts_bp
from api.routes.weather import weather_bp
from api.routes.tasks import tasks_bp

def register_routes(app):
    """Register all API routes with the Flask application"""
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(blog_posts_bp, url_prefix="/api/blog")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")