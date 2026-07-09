"""
Doctor Finder Service - the single entrypoint the rest of the app calls.

Strategy:
  1. Check curated static list (Tier 1) for the city.
  2. If not found (or empty), fall back to live API search (Tier 2):
     Google Places first, then Google CSE (Practo-scoped) if Places
     isn't configured.
"""
from backend.core.doctors.curated import get_curated_doctors, is_static_metro
from backend.core.doctors.api_clients import search_places_live, search_practo_via_cse
from backend.core.doctors.models import Doctor


def find_doctors(city: str) -> dict:
    """
    Returns: {"city": str, "tier": "curated" | "dynamic" | "none", "doctors": [Doctor]}
    """
    if is_static_metro(city):
        doctors = get_curated_doctors(city)
        if doctors:
            return {"city": city, "tier": "curated", "doctors": doctors}

    dynamic_doctors: list[Doctor] = search_places_live(city)
    if not dynamic_doctors:
        dynamic_doctors = search_practo_via_cse(city)

    if dynamic_doctors:
        return {"city": city, "tier": "dynamic", "doctors": dynamic_doctors}

    return {"city": city, "tier": "none", "doctors": []}
