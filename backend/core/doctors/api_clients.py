"""
Tier 2: dynamic fallback lookups for cities not in the curated static list.

Two options, both optional (used only if the relevant API key is set):

1. Google Places API - live text search, real phone/address/rating data.
   Requires billing enabled on the Google Cloud project.
2. Google Programmable Search Engine (CSE) scoped to practo.com - a free-tier
   alternative (100 queries/day) since Practo has no public developer API.
"""
import requests

from backend.config import get_settings
from backend.core.doctors.models import Doctor


def search_places_live(city: str) -> list[Doctor]:
    settings = get_settings()
    if not settings.google_places_api_key:
        return []

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"gynecologist doctors in {city}", "key": settings.google_places_api_key}

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException:
        return []

    doctors = []
    for r in results[:15]:
        place_id = r.get("place_id")
        doctors.append(Doctor(
            name=r.get("name", "Unknown"),
            specialization="General gynec",
            area=city,
            address=r.get("formatted_address", ""),
            phone=None,  # text search doesn't return phone; needs a Place Details call
            rating=r.get("rating"),
            rating_count=r.get("user_ratings_total"),
            maps_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
            source="dynamic",
        ))
    return doctors


def search_practo_via_cse(city: str) -> list[Doctor]:
    """Free-tier alternative: Google Custom Search Engine scoped to practo.com."""
    settings = get_settings()
    if not settings.google_cse_api_key or not settings.google_cse_engine_id:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.google_cse_api_key,
        "cx": settings.google_cse_engine_id,
        "q": f"gynecologist PCOS PMOS specialist {city} site:practo.com",
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except requests.RequestException:
        return []

    doctors = []
    for item in items[:10]:
        doctors.append(Doctor(
            name=item.get("title", "Unknown"),
            specialization="See Practo listing",
            area=city,
            address=item.get("snippet", ""),
            phone=None,
            maps_url=item.get("link"),
            source="dynamic",
        ))
    return doctors
