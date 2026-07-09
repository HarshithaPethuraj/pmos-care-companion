from pydantic import BaseModel
from typing import Optional


class DoctorOut(BaseModel):
    name: str
    specialization: str
    area: str
    address: str
    phone: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    maps_url: Optional[str] = None
    source: str


class DoctorSearchResult(BaseModel):
    city: str
    tier: str  # "curated" | "dynamic" | "none"
    doctors: list[DoctorOut]
    disclaimer: str = (
        "This directory is for informational purposes only, based on publicly "
        "available listings. It is not a medical referral or endorsement. "
        "Please verify credentials and availability independently."
    )
