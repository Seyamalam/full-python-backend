# Advanced Flask Portfolio API

A comprehensive, production-ready Flask API project showcasing various backend development skills and best practices. This project is designed to be a portfolio piece demonstrating advanced API development capabilities.

## 🚀 Features

- **RESTful API Architecture**: Well-structured API endpoints following REST principles with GET, POST, PUT, DELETE methods
- **Authentication & Authorization**: JWT-based auth system with role-based access control
- **Database Integration**: SQLite for local development (easily configurable for other databases)
- **API Documentation**: Interactive Swagger documentation with Flasgger
- **Rate Limiting**: Prevent abuse with configurable rate limits using Flask-Limiter
- **Data Validation**: Schema-based validation using Marshmallow
- **Error Handling**: Comprehensive error handling and reporting
- **Cloudflare Workers Compatible**: Designed to be deployable to Cloudflare Workers
- **Testing Framework**: Pytest setup with fixtures and sample tests
- **Multiple API Types**: Demonstrates various API patterns and use cases
- **Database Seeding**: Faker integration for generating realistic test data
- **Custom CLI Commands**: Flask commands for database seeding, testing, and admin creation
- **Docker Support**: Containerization with Docker and docker-compose
- **CI/CD Pipeline**: GitHub Actions workflow for testing and deployment
- **Code Quality**: Linting with flake8 and formatting with black
- **Test Coverage**: Coverage reporting with pytest-cov

## 📋 API Modules

### 🔐 Authentication API
- User registration and login
- JWT token generation and refresh
- Password reset functionality
- Role-based authorization

### 👤 User Management API
- CRUD operations for user accounts
- Profile management
- Role management
- User search and filtering

### 🛒 E-commerce API
- Product catalog management
- Order processing
- Inventory tracking
- Product search and filtering

### 📝 Blog Content API
- Blog post management
- Content categorization with tags
- View tracking
- Content search

### ☁️ Weather API
- Current weather data (simulated)
- Weather forecasts
- City-based weather lookup

### ⚙️ Task Management API
- Background task processing
- Task status tracking
- Progress monitoring
- Task cancellation

## 🏗️ Project Structure

```
/
├── app.py                  # Application entry point
├── requirements.txt        # Project dependencies
├── .env.example            # Environment variable template
├── api/                    # API package
│   ├── __init__.py         # API initialization
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── blog_post.py
│   ├── routes/             # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── blog_posts.py
│   │   ├── weather.py
│   │   └── tasks.py
│   ├── schemas/            # Data validation schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── blog_post.py
│   └── utils/              # Utility functions
│       └── decorators.py
└── tests/                  # Test suite
    ├── conftest.py
    ├── test_auth.py
    ├── test_users.py
    └── ...
```

## 🛠️ Technologies Used

- **Flask**: Lightweight web framework
- **Flask-RESTful**: Extension for building REST APIs
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: JWT authentication
- **Flask-Migrate**: Database migrations
- **Flask-Limiter**: API rate limiting
- **Marshmallow**: Object serialization/deserialization
- **Flasgger**: Swagger documentation
- **SQLite**: Local database
- **pytest**: Testing framework
- **Faker**: Generating realistic test data
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline

## 🏗️ Project Structure

```
/
├── app.py                  # Application entry point
├── requirements.txt        # Project dependencies
├── .env.example            # Environment variable template
├── .env                    # Environment variables (not in version control)
├── setup.py                # Package setup script
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── wrangler.toml           # Cloudflare Workers configuration
├── run_tests.sh            # Test runner script for Unix/Mac
├── run_tests.bat           # Test runner script for Windows
├── .gitignore              # Git ignore file
├── api/                    # API package
│   ├── __init__.py         # API initialization
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions
│   ├── commands.py         # Custom CLI commands
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── blog_post.py
│   ├── routes/             # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── blog_posts.py
│   │   ├── weather.py
│   │   └── tasks.py
│   ├── schemas/            # Data validation schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── blog_post.py
│   └── utils/              # Utility functions
│       └── decorators.py
├── tests/                  # Test suite
│   ├── conftest.py         # Test configuration and fixtures
│   ├── test_auth.py        # Authentication tests
│   ├── test_users_api.py   # User management tests
│   ├── test_products_api.py # Product tests
│   ├── test_orders_api.py  # Order tests
│   ├── test_blog_posts_api.py # Blog post tests
│   ├── test_weather_api.py # Weather API tests
│   └── test_tasks_api.py   # Task management tests
└── .github/                # GitHub configuration
    └── workflows/          # GitHub Actions workflows
        └── main.yml        # CI/CD pipeline
```

## 🚦 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/flask-portfolio-api.git
cd flask-portfolio-api
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Seed the database with sample data
```bash
flask seed-db
```

6. Run the application
```bash
flask run
```

7. Access the API documentation
```
http://localhost:5000/docs/
```

### Custom Commands

The application includes several custom CLI commands:

- **Seed Database**: Populate the database with sample data
  ```bash
  flask seed-db --users 20 --products 100 --orders 50 --posts 30
  ```

- **Create Admin User**: Create a new admin user
  ```bash
  flask create-admin username admin@example.com
  ```

- **Run Tests**: Run the test suite
  ```bash
  flask run-tests
  flask run-tests --coverage  # Generate coverage report
  flask run-tests --verbose   # Verbose output
  ```

## 📊 API Documentation

The API is fully documented using Swagger. Once the application is running, you can access the interactive documentation at `/docs/`.

### Authentication

Most endpoints require authentication. To authenticate:

1. Register a new user at `/api/auth/register`
2. Login at `/api/auth/login` to get an access token
3. Include the token in the Authorization header: `Authorization: Bearer <token>`

## 🧪 Testing

The project includes comprehensive test suites for all API endpoints:

### Running Tests

1. **Run all tests at once:**
   ```bash
   flask run-tests
   ```

2. **Run tests with coverage:**
   ```bash
   flask run-tests --coverage
   ```

3. **Run specific test files:**
   ```bash
   python -m pytest tests/test_auth.py -v
   python -m pytest tests/test_products_api.py -v
   python -m pytest tests/test_blog_posts_api.py -v
   python -m pytest tests/test_orders_api.py -v
   python -m pytest tests/test_weather_api.py -v
   python -m pytest tests/test_tasks_api.py -v
   python -m pytest tests/test_users_api.py -v
   ```

4. **Run all tests using the provided scripts:**
   - On Windows:
     ```bash
     .\run_tests.bat
     ```
   - On Linux/Mac:
     ```bash
     chmod +x run_tests.sh
     ./run_tests.sh
     ```

### What These Tests Cover

1. **Authentication Tests**
   - User registration
   - User login
   - Token refresh
   - Getting current user info

2. **User Management Tests**
   - Getting all users (admin only)
   - Getting a specific user
   - Updating user information
   - Deleting users (admin only)

3. **Product Tests**
   - Getting all products with filters and sorting
   - Getting a specific product
   - Creating products (admin only)
   - Updating products (admin only)
   - Deleting products (admin only)
   - Getting product categories

4. **Order Tests**
   - Getting all orders (filtered by user for non-admins)
   - Getting a specific order
   - Creating orders

5. **Blog Post Tests**
   - Getting all blog posts with filters
   - Getting a specific blog post
   - Creating blog posts (admin only)
   - Updating blog posts (admin only)
   - Deleting blog posts (admin only)
   - Getting blog post tags

6. **Weather API Tests**
   - Getting current weather
   - Getting weather forecasts
   - Getting available cities

7. **Task Management Tests**
   - Creating background tasks
   - Getting all tasks
   - Getting a specific task
   - Cancelling tasks

## 🌩️ Deployment

### Cloudflare Workers

This API is designed to be compatible with Cloudflare Workers. To deploy:

1. Install Wrangler CLI
```bash
npm install -g @cloudflare/wrangler
```

2. Configure wrangler.toml
3. Deploy using Wrangler
```bash
wrangler publish
```

### Other Deployment Options

- **Heroku**: Use the Procfile included
- **Docker**: Dockerfile is provided
- **AWS/GCP/Azure**: Follow standard Python app deployment

## 🔄 CI/CD Pipeline

A GitHub Actions workflow is included for:
- Running tests
- Linting code
- Building and deploying to Cloudflare Workers

## 📝 Future Enhancements

- [ ] Add WebSocket support for real-time notifications
- [ ] Implement GraphQL API alongside REST
- [ ] Add OAuth2 authentication providers
- [ ] Create admin dashboard
- [ ] Implement caching layer
- [ ] Add file upload functionality
- [ ] Implement full-text search
- [ ] Add analytics tracking

## 🔧 API Testing Commands

Here are some curl commands to test the various API endpoints:

### Authentication API

**Register a new user:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" -d '{"username":"testuser", "email":"test@example.com", "password":"Test123!", "password_confirm":"Test123!"}'
```

**Login with the new user:**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"testuser", "password":"Test123!"}'
```

**Get current user info:**
```bash
curl -X GET http://127.0.0.1:5000/api/auth/me -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Products API

**Get all products:**
```bash
curl -X GET http://127.0.0.1:5000/api/products
```

**Get a specific product:**
```bash
curl -X GET http://127.0.0.1:5000/api/products/PRODUCT_ID
```

**Create a new product (admin only):**
```bash
curl -X POST http://127.0.0.1:5000/api/products -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -d '{"name":"Test Product", "description":"This is a test product", "price":99.99, "stock":10, "category":"Test"}'
```

### Blog Posts API

**Get all blog posts:**
```bash
curl -X GET http://127.0.0.1:5000/api/blog
```

**Get a specific blog post:**
```bash
curl -X GET http://127.0.0.1:5000/api/blog/POST_ID
```

**Create a new blog post (admin only):**
```bash
curl -X POST http://127.0.0.1:5000/api/blog -H "Content-Type: application/json" -H "Authorization: Bearer ADMIN_TOKEN" -d '{"title":"Test Blog Post", "content":"This is a test blog post content.", "summary":"Test summary", "tags":["test", "api"]}'
```

### Weather API

**Get current weather:**
```bash
curl -X GET "http://127.0.0.1:5000/api/weather/current?city=New%20York"
```

**Get weather forecast:**
```bash
curl -X GET "http://127.0.0.1:5000/api/weather/forecast?city=Chicago&days=3"
```

### Tasks API

**Create a new task:**
```bash
curl -X POST http://127.0.0.1:5000/api/tasks -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_ACCESS_TOKEN" -d '{"name":"Test Task", "description":"This is a test task", "duration":5}'
```

**Get all tasks:**
```bash
curl -X GET http://127.0.0.1:5000/api/tasks -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Your Name - [your.email@example.com](mailto:your.email@example.com)

---

⭐️ If you find this project useful, please consider giving it a star on GitHub!