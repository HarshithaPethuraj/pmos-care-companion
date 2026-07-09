"""
Tier 1: curated doctor directory.

Loads data/doctors.json, which has this shape:

{
  "disclaimer": "...",
  "dynamic_fallback": {"enabled": true, "note": "..."},
  "static_metros": {
    "chennai": {
      "google_places_tier": {"doctors": [...]},
      "practo_tier": {"doctors": [...]}
    },
    ...
  }
}
"""
import json
from functools import lru_cache
from pathlib import Path

from backend.config import get_settings
from backend.core.doctors.models import Doctor

# Normalizes free-text city input to the metro keys used in doctors.json.
CITY_ALIASES = {
    "chennai": "chennai",
    "bengaluru": "bengaluru", "bangalore": "bengaluru",
    "mumbai": "mumbai", "bombay": "mumbai",
    "delhi": "delhi", "new delhi": "delhi",
    "gurugram": "ncr", "gurgaon": "ncr", "noida": "ncr", "ncr": "ncr", "delhi ncr": "ncr",
    "hyderabad": "hyderabad",
    "kolkata": "kolkata", "calcutta": "kolkata",
}


@lru_cache()
def _load_raw_data() -> dict:
    settings = get_settings()
    path = Path(settings.doctors_data_path)
    with open(path, "r") as f:
        return json.load(f)


def resolve_metro_key(city: str) -> str | None:
    return CITY_ALIASES.get(city.strip().lower())


def get_curated_doctors(city: str) -> list[Doctor]:
    """Returns curated doctors for a city, or [] if city isn't in the static list."""
    metro_key = resolve_metro_key(city)
    if not metro_key:
        return []

    data = _load_raw_data()
    metro = data.get("static_metros", {}).get(metro_key)
    if not metro:
        return []

    doctors: list[Doctor] = []

    for d in metro.get("google_places_tier", {}).get("doctors", []):
        doctors.append(Doctor(
            name=d["name"], specialization=d.get("specialization", "General gynec"),
            area=d.get("area", ""), address=d.get("address", ""),
            phone=d.get("phone"), rating=d.get("rating"), rating_count=d.get("rating_count"),
            maps_url=d.get("maps_url"), source="curated",
        ))

    for d in metro.get("practo_tier", {}).get("doctors", []):
        doctors.append(Doctor(
            name=d["name"], specialization=d.get("specialization", "General gynec"),
            area=d.get("area", ""), address=f"Fee: Rs.{d.get('consultation_fee_inr', 'N/A')} | {d.get('experience_years', '?')} yrs exp",
            phone=None, rating=d.get("recommended_pct"), rating_count=d.get("patient_story_count"),
            maps_url=d.get("profile_url"), source="practo",
        ))

    return doctors


def is_static_metro(city: str) -> bool:
    return resolve_metro_key(city) is not None
