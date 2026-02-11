"""
Weather API endpoints for IMD weather data.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.models.user import User
from app.core.schemas.weather import WeatherResponse
from app.core.services.auth import get_current_user
from app.core.services.weather import WeatherService

router = APIRouter()

# Global weather service instance
# In production, this could be managed via dependency injection
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService(cache_ttl_minutes=15)
    return _weather_service


@router.get("/tiruvannamalai", response_model=WeatherResponse)
async def get_tiruvannamalai_weather(
    current_user: Annotated[User, Depends(get_current_user)],
    weather_service: Annotated[WeatherService, Depends(get_weather_service)],
):
    """
    Get current weather for Tiruvannamalai.

    Returns weather data from IMD including:
    - Temperature (°C)
    - Humidity (%)
    - Weather description (English and Tamil)
    - Wind speed and direction
    - Rainfall

    Data is cached for 15 minutes to reduce API calls.
    Falls back to reasonable defaults if IMD API is unavailable.
    """
    try:
        weather_data = await weather_service.get_tiruvannamalai_weather()
        return WeatherResponse(**weather_data)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather service temporarily unavailable: {str(e)}",
        )


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    current_user: Annotated[User, Depends(get_current_user)],
    weather_service: Annotated[WeatherService, Depends(get_weather_service)],
    latitude: Optional[float] = Query(None, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, description="Longitude coordinate"),
):
    """
    Get current weather data.

    If latitude and longitude are provided, returns weather for that location.
    Otherwise, returns weather for Tiruvannamalai (default farm location).

    **Note**: Coordinate-based weather is planned for future implementation.
    Currently returns Tiruvannamalai data regardless of coordinates.
    """
    try:
        if latitude is not None and longitude is not None:
            weather_data = await weather_service.get_weather_by_coordinates(
                latitude, longitude
            )
        else:
            weather_data = await weather_service.get_tiruvannamalai_weather()

        return WeatherResponse(**weather_data)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather service temporarily unavailable: {str(e)}",
        )


@router.on_event("shutdown")
async def shutdown_weather_service():
    """Clean up weather service on shutdown."""
    global _weather_service
    if _weather_service:
        await _weather_service.close()
