@echo off

REM Run all tests
echo Running all tests...
flask run-tests

REM Run specific test files
echo.
echo Running authentication tests...
python -m pytest tests/test_auth.py -v

echo.
echo Running user management tests...
python -m pytest tests/test_users_api.py -v

echo.
echo Running product tests...
python -m pytest tests/test_products_api.py -v

echo.
echo Running order tests...
python -m pytest tests/test_orders_api.py -v

echo.
echo Running blog post tests...
python -m pytest tests/test_blog_posts_api.py -v

echo.
echo Running weather API tests...
python -m pytest tests/test_weather_api.py -v

echo.
echo Running task management tests...
python -m pytest tests/test_tasks_api.py -v

REM Run tests with coverage
echo.
echo Running tests with coverage report...
flask run-tests --coverage