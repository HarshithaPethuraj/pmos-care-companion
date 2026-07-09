from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from backend.api.schemas.checklist import ChecklistInput, ChecklistResult
from backend.core.rule_engine.engine import evaluate_rotterdam
from backend.core.rule_engine.models import SymptomInput
from backend.core.rule_engine.criteria import DISCLAIMER

router = APIRouter(tags=["checklist"])


@router.get("/checklist", response_class=HTMLResponse)
async def checklist_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "checklist.html", {})


@router.post("/api/v1/checklist", response_model=ChecklistResult)
async def run_checklist(payload: ChecklistInput):
    symptoms = SymptomInput(
        irregular_cycles=payload.irregular_cycles,
        clinical_hyperandrogenism=payload.clinical_hyperandrogenism,
        biochemical_hyperandrogenism=payload.biochemical_hyperandrogenism,
        polycystic_ovaries_on_usg=payload.polycystic_ovaries_on_usg,
    )
    result = evaluate_rotterdam(symptoms)

    return ChecklistResult(
        criteria_met_count=result.criteria_met_count,
        criteria_met=result.criteria_met,
        meets_rotterdam_threshold=result.meets_rotterdam_threshold,
        disclaimer=DISCLAIMER,
    )
