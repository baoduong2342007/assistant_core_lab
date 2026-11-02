"""External data: current weather at campus from Open-Meteo (no API key needed).

Shows the three habits for any external service: timeout, limited retries, graceful fallback.
"""

from __future__ import annotations

import logging
import math
import time

import httpx

from assistant_api.schemas import Weather

log = logging.getLogger("assistant_api.weather")

WMO = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    51: "light drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    80: "rain showers",
    81: "heavy showers",
    95: "thunderstorm",
}


class ExternalServiceError(Exception):
    """The upstream service failed and no cached value is available."""


class WeatherClient:
    def __init__(
        self,
        url: str,
        lat: float,
        lon: float,
        timeout_s: float = 3.0,
        retries: int = 1,
        cache_ttl_s: float = 600,
        transport: httpx.BaseTransport | None = None,
    ):
        self.url, self.lat, self.lon = url, lat, lon
        self.retries, self.cache_ttl_s = retries, cache_ttl_s
        self._client = httpx.Client(timeout=timeout_s, transport=transport)
        self._cache: tuple[float, Weather] | None = None

    def current(self) -> Weather:
        if self._cache and time.monotonic() - self._cache[0] < self.cache_ttl_s:
            return self._cache[1]
        params = {"latitude": self.lat, "longitude": self.lon, "current": "temperature_2m,weather_code,wind_speed_10m"}
        last_exc: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                r = self._client.get(self.url, params=params)
                r.raise_for_status()
                data = r.json()
                if not isinstance(data, dict):
                    raise ValueError("weather payload must be a JSON object")
                cur = data.get("current")
                if not isinstance(cur, dict):
                    raise ValueError("weather 'current' must be a JSON object")
                temp = cur.get("temperature_2m")
                wind = cur.get("wind_speed_10m")
                if temp is None or wind is None:
                    raise ValueError("weather 'current' missing temperature or wind speed")
                temp_f = float(temp)
                wind_f = float(wind)
                if not (math.isfinite(temp_f) and math.isfinite(wind_f)):
                    raise ValueError(f"non-finite weather values: temp={temp}, wind={wind}")
                w = Weather(
                    temperature_c=temp_f,
                    wind_kmh=wind_f,
                    description=WMO.get(cur.get("weather_code"), f"code {cur.get('weather_code')}"),
                    observed_at=str(cur.get("time")),
                )
                self._cache = (time.monotonic(), w)
                return w
            except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
                last_exc = exc
                log.warning("weather attempt %d failed: %s", attempt + 1, type(exc).__name__)
                time.sleep(0.2 * (attempt + 1))
        if self._cache:  # graceful: stale but useful
            return self._cache[1].model_copy(update={"stale": True})
        raise ExternalServiceError("weather service unavailable") from last_exc
