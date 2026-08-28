"""Defensive JSON parser and Pydantic validator module.

Parses LLM string outputs into validated Pydantic schemas, repairing minor malformations
and falling back safely without crashing the pipeline.
"""

import json
import re
from typing import List, Dict, Any

from src.schemas import FacetScoreResult


def extract_json_payload(raw_text: str) -> str:
    """Extracts JSON text payload from raw string, stripping markdown backticks."""
    if not isinstance(raw_text, str):
        return ""
    
    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", raw_text, re.DOTALL)
    if match:
        return match.group(1)
        
    # Attempt to locate first '{' and last '}'
    start_idx = raw_text.find("{")
    end_idx = raw_text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return raw_text[start_idx : end_idx + 1]

    return raw_text.strip()


def validate_and_repair_facet_result(raw_item: Dict[str, Any], fallback_facet: str = "unknown") -> FacetScoreResult:
    """Validates an individual facet result dictionary against FacetScoreResult schema,
    applying safe auto-repairs for minor type mismatches.

    Args:
        raw_item: Raw dictionary from LLM JSON.
        fallback_facet: Facet name to use if missing.

    Returns:
        Validated FacetScoreResult instance.
    """
    if not isinstance(raw_item, dict):
        return FacetScoreResult(
            facet=fallback_facet,
            status="insufficient_evidence",
            score=None,
            confidence=0.0,
            evidence=None,
            reason="Malformed LLM result item (expected JSON object)."
        )

    facet_name = str(raw_item.get("facet", fallback_facet)).strip() or fallback_facet
    raw_status = str(raw_item.get("status", "insufficient_evidence")).strip().lower()

    # Map status variants
    if raw_status in ["scored", "valid"]:
        status = "scored"
    elif raw_status in ["not_observable", "unobservable", "non_observable"]:
        status = "not_observable"
    else:
        status = "insufficient_evidence"

    # Repair score
    raw_score = raw_item.get("score")
    score = None
    if status == "scored":
        try:
            score = int(raw_score)
            if score < 1: score = 1
            if score > 5: score = 5
        except (ValueError, TypeError):
            # If score cannot be parsed to 1-5 int, downgrade status to insufficient_evidence
            status = "insufficient_evidence"
            score = None

    # Repair confidence
    raw_conf = raw_item.get("confidence", 0.5)
    try:
        conf = float(raw_conf)
        if conf < 0.0: conf = 0.0
        if conf > 1.0: conf = 1.0
    except (ValueError, TypeError):
        conf = 0.5

    evidence = str(raw_item.get("evidence", "")) if raw_item.get("evidence") else None
    reason = str(raw_item.get("reason", "")) if raw_item.get("reason") else None

    try:
        return FacetScoreResult(
            facet=facet_name,
            status=status,
            score=score,
            confidence=conf,
            evidence=evidence,
            reason=reason
        )
    except Exception as err:
        print(f"[Validation Repair] Failed strict schema validation: {err}. Applying fallback.")
        return FacetScoreResult(
            facet=facet_name,
            status="insufficient_evidence",
            score=None,
            confidence=0.0,
            evidence=None,
            reason=f"Validation error fallback: {err}"
        )


def parse_and_validate_batch_output(
    raw_llm_response: str,
    requested_facets: List[str]
) -> List[FacetScoreResult]:
    """Parses raw LLM text into a list of validated FacetScoreResult objects.

    Args:
        raw_llm_response: Raw text returned by LLM endpoint.
        requested_facets: List of candidate facet names requested in prompt.

    Returns:
        List of validated FacetScoreResult objects.
    """
    clean_json_str = extract_json_payload(raw_llm_response)
    results = []

    try:
        data = json.loads(clean_json_str)
        if isinstance(data, dict) and "results" in data and isinstance(data["results"], list):
            items = data["results"]
        elif isinstance(data, list):
            items = data
        else:
            items = []

        item_by_facet = {}
        for item in items:
            if isinstance(item, dict) and "facet" in item:
                item_by_facet[str(item["facet"]).strip().lower()] = item

        for facet_name in requested_facets:
            key = facet_name.strip().lower()
            if key in item_by_facet:
                val_res = validate_and_repair_facet_result(item_by_facet[key], facet_name)
            else:
                # If model missed a requested facet, create explicit abstention
                val_res = FacetScoreResult(
                    facet=facet_name,
                    status="insufficient_evidence",
                    score=None,
                    confidence=0.0,
                    evidence=None,
                    reason="Model omitted facet from batch results."
                )
            results.append(val_res)

    except Exception as e:
        print(f"[Validation Warning] Failed to parse LLM JSON: {e}. Falling back to default abstention.")
        for facet_name in requested_facets:
            results.append(
                FacetScoreResult(
                    facet=facet_name,
                    status="insufficient_evidence",
                    score=None,
                    confidence=0.0,
                    evidence=None,
                    reason=f"Malformed LLM output error: {e}"
                )
            )

    return results
