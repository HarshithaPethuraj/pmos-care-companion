from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["modes"])

AVAILABLE_MODES = [
    {"id": "patient", "label": "Patient Mode", "description": "Plain-language Q&A, lifestyle & diet, always cites sources."},
    {"id": "clinician", "label": "Clinician Mode", "description": "Rotterdam criteria detail, ESHRE/ASRM guideline content, technical tone."},
]


@router.get("/modes")
async def list_modes():
    return {"modes": AVAILABLE_MODES}
