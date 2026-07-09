from backend.core.rule_engine.engine import evaluate_rotterdam
from backend.core.rule_engine.models import SymptomInput


def test_meets_threshold_with_two_criteria():
    symptoms = SymptomInput(
        irregular_cycles=True,
        clinical_hyperandrogenism=True,
        biochemical_hyperandrogenism=False,
        polycystic_ovaries_on_usg=False,
    )
    result = evaluate_rotterdam(symptoms)
    assert result.criteria_met_count == 2
    assert result.meets_rotterdam_threshold is True


def test_does_not_meet_threshold_with_one_criterion():
    symptoms = SymptomInput(
        irregular_cycles=True,
        clinical_hyperandrogenism=False,
        biochemical_hyperandrogenism=False,
        polycystic_ovaries_on_usg=False,
    )
    result = evaluate_rotterdam(symptoms)
    assert result.criteria_met_count == 1
    assert result.meets_rotterdam_threshold is False


def test_hyperandrogenism_counts_once_even_if_both_subtypes_present():
    symptoms = SymptomInput(
        irregular_cycles=False,
        clinical_hyperandrogenism=True,
        biochemical_hyperandrogenism=True,
        polycystic_ovaries_on_usg=False,
    )
    result = evaluate_rotterdam(symptoms)
    assert result.criteria_met_count == 1
    assert result.meets_rotterdam_threshold is False


def test_all_three_criteria_met():
    symptoms = SymptomInput(
        irregular_cycles=True,
        clinical_hyperandrogenism=True,
        biochemical_hyperandrogenism=False,
        polycystic_ovaries_on_usg=True,
    )
    result = evaluate_rotterdam(symptoms)
    assert result.criteria_met_count == 3
    assert result.meets_rotterdam_threshold is True
