TERMINOLOGY_NOTE = (
    "You may see this condition called PCOS or PMOS (Polyendocrine Metabolic "
    "Ovarian Syndrome) - same condition, updated name as of May 2026."
)

PATIENT_MODE_FOOTER = (
    "This information is educational and not a substitute for professional "
    "medical advice. Please consult a doctor for diagnosis or treatment."
)


def append_disclaimer(answer: str, mode: str = "patient") -> str:
    if mode == "patient":
        return f"{answer}\n\n---\n{PATIENT_MODE_FOOTER}"
    return answer
