"""
PMOS Care Companion - FastAPI application entry point.

Run locally:  uvicorn backend.main:app --reload --port 7860
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import get_settings
from backend.api.routes import health, checklist, chat, doctors, modes, markers

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Static assets (CSS) and Jinja2 templates live inside backend/
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Make templates accessible to route modules without circular imports
app.state.templates = templates

# API + page routes
app.include_router(health.router)
app.include_router(checklist.router)
app.include_router(chat.router)
app.include_router(doctors.router)
app.include_router(modes.router)
app.include_router(markers.router)
