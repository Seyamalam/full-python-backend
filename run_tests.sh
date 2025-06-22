#!/bin/bash

# Run all tests
echo "Running all tests..."
flask run-tests

# Run specific test files
echo -e "\nRunning authentication tests..."
python -m pytest tests/test_auth.py -v

echo -e "\nRunning user management tests..."
python -m pytest tests/test_users_api.py -v

echo -e "\nRunning product tests..."
python -m pytest tests/test_products_api.py -v

echo -e "\nRunning order tests..."
python -m pytest tests/test_orders_api.py -v

echo -e "\nRunning blog post tests..."
python -m pytest tests/test_blog_posts_api.py -v

echo -e "\nRunning weather API tests..."
python -m pytest tests/test_weather_api.py -v

echo -e "\nRunning task management tests..."
python -m pytest tests/test_tasks_api.py -v

# Run tests with coverage
echo -e "\nRunning tests with coverage report..."
flask run-tests --coverage