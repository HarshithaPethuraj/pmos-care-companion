from pydantic import BaseModel
from typing import Optional, Literal


class ChatInput(BaseModel):
    query: str
    mode: Literal["patient", "clinician"] = "patient"


class ChatOutput(BaseModel):
    answer: Optional[str] = None
    redirect_to_doctors: bool = False
    city_needed: bool = False
    city: Optional[str] = None
