"""
Rotterdam Criteria (2003, reaffirmed by ESHRE/ASRM 2023 International Guideline)
for PMOS (formerly PCOS). Diagnosis requires 2 of the following 3:

1. Oligo- or anovulation (irregular cycles)
2. Clinical and/or biochemical signs of hyperandrogenism
3. Polycystic ovaries on ultrasound (after exclusion of other etiologies)

This module intentionally contains NO ML model - it is a transparent,
auditable rule engine. Output states which criteria are met and does
NOT issue a diagnosis.
"""

CRITERIA_LABELS = {
    "irregular_cycles": "Oligo/anovulation (irregular menstrual cycles)",
    "hyperandrogenism": "Clinical and/or biochemical hyperandrogenism",
    "polycystic_ovaries_on_usg": "Polycystic ovarian morphology on ultrasound",
}

ROTTERDAM_THRESHOLD = 2  # of 3 criteria required
TOTAL_CRITERIA = 3

DISCLAIMER = (
    "This checklist reflects the Rotterdam criteria used in clinical guidelines "
    "as a reference tool only. It is not a diagnosis. PMOS (formerly PCOS) diagnosis "
    "requires exclusion of other conditions (thyroid disorders, hyperprolactinemia, "
    "non-classic congenital adrenal hyperplasia) by a qualified clinician. "
    "Please consult a doctor or gynecologist for an actual diagnosis."
)
