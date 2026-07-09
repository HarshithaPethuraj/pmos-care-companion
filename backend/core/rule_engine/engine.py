"""
Rotterdam rule engine - pure Python, no ML.

Given symptom flags, returns which of the 3 Rotterdam criteria are met
and whether the 2-of-3 threshold is reached. Never returns a diagnosis.
"""
from backend.core.rule_engine.criteria import CRITERIA_LABELS, ROTTERDAM_THRESHOLD
from backend.core.rule_engine.models import SymptomInput, RuleEngineResult


def evaluate_rotterdam(symptoms: SymptomInput) -> RuleEngineResult:
    hyperandrogenism = symptoms.clinical_hyperandrogenism or symptoms.biochemical_hyperandrogenism

    criteria_flags = {
        "irregular_cycles": symptoms.irregular_cycles,
        "hyperandrogenism": hyperandrogenism,
        "polycystic_ovaries_on_usg": symptoms.polycystic_ovaries_on_usg,
    }

    met = [CRITERIA_LABELS[key] for key, is_met in criteria_flags.items() if is_met]
    count = len(met)

    return RuleEngineResult(
        criteria_met_count=count,
        criteria_met=met,
        meets_rotterdam_threshold=count >= ROTTERDAM_THRESHOLD,
    )
