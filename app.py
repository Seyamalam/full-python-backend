"""
Main application entry point for Portfolio API
"""
from flask import Flask
from dotenv import load_dotenv
import os
from flask_migrate import Migrate

from api import create_app
from api.commands import register_commands
from api.extensions import db

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

# Register custom CLI commands
register_commands(app)

# Initialize Flask-Migrate with the app
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=os.environ.get("FLASK_ENV") == "development")