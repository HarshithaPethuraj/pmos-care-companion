from dataclasses import dataclass
from typing import Optional


@dataclass
class Doctor:
    name: str
    specialization: str
    area: str
    address: str
    phone: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    maps_url: Optional[str] = None
    source: str = "curated"  # "curated" | "practo" | "dynamic"
