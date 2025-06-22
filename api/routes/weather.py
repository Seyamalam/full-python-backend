"""
Weather API routes - simulated weather data for demonstration
"""
from flask import Blueprint, request, jsonify
import datetime
import random
import math

from api.extensions import limiter

weather_bp = Blueprint("weather", __name__)

# Simulated weather data
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "San Francisco", "Columbus", "Indianapolis", "Seattle", "Denver", "Boston"
]

WEATHER_CONDITIONS = [
    "Clear", "Partly Cloudy", "Cloudy", "Overcast", 
    "Light Rain", "Rain", "Heavy Rain", "Thunderstorm",
    "Light Snow", "Snow", "Heavy Snow", "Fog", "Mist"
]

def get_simulated_weather(city, date=None):
    """Generate simulated weather data for a city"""
    # Use city name as seed for consistent but different data per city
    seed = sum(ord(c) for c in city)
    if date:
        # Add date to seed for different data per day
        seed += date.day + date.month * 100 + date.year * 10000
    
    random.seed(seed)
    
    # Generate temperature based on season (Northern Hemisphere)
    if date:
        month = date.month
        # Summer (June-August)
        if 6 <= month <= 8:
            temp_base = 25  # Celsius
            temp_range = 10
        # Winter (December-February)
        elif month == 12 or month <= 2:
            temp_base = 5
            temp_range = 10
        # Spring/Fall
        else:
            temp_base = 15
            temp_range = 15
    else:
        # Default if no date provided
        temp_base = 20
        temp_range = 15
    
    # Adjust base temperature by city (rough approximation)
    if "Los Angeles" in city or "San Diego" in city or "Phoenix" in city:
        temp_base += 5
    elif "Chicago" in city or "Boston" in city or "Denver" in city:
        temp_base -= 5
    
    # Generate weather data
    temp = round(temp_base + (random.random() * 2 - 1) * temp_range, 1)
    condition_idx = random.randint(0, len(WEATHER_CONDITIONS) - 1)
    condition = WEATHER_CONDITIONS[condition_idx]
    
    # Humidity based on condition
    if "Rain" in condition or "Snow" in condition:
        humidity = random.randint(70, 95)
    elif "Clear" in condition:
        humidity = random.randint(30, 60)
    else:
        humidity = random.randint(40, 80)
    
    # Wind speed
    wind_speed = round(random.random() * 30, 1)
    
    # Precipitation probability based on condition
    if "Heavy" in condition and ("Rain" in condition or "Snow" in condition):
        precipitation = random.randint(70, 100)
    elif "Rain" in condition or "Snow" in condition:
        precipitation = random.randint(40, 80)
    elif "Cloudy" in condition or "Overcast" in condition:
        precipitation = random.randint(20, 50)
    else:
        precipitation = random.randint(0, 20)
    
    return {
        "city": city,
        "date": date.strftime("%Y-%m-%d") if date else datetime.datetime.now().strftime("%Y-%m-%d"),
        "temperature": temp,
        "condition": condition,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "precipitation": precipitation
    }

@weather_bp.route("/current", methods=["GET"])
@limiter.limit("30 per minute")
def get_current_weather():
    """
    Get current weather for a city
    ---
    tags:
      - Weather
    parameters:
      - in: query
        name: city
        schema:
          type: string
        required: true
        description: City name
    responses:
      200:
        description: Current weather data
      400:
        description: Invalid city
    """
    try:
        # Get city from query parameters
        city = request.args.get("city")
        if not city:
            return jsonify({"error": "City parameter is required"}), 400
        
        # Check if city is supported
        city_match = next((c for c in CITIES if city.lower() in c.lower()), None)
        if not city_match:
            return jsonify({
                "error": "City not found",
                "available_cities": CITIES
            }), 400
        
        # Get current weather
        weather = get_simulated_weather(city_match)
        
        # Return weather data
        return jsonify({
            "weather": weather
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@weather_bp.route("/forecast", methods=["GET"])
@limiter.limit("20 per minute")
def get_weather_forecast():
    """
    Get weather forecast for a city
    ---
    tags:
      - Weather
    parameters:
      - in: query
        name: city
        schema:
          type: string
        required: true
        description: City name
      - in: query
        name: days
        schema:
          type: integer
          default: 5
        description: Number of days to forecast (max 10)
    responses:
      200:
        description: Weather forecast data
      400:
        description: Invalid city or days parameter
    """
    try:
        # Get query parameters
        city = request.args.get("city")
        days = min(request.args.get("days", 5, type=int), 10)
        
        if not city:
            return jsonify({"error": "City parameter is required"}), 400
        
        # Check if city is supported
        city_match = next((c for c in CITIES if city.lower() in c.lower()), None)
        if not city_match:
            return jsonify({
                "error": "City not found",
                "available_cities": CITIES
            }), 400
        
        # Generate forecast for each day
        forecast = []
        today = datetime.datetime.now()
        
        for i in range(days):
            date = today + datetime.timedelta(days=i)
            weather = get_simulated_weather(city_match, date)
            forecast.append(weather)
        
        # Return forecast data
        return jsonify({
            "city": city_match,
            "forecast": forecast
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@weather_bp.route("/cities", methods=["GET"])
def get_available_cities():
    """
    Get available cities for weather data
    ---
    tags:
      - Weather
    responses:
      200:
        description: List of available cities
    """
    try:
        return jsonify({
            "cities": CITIES
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500