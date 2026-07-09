from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from backend.api.schemas.doctors import DoctorSearchResult, DoctorOut
from backend.core.doctors.service import find_doctors

router = APIRouter(tags=["doctors"])


@router.get("/api/v1/doctors", response_model=DoctorSearchResult)
async def search_doctors_api(city: str):
    """JSON API - used by the RAG chat route when it detects a doctor-finder intent."""
    result = find_doctors(city)
    return DoctorSearchResult(
        city=result["city"],
        tier=result["tier"],
        doctors=[DoctorOut(**vars(d)) for d in result["doctors"]],
    )


@router.get("/doctors", response_class=HTMLResponse)
async def doctors_page(request: Request, city: str = "chennai"):
    """Server-rendered Find a Doctor page."""
    result = find_doctors(city)
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "find_doctor.html", {
        "city": result["city"],
        "tier": result["tier"],
        "doctors": result["doctors"],
    })
