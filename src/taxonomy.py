"""Taxonomy classification module.

Categorizes facets into domain types and determines whether an attribute is
directly observable from conversational evidence or requires external/medical proof.
"""

from typing import Tuple

TAXONOMY_CATEGORIES = [
    "behavioral",
    "communication",
    "emotional_expression",
    "skill",
    "preference",
    "goal_intent",
    "biographical",
    "medical",
    "financial",
    "external_fact",
    "sensitive",
    "unknown"
]

# Keywords mapping for deterministic rule-based classification
CATEGORY_KEYWORD_MAP = {
    "medical": ["medical", "blood pressure", "diagnosis", "cholesterol", "heart rate", "disease", "illness", "clinical", "doctor", "history"],
    "communication": ["communication", "presentation", "speaking", "fluency", "listening", "sarcasm", "code-switching", "hindi", "assertiveness", "articulation"],
    "behavioral": ["confidence", "leadership", "adaptability", "team management", "self-confidence"],
    "emotional_expression": ["stress", "anxiety", "frustration", "enthusiasm", "emotional stability", "humor"],
    "skill": ["skill", "ability", "problem solving", "programming", "sql", "decision making", "time management", "project management"],
    "financial": ["salary", "bank account", "balance", "credit score", "financial"],
    "biographical": ["age", "years of experience", "employer", "father's", "mother's", "employment status"],
    "external_fact": ["manager rating", "gpa", "iq score"],
    "sensitive": ["criminal record", "political", "religious", "home address"],
    "preference": ["sleep quality", "work-life balance", "expectations"]
}


def classify_facet(facet_normalized: str, raw_category_hint: str = "") -> Tuple[str, bool, str]:
    """Classifies a normalized facet string into a taxonomy type and observability flag.
    
    Args:
        facet_normalized: Cleaned lowercase facet string.
        raw_category_hint: Optional category hint from raw CSV.

    Returns:
        Tuple[facet_type, conversation_observable, default_abstention_reason]
    """
    text = f"{facet_normalized} {raw_category_hint}".lower()
    
    # Check for medical non-observable trap
    for kw in CATEGORY_KEYWORD_MAP["medical"]:
        if kw in text:
            return (
                "medical",
                False,
                "Medical measurements and clinical diagnoses cannot be inferred from conversational text without explicit reported lab values."
            )
            
    # Check for third-person or biographical non-observable trap
    if any(p in text for p in ["father's", "mother's", "friend's", "manager rating"]):
        return (
            "biographical" if "father" in text or "mother" in text else "external_fact",
            False,
            "Statements regarding third parties or external official evaluations are not direct evidence of the speaker's own attributes."
        )

    # Check financial / sensitive
    for kw in CATEGORY_KEYWORD_MAP["financial"]:
        if kw in text:
            return (
                "financial",
                False,
                "Private financial metrics require explicit self-reported numerical disclosures."
            )
            
    for kw in CATEGORY_KEYWORD_MAP["sensitive"]:
        if kw in text:
            return (
                "sensitive",
                False,
                "Sensitive legal or personal background attributes are non-observable from general conversation."
            )
            
    for kw in CATEGORY_KEYWORD_MAP["external_fact"]:
        if kw in text:
            return (
                "external_fact",
                False,
                "Formal external test scores or academic metrics require explicit documentation."
            )

    # Check observable categories
    for cat in ["communication", "behavioral", "emotional_expression", "skill", "preference"]:
        for kw in CATEGORY_KEYWORD_MAP[cat]:
            if kw in text:
                return (cat, True, "")

    # Default fallback
    if raw_category_hint:
        hint_clean = raw_category_hint.lower().strip()
        if hint_clean in ["communication", "behavioral", "skill", "emotional_expression"]:
            return (hint_clean, True, "")
        elif hint_clean in ["medical", "biographical", "financial", "sensitive", "external_fact"]:
            return (hint_clean, False, "Attribute requires explicit external or physical measurement.")
            
    return ("unknown", True, "")
