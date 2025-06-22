"""
Tests for weather API endpoints
"""
import json
import pytest

def test_get_current_weather(client):
    """Test getting current weather"""
    # Test with valid city
    response = client.get("/api/weather/current?city=New York")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "weather" in data
    assert data["weather"]["city"] == "New York"
    assert "temperature" in data["weather"]
    assert "condition" in data["weather"]
    assert "humidity" in data["weather"]
    assert "wind_speed" in data["weather"]
    assert "precipitation" in data["weather"]
    
    # Test with invalid city
    response = client.get("/api/weather/current?city=NonExistentCity")
    assert response.status_code == 400
    
    # Test without city parameter
    response = client.get("/api/weather/current")
    assert response.status_code == 400

def test_get_weather_forecast(client):
    """Test getting weather forecast"""
    # Test with valid city and default days
    response = client.get("/api/weather/forecast?city=Chicago")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "city" in data
    assert data["city"] == "Chicago"
    assert "forecast" in data
    assert len(data["forecast"]) == 5  # Default is 5 days
    
    # Test with custom days
    response = client.get("/api/weather/forecast?city=Chicago&days=3")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["forecast"]) == 3
    
    # Test with invalid city
    response = client.get("/api/weather/forecast?city=NonExistentCity")
    assert response.status_code == 400
    
    # Test without city parameter
    response = client.get("/api/weather/forecast")
    assert response.status_code == 400
    
    # Test with invalid days parameter
    response = client.get("/api/weather/forecast?city=Chicago&days=invalid")
    assert response.status_code == 200  # Should use default days
    data = json.loads(response.data)
    assert len(data["forecast"]) == 5

def test_get_available_cities(client):
    """Test getting available cities"""
    response = client.get("/api/weather/cities")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "cities" in data
    assert isinstance(data["cities"], list)
    assert len(data["cities"]) > 0
    assert "New York" in data["cities"]