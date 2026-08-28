"""Unit tests for JSON output validation and repair module."""

from src.validation import extract_json_payload, validate_and_repair_facet_result, parse_and_validate_batch_output

def test_extract_json_payload():
    raw_markdown = "Here is the result:\n```json\n{\"results\": []}\n```"
    extracted = extract_json_payload(raw_markdown)
    assert extracted == "{\"results\": []}"

def test_validate_and_repair_facet_result():
    # Valid scored item
    res1 = validate_and_repair_facet_result({
        "facet": "confidence",
        "status": "scored",
        "score": "4",
        "confidence": "0.9"
    })
    assert res1.status == "scored"
    assert res1.score == 4
    assert res1.confidence == 0.9

    # Mismatched status and score (auto-repair score to None)
    res2 = validate_and_repair_facet_result({
        "facet": "blood pressure",
        "status": "not_observable",
        "score": 3,
        "confidence": 0.95
    })
    assert res2.status == "not_observable"
    assert res2.score is None

def test_parse_and_validate_batch_output_malformed():
    raw_bad = "Invalid non-JSON string"
    results = parse_and_validate_batch_output(raw_bad, ["confidence", "leadership"])
    assert len(results) == 2
    assert results[0].status == "insufficient_evidence"
    assert results[0].score is None
