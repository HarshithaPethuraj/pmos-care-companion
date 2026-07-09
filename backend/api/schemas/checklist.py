from pydantic import BaseModel, Field


class ChecklistInput(BaseModel):
    """Raw symptom inputs collected from the user-facing checklist form."""
    irregular_cycles: bool = Field(..., description="Fewer than 8 cycles/year or cycles longer than 35 days")
    clinical_hyperandrogenism: bool = Field(..., description="Hirsutism, acne, or androgenic alopecia present")
    biochemical_hyperandrogenism: bool = Field(False, description="Elevated free/total testosterone on lab work")
    polycystic_ovaries_on_usg: bool = Field(..., description="≥20 follicles per ovary or ovarian volume ≥10ml on ultrasound")


class ChecklistResult(BaseModel):
    criteria_met_count: int
    criteria_met: list[str]
    meets_rotterdam_threshold: bool
    disclaimer: str
