"""Unit tests for safety, abstention, and hallucination traps."""

from src.abstention import check_observability_and_safety

def test_medical_lab_value_trap():
    # Blood pressure without numerical measurement -> abstain
    facet_record = {
        "facet_normalized": "blood pressure",
        "facet_type": "medical",
        "conversation_observable": False,
        "abstention_reason": "Medical measurement required."
    }
    is_scorable, status, reason = check_observability_and_safety(
        facet_record,
        "I've been feeling very dizzy lately when I wake up."
    )
    assert is_scorable is False
    assert status == "not_observable"
    assert "medical measurement" in reason.lower()

    # Blood pressure WITH explicit reported measurement -> scorable
    is_scorable_num, _, _ = check_observability_and_safety(
        facet_record,
        "My doctor measured my blood pressure at 120/80 yesterday."
    )
    assert is_scorable_num is True

def test_third_person_trap():
    facet_record = {
        "facet_normalized": "father's employment status",
        "facet_type": "biographical",
        "conversation_observable": False,
        "abstention_reason": "Third person."
    }
    is_scorable, status, _ = check_observability_and_safety(
        facet_record,
        "My father lost his job last month."
    )
    assert is_scorable is False
    assert status == "insufficient_evidence"

def test_observable_facet():
    facet_record = {
        "facet_normalized": "confidence",
        "facet_type": "behavioral",
        "conversation_observable": True,
        "abstention_reason": ""
    }
    is_scorable, status, _ = check_observability_and_safety(
        facet_record,
        "I gave the presentation confidently."
    )
    assert is_scorable is True
    assert status == "scored"
