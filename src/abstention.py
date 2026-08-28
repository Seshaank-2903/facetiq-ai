"""Observability and Safety Filtering Engine (Abstention Layer).

Distinguishes semantic relevance from conversational observability to prevent
unsupported LLM inferences on medical diagnoses, third-person facts, or missing data.
"""

import re
from typing import Dict, Any, Tuple

# Patterns that indicate an explicit physical measurement or diagnostic quote in text
NUMERICAL_MEASUREMENT_PATTERNS = [
    r"\d+\/\d+\s*(mmHg)?",  # e.g., 120/80 blood pressure
    r"\d+\s*bpm",          # e.g., 72 bpm heart rate
    r"\d+\s*mg\/dl",       # e.g., 180 mg/dL cholesterol
    r"\d+\s*kg",           # e.g., 70 kg weight
    r"measured\s+at\s+\d+",
    r"lab\s+result[s]?\s+show[ed]?"
]

THIRD_PERSON_PATTERNS = [
    r"my\s+(father|mother|friend|manager|boss|sister|brother|doctor|colleague)",
    r"(he|she|they)\s+said",
    r"according\s+to\s+my"
]


def check_observability_and_safety(
    facet_record: Dict[str, Any],
    conversation_text: str
) -> Tuple[bool, str, str]:
    """Evaluates whether a candidate facet can be safely passed to LLM scoring
    or must be immediately abstained.

    Args:
        facet_record: Dictionary containing facet metadata (facet_normalized, facet_type, conversation_observable).
        conversation_text: Raw conversation string.

    Returns:
        Tuple[is_scorable: bool, status: str, abstention_reason: str]
    """
    facet_name = facet_record.get("facet_normalized", "")
    facet_type = facet_record.get("facet_type", "unknown")
    is_observable_by_default = facet_record.get("conversation_observable", True)
    default_reason = facet_record.get("abstention_reason", "")

    conv_lower = conversation_text.lower()

    # Rule 1: Medical Lab Value / Physical Measurement
    if any(m in facet_name for m in ["blood pressure", "cholesterol", "heart rate", "body weight"]):
        has_measurement = any(re.search(pat, conv_lower) for pat in NUMERICAL_MEASUREMENT_PATTERNS)
        if not has_measurement:
            return (
                False,
                "not_observable",
                f"Facet '{facet_name}' is a medical measurement. Conversation contains no explicit quantitative test values."
            )
        return (True, "scored", "")

    # Rule 2: Clinical Medical Diagnoses Trap
    if "diagnosis" in facet_name or (facet_type == "medical" and "condition" in facet_name):
        if "diagnosed" not in conv_lower and "doctor said" not in conv_lower:
            return (
                False,
                "not_observable",
                f"Facet '{facet_name}' requires formal clinical diagnosis, which cannot be inferred from symptoms."
            )

    # Rule 3: Third-Person Statement Trap
    if any(p in facet_name for p in ["father's", "mother's", "friend's", "manager rating"]):
        return (
            False,
            "insufficient_evidence",
            f"Facet '{facet_name}' refers to third-party or external entity, not direct evidence of the speaker."
        )

    # Rule 4: General Non-Observable Attributes
    if not is_observable_by_default:
        return (
            False,
            "not_observable",
            default_reason or f"Facet '{facet_name}' is classified as not directly observable from conversation."
        )

    # Rule 5: Scorable Candidate
    return (True, "scored", "")
