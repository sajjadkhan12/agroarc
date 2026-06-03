"""
Weather Advisory API Routes
Provides weather data and farming advisories using OpenWeatherMap API
"""

from fastapi import APIRouter, HTTPException, status, Query
import httpx
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Get OpenWeather API key from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# OpenWeather API base URL
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/weather",
    tags=["Weather Advisory"]
)


def generate_farming_advisory(temp: float, humidity: float, wind_speed: float, rain: float) -> str:
    """
    Generate rule-based farming advisory based on weather conditions
    
    Args:
        temp: Temperature in Celsius
        humidity: Humidity percentage (0-100)
        wind_speed: Wind speed in m/s
        rain: Rainfall in mm (0 if no rain)
    
    Returns:
        Advisory message with farming recommendations
    
    Rules:
    - Rain > 0: Postpone irrigation and spraying
    - Temp > 35°C: High heat stress, ensure adequate irrigation
    - Temp < 10°C: Risk of frost damage, protect sensitive crops
    - Humidity > 80%: High disease risk, monitor for fungal infections
    - Wind speed > 10 m/s: Avoid spraying, risk of crop damage
    - Optimal conditions: Good for farming activities
    """
    
    advisories = []
    
    # Check for rain - affects irrigation and spraying
    if rain > 0:
        advisories.append(f"⚠️ Rain detected ({rain:.1f}mm). Postpone irrigation and chemical spraying.")
    
    # Check temperature extremes
    if temp > 35:
        advisories.append(f"🌡️ High temperature ({temp:.1f}°C). Heat stress alert! Ensure adequate irrigation and shade for sensitive crops.")
    elif temp < 10:
        advisories.append(f"❄️ Low temperature ({temp:.1f}°C). Frost risk! Protect sensitive crops and delay planting.")
    elif temp >= 25 and temp <= 30:
        advisories.append(f"✅ Optimal temperature ({temp:.1f}°C) for most crops.")
    
    # Check humidity levels - affects disease pressure
    if humidity > 80:
        advisories.append(f"💧 High humidity ({humidity:.1f}%). Increased risk of fungal diseases. Monitor crops closely.")
    elif humidity < 30:
        advisories.append(f"🌵 Low humidity ({humidity:.1f}%). Increase irrigation frequency to prevent moisture stress.")
    
    # Check wind speed - affects spraying and crop damage
    if wind_speed > 10:
        advisories.append(f"💨 Strong winds ({wind_speed:.1f} m/s). Avoid spraying operations. Risk of mechanical damage to crops.")
    elif wind_speed > 5:
        advisories.append(f"🌬️ Moderate winds ({wind_speed:.1f} m/s). Exercise caution during spraying.")
    
    # If no specific warnings, provide general advice
    if not advisories:
        advisories.append("✅ Weather conditions are favorable for general farming activities.")
    
    # Combine all advisories into a single message
    return " ".join(advisories)


@router.get(
    "/weather-advice",
    summary="Get weather advisory for farming",
    description="Fetch current weather data and receive farming advisories based on conditions"
)
async def get_weather_advice(
    city: str = Query(..., description="City name (e.g., 'Lahore', 'Karachi', 'Islamabad')")
) -> dict:
    """
    Get weather data and farming advisory for a specified city
    
    Endpoint: GET /api/v1/weather/weather-advice?city=CityName
    
    Query Parameters:
    - city: Name of the city (required)
    
    Returns:
    - city: City name
    - country: Country code
    - temperature: Current temperature in Celsius
    - humidity: Humidity percentage
    - wind_speed: Wind speed in m/s
    - rainfall: Rainfall in mm (last 1 hour, 0 if no rain)
    - weather_description: General weather description
    - advisory: Farming recommendations based on weather
    
    Process:
    1. Validate API key is configured
    2. Call OpenWeatherMap API with city name
    3. Extract weather parameters (temp, humidity, wind, rain)
    4. Generate rule-based farming advisory
    5. Return structured response with data and advisory
    
    Error Handling:
    - 500: API key not configured
    - 404: City not found
    - 503: OpenWeatherMap API failure
    """
    
    # Step 1: Check if API key is configured
    if not OPENWEATHER_API_KEY:
        logger.error("OpenWeather API key not configured in .env file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Weather service not configured. API key missing in environment variables."
        )
    
    # Step 2: Prepare API request parameters
    params = {
        "q": city,  # City name query
        "appid": OPENWEATHER_API_KEY,  # API authentication key
        "units": "metric"  # Use Celsius for temperature, m/s for wind
    }
    
    try:
        # Step 3: Make HTTP request to OpenWeatherMap API
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Fetching weather data for city: {city}")
            response = await client.get(OPENWEATHER_BASE_URL, params=params)
            
            # Step 4: Handle API response errors
            if response.status_code == 404:
                logger.warning(f"City not found: {city}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"City '{city}' not found. Please check the city name and try again."
                )
            
            # Check for other API errors
            if response.status_code != 200:
                logger.error(f"OpenWeather API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Weather service unavailable. API returned status {response.status_code}"
                )
            
            # Step 5: Parse JSON response
            data = response.json()
        
        # Step 6: Extract weather parameters from API response
        # Temperature in Celsius
        temperature = data["main"]["temp"]
        
        # Humidity percentage
        humidity = data["main"]["humidity"]
        
        # Wind speed in m/s
        wind_speed = data["wind"]["speed"]
        
        # Rainfall in mm (last 1 hour) - default to 0 if no rain data
        # OpenWeather only includes 'rain' key if it's currently raining
        rainfall = data.get("rain", {}).get("1h", 0.0)
        
        # General weather description (e.g., "light rain", "clear sky")
        weather_description = data["weather"][0]["description"] if data.get("weather") else "N/A"
        
        # Country code (e.g., "PK" for Pakistan)
        country = data["sys"].get("country", "N/A")
        
        logger.debug(f"Weather data - Temp: {temperature}°C, Humidity: {humidity}%, "
                    f"Wind: {wind_speed} m/s, Rain: {rainfall}mm")
        
        # Step 7: Generate farming advisory based on weather conditions
        advisory = generate_farming_advisory(
            temp=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            rain=rainfall
        )
        
        # Step 8: Return structured response
        return {
            "city": city,
            "country": country,
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "wind_speed": round(wind_speed, 1),
            "rainfall": round(rainfall, 1),
            "weather_description": weather_description,
            "advisory": advisory
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise
    
    except httpx.TimeoutException:
        # Handle request timeout
        logger.error(f"Request timeout while fetching weather for {city}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Weather service request timed out. Please try again."
        )
    
    except httpx.RequestError as e:
        # Handle network/connection errors
        logger.error(f"Network error while fetching weather: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to weather service: {str(e)}"
        )
    
    except KeyError as e:
        # Handle unexpected API response structure
        logger.error(f"Unexpected API response structure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse weather data: missing field {str(e)}"
        )
    
    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error in weather advisory: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather advisory failed: {str(e)}"
        )


# Health check endpoint for weather service
@router.get(
    "/health",
    summary="Health check",
    description="Check if weather service is operational"
)
async def weather_health() -> dict:
    """
    Health check for weather advisory service
    
    Endpoint: GET /api/v1/weather/health
    
    Returns:
    - status: 'healthy' if API key is configured, 'unhealthy' otherwise
    - api_configured: Boolean indicating if OpenWeather API key is set
    """
    
    # Check if API key is configured
    api_configured = bool(OPENWEATHER_API_KEY)
    status_msg = "healthy" if api_configured else "unhealthy"
    
    return {
        "status": status_msg,
        "api_configured": api_configured,
        "service": "weather_advisory"
    }
