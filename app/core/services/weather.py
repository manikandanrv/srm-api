"""
Weather service for fetching IMD weather data.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx
from dateutil import parser

logger = logging.getLogger(__name__)


class WeatherCache:
    """Simple in-memory cache for weather data."""

    def __init__(self, ttl_minutes: int = 15):
        self._cache: Dict[str, dict] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[dict]:
        """Get cached data if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._ttl:
                return data
            else:
                # Expired, remove from cache
                del self._cache[key]
        return None

    def set(self, key: str, data: dict) -> None:
        """Set cache data with current timestamp."""
        self._cache[key] = (data, datetime.now())

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


class WeatherService:
    """Service for fetching weather data from IMD API."""

    # IMD API base URL
    IMD_BASE_URL = "https://mausam.imd.gov.in/api"
    
    # Default station/district ID for Tiruvannamalai
    # Note: This needs to be obtained from IMD's API documentation PDF
    # For now using a placeholder - update with actual ID from IMD docs
    TIRUVANNAMALAI_STATION_ID = "43279"  # Placeholder - needs verification
    
    # Tamil translations for common weather conditions
    WEATHER_TRANSLATIONS = {
        "clear sky": "தெளிவான வானம்",
        "partly cloudy": "ஓரளவு மேகமூட்டம்",
        "cloudy": "மேகமூட்டம்",
        "overcast": "முழு மேகமூட்டம்",
        "light rain": "லேசான மழை",
        "moderate rain": "மிதமான மழை",
        "heavy rain": "கனமழை",
        "thunderstorm": "இடி மின்னல் மழை",
        "fog": "மூடுபனி",
        "mist": "இலேசான மூடுபனி",
        "haze": "மங்கலான",
        "smoke": "புகை",
        "dust": "தூசி",
        "sand": "மணல்",
        "hot": "வெப்பம்",
        "warm": "வெதுவெதுப்பு",
        "cool": "குளிர்ச்சி",
        "cold": "குளிர்",
    }

    def __init__(self, cache_ttl_minutes: int = 15):
        self._cache = WeatherCache(ttl_minutes=cache_ttl_minutes)
        self._http_client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Close HTTP client."""
        await self._http_client.aclose()

    def _translate_to_tamil(self, description: str) -> str:
        """Translate weather description to Tamil."""
        description_lower = description.lower()
        for english, tamil in self.WEATHER_TRANSLATIONS.items():
            if english in description_lower:
                return tamil
        return description  # Return original if no translation found

    async def get_tiruvannamalai_weather(self) -> dict:
        """
        Get current weather for Tiruvannamalai.
        
        Returns weather data with caching support.
        Falls back to mock data if IMD API is unavailable.
        """
        cache_key = "tiruvannamalai"
        
        # Check cache first
        cached_data = self._cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached weather data for Tiruvannamalai")
            cached_data["cached"] = True
            return cached_data

        try:
            # Attempt to fetch from IMD API
            weather_data = await self._fetch_from_imd(self.TIRUVANNAMALAI_STATION_ID)
            
            # Cache the result
            self._cache.set(cache_key, weather_data)
            weather_data["cached"] = False
            
            logger.info("Successfully fetched weather data from IMD for Tiruvannamalai")
            return weather_data
            
        except Exception as e:
            logger.warning(f"Failed to fetch weather from IMD: {e}")
            # Return fallback data
            return self._get_fallback_data("Tiruvannamalai")

    async def _fetch_from_imd(self, station_id: str) -> dict:
        """
        Fetch weather data from IMD API.
        
        Args:
            station_id: IMD station ID
            
        Returns:
            Parsed weather data
            
        Raises:
            Exception: If API request fails
        """
        url = f"{self.IMD_BASE_URL}/current_wx_api.php"
        params = {"id": station_id}
        
        logger.info(f"Fetching weather from IMD for station {station_id}")
        
        response = await self._http_client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse IMD response
        # Note: The exact field names depend on IMD's actual response format
        # This is based on common weather API patterns
        return self._parse_imd_response(data)

    def _parse_imd_response(self, data: dict) -> dict:
        """
        Parse IMD API response into standardized format.
        
        Args:
            data: Raw IMD API response
            
        Returns:
            Standardized weather data dictionary
        """
        # Get description and translate
        description = data.get("wth_desc", data.get("weather", "Clear sky"))
        description_tamil = self._translate_to_tamil(description)
        
        # Parse timestamp
        timestamp_str = data.get("observ_time", data.get("timestamp"))
        if timestamp_str:
            try:
                timestamp = parser.parse(timestamp_str)
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        return {
            "temperature": float(data.get("temp", data.get("temperature", 28.0))),
            "humidity": int(data.get("rh", data.get("humidity", 60))),
            "description": description,
            "description_tamil": description_tamil,
            "wind_speed": float(data.get("ws", data.get("wind_speed", 0.0))),
            "wind_direction": data.get("wd", data.get("wind_direction", "N")),
            "rainfall": float(data.get("rf", data.get("rainfall", 0.0))),
            "location": "Tiruvannamalai",
            "timestamp": timestamp,
        }

    def _get_fallback_data(self, location: str) -> dict:
        """
        Get fallback weather data when API is unavailable.
        
        Args:
            location: Location name
            
        Returns:
            Fallback weather data with reasonable defaults for Tiruvannamalai
        """
        logger.info(f"Using fallback weather data for {location}")
        
        return {
            "temperature": 28.0,
            "humidity": 65,
            "description": "Weather data temporarily unavailable",
            "description_tamil": "வானிலை தகவல் தற்காலிகமாக கிடைக்கவில்லை",
            "wind_speed": 10.0,
            "wind_direction": "NE",
            "rainfall": 0.0,
            "location": location,
            "timestamp": datetime.now(),
            "cached": False,
        }

    async def get_weather_by_coordinates(
        self, latitude: float, longitude: float
    ) -> dict:
        """
        Get weather data by latitude and longitude.
        
        Note: This would require geocoding to find the nearest IMD station.
        For now, returns Tiruvannamalai data as fallback.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Weather data
        """
        # For future implementation: map coordinates to nearest IMD station
        # For now, return Tiruvannamalai data
        logger.info(
            f"Coordinate-based weather requested ({latitude}, {longitude}), "
            "returning Tiruvannamalai data"
        )
        return await self.get_tiruvannamalai_weather()
