from dataclasses import dataclass


@dataclass
class SymptomInput:
    irregular_cycles: bool
    clinical_hyperandrogenism: bool
    biochemical_hyperandrogenism: bool
    polycystic_ovaries_on_usg: bool


@dataclass
class RuleEngineResult:
    criteria_met_count: int
    criteria_met: list[str]
    meets_rotterdam_threshold: bool
