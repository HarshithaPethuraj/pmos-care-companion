import re

DIAGNOSTIC_REQUEST_PATTERNS = [
    r"\bdo i have (pcos|pmos)\b",
    r"\bam i (having|suffering from) (pcos|pmos)\b",
    r"\bdiagnose me\b",
]

DOCTOR_INTENT_PATTERNS = [
    r"\b(doctor|gynecologist|gynaecologist|specialist|clinic)\b.*\b(recommend|suggest|find|near|in)\b",
    r"\b(recommend|suggest|find)\b.*\b(doctor|gynecologist|gynaecologist|specialist|clinic)\b",
    r"\bwhere can i (find|see|consult)\b",
]

CITY_LIST = [
    "chennai", "bengaluru", "bangalore", "mumbai", "delhi", "gurugram",
    "gurgaon", "noida", "ncr", "hyderabad", "kolkata",
]


def is_diagnostic_request(query: str) -> bool:
    q = query.lower()
    return any(re.search(p, q) for p in DIAGNOSTIC_REQUEST_PATTERNS)


def detect_doctor_intent(query: str) -> tuple[bool, str | None]:
    q = query.lower()
    is_doctor_query = any(re.search(p, q) for p in DOCTOR_INTENT_PATTERNS)
    city = next((c for c in CITY_LIST if c in q), None)
    return is_doctor_query, city
