from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

from backend.api.schemas.chat import ChatInput, ChatOutput
from backend.core.guardrails.filters import detect_doctor_intent
from backend.core.rag.pipeline import run_rag_pipeline

router = APIRouter(tags=["chat"])


@router.post("/api/v1/chat", response_model=ChatOutput)
async def chat_api(payload: ChatInput):
    """JSON API. If a doctor-finder intent is detected, tells the caller to
    hit /api/v1/doctors instead of returning a RAG answer."""
    is_doctor_query, city = detect_doctor_intent(payload.query)

    if is_doctor_query:
        if not city:
            return ChatOutput(city_needed=True)
        return ChatOutput(redirect_to_doctors=True, city=city)

    answer = run_rag_pipeline(payload.query, payload.mode)
    return ChatOutput(answer=answer)


@router.get("/", response_class=HTMLResponse)
async def chat_page_get(request: Request, mode: str = "patient"):
    templates = request.app.state.templates
    template_name = "clinician_mode.html" if mode == "clinician" else "patient_mode.html"
    return templates.TemplateResponse(request, template_name, {})


@router.post("/ask", response_class=HTMLResponse)
async def chat_page_post(request: Request, query: str = Form(...), mode: str = Form("patient")):
    """Server-rendered chat form submission (Jinja2 flow)."""
    templates = request.app.state.templates
    is_doctor_query, city = detect_doctor_intent(query)

    if is_doctor_query:
        if not city:
            return templates.TemplateResponse(request, "patient_mode.html", {
                "query": query,
                "answer_html": "<p>Which city are you looking in? (e.g. Chennai, Mumbai, Bengaluru, NCR)</p>",
            })
        # Redirect logic handled client-side or via RedirectResponse to /doctors?city=...
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/doctors?city={city}", status_code=303)

    answer = run_rag_pipeline(query, mode)
    from backend.utils.formatting import format_answer
    answer_html = format_answer(answer)
    template_name = "clinician_mode.html" if mode == "clinician" else "patient_mode.html"
    return templates.TemplateResponse(request, template_name, {"query": query, "answer_html": answer_html})
