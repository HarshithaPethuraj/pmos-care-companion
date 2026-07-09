from backend.core.guardrails.filters import is_diagnostic_request, detect_doctor_intent
from backend.core.guardrails.red_flags import check_red_flags


def test_diagnostic_request_detected():
    assert is_diagnostic_request("Do I have PCOS?") is True
    assert is_diagnostic_request("What is PMOS?") is False


def test_doctor_intent_with_city():
    is_doctor, city = detect_doctor_intent("Can you recommend a gynecologist in Chennai?")
    assert is_doctor is True
    assert city == "chennai"


def test_doctor_intent_without_city():
    is_doctor, city = detect_doctor_intent("Can you recommend a good gynecologist?")
    assert is_doctor is True
    assert city is None


def test_no_doctor_intent_on_plain_question():
    is_doctor, city = detect_doctor_intent("What foods help manage PMOS?")
    assert is_doctor is False


def test_red_flag_detected():
    assert check_red_flags("I have severe pain and heavy bleeding") is not None


def test_no_red_flag_on_normal_query():
    assert check_red_flags("What is the Rotterdam criteria?") is None
