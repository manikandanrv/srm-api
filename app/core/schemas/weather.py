"""
Weather data schemas for IMD API integration.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    """Weather response model for API endpoints."""

    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., description="Relative humidity percentage")
    description: str = Field(..., description="Weather description in English")
    description_tamil: Optional[str] = Field(
        None, description="Weather description in Tamil"
    )
    wind_speed: Optional[float] = Field(None, description="Wind speed in km/h")
    wind_direction: Optional[str] = Field(None, description="Wind direction")
    rainfall: Optional[float] = Field(None, description="Rainfall in mm")
    location: str = Field(..., description="Location name")
    timestamp: datetime = Field(..., description="Data observation timestamp")
    cached: bool = Field(
        default=False, description="Whether data is from cache"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28.5,
                "humidity": 65,
                "description": "Partly cloudy",
                "description_tamil": "ஓரளவு மேகமூட்டம்",
                "wind_speed": 12.5,
                "wind_direction": "NE",
                "rainfall": 0.0,
                "location": "Tiruvannamalai",
                "timestamp": "2024-01-15T10:30:00",
                "cached": False,
            }
        }


class WeatherErrorResponse(BaseModel):
    """Weather error response when data is unavailable."""

    message: str
    location: str
    timestamp: datetime
    fallback: bool = True
