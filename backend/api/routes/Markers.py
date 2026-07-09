from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from backend.core.rag.pipeline import run_rag_pipeline
from backend.utils.formatting import format_answer

router = APIRouter(tags=["markers"])

# Curated list of PMOS-relevant markers offered as quick-pick chips.
COMMON_MARKERS = [
    "Testosterone", "SHBG", "LH", "FSH", "AMH", "Prolactin",
    "TSH", "17-OHP", "Fasting insulin", "HbA1c", "Lipid panel",
]

EXPLAINER_INTRO = (
    "Pick a marker from your blood test to learn what it means and why it's "
    "relevant to PMOS. This explains the marker in general - it does not "
    "interpret your specific numbers or diagnose anything. Always review your "
    "actual results with your doctor."
)


def _marker_query(marker: str) -> str:
    return (
        f"Explain the blood test marker '{marker}' in the context of PMOS: what it is, "
        f"why it's measured, and what a patient should ask their doctor. Do not interpret "
        f"specific values or diagnose."
    )


@router.get("/markers", response_class=HTMLResponse)
async def markers_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "markers.html", {
        "markers": COMMON_MARKERS,
        "intro": EXPLAINER_INTRO,
    })


@router.post("/markers", response_class=HTMLResponse)
async def markers_explain(request: Request, marker: str = Form(...)):
    templates = request.app.state.templates
    # Reuse the patient-mode RAG pipeline; guardrails still apply.
    answer = run_rag_pipeline(_marker_query(marker), mode="patient")
    answer_html = format_answer(answer)
    return templates.TemplateResponse(request, "markers.html", {
        "markers": COMMON_MARKERS,
        "intro": EXPLAINER_INTRO,
        "selected": marker,
        "answer_html": answer_html,
    })
