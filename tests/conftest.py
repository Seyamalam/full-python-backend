"""
Pytest configuration file
"""
import os
import tempfile
import uuid
import pytest
from flask_jwt_extended import create_access_token
from faker import Faker

from api import create_app
from api.extensions import db
from api.models import User

# Initialize Faker
fake = Faker()

# Create unique IDs for test users
TEST_ADMIN_ID = str(uuid.uuid4())
TEST_USER_ID = str(uuid.uuid4())

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app("testing")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["TESTING"] = True
    
    # Create the database and the database tables
    with app.app_context():
        db.create_all()
        
        # Create test users with unique random data
        admin_username = f"admin_{fake.user_name()}_{uuid.uuid4().hex[:8]}"
        admin_email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
        
        user_username = f"user_{fake.user_name()}_{uuid.uuid4().hex[:8]}"
        user_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        
        admin_user = User(
            id=TEST_ADMIN_ID,
            username=admin_username,
            email=admin_email,
            role="admin"
        )
        admin_user.password = "Admin123!"
        
        regular_user = User(
            id=TEST_USER_ID,
            username=user_username,
            email=user_email,
            role="user"
        )
        regular_user.password = "User123!"
        
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def admin_token(app):
    """Generate a valid admin token"""
    with app.app_context():
        # Use the predefined ID to get the admin user
        admin = User.query.get(TEST_ADMIN_ID)
        return create_access_token(identity=admin.id)

@pytest.fixture
def user_token(app):
    """Generate a valid user token"""
    with app.app_context():
        # Use the predefined ID to get the regular user
        user = User.query.get(TEST_USER_ID)
        return create_access_token(identity=user.id)