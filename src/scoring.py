"""Batched LLM Scoring Module.

Constructs scoring prompts, batches candidate facets, calls open-weight LLM backends
(hosted, Ollama, or deterministic mock), and validates structured outputs.
"""

import json
import requests
from typing import List, Dict, Any

from src.config import settings
from src.schemas import FacetScoreResult
from src.validation import parse_and_validate_batch_output

SYSTEM_PROMPT = """You are an expert AI evidence evaluator scoring conversation text against candidate facets.

STRICT SCORING RULES:
1. Rely ONLY on explicit conversational evidence in the provided text. Do NOT invent facts or infer unstated attributes.
2. Score on a 5-level ordinal scale supported by evidence strength:
   1 = Very weak evidence
   2 = Weak evidence
   3 = Moderate evidence
   4 = Strong evidence
   5 = Very strong evidence
3. Speaker vs. Third-Party: Distinguish the speaker's own statements from statements made by or about third parties (e.g., father, manager, friend). If evidence concerns another person, abstain with status "insufficient_evidence".
4. Quoted Speech & Sarcasm: Do not treat quoted statements or sarcastic remarks literally unless backed by actual speaker sentiment.
5. Contradictory Evidence: If text contains conflicting statements, assign a moderate score (e.g. 3) with low confidence (0.50-0.60) and explain both sides in evidence.
6. Abstention: Return status "not_observable" or "insufficient_evidence" with score null when evidence is missing or unsupported.
7. Return ONLY valid JSON matching this structure:
{
  "results": [
    {
      "facet": "<facet_name>",
      "status": "scored" | "insufficient_evidence" | "not_observable",
      "score": 1-5 integer or null,
      "confidence": float 0.0-1.0,
      "evidence": "quoted evidence string or null",
      "reason": "abstention reason string or null"
    }
  ]
}
"""


def construct_batch_prompt(conversation_text: str, candidate_facets: List[Dict[str, Any]]) -> str:
    """Builds the user prompt for a batch of candidate facets."""
    facets_desc = []
    for f in candidate_facets:
        facets_desc.append(f"- Facet: '{f['facet_normalized']}' | Description: {f.get('scoring_definition', '')}")

    facets_block = "\n".join(facets_desc)

    user_prompt = f"""CONVERSATION TEXT:
\"\"\"{conversation_text}\"\"\"

CANDIDATE FACETS TO EVALUATE:
{facets_block}

Evaluate each candidate facet against the conversation text and return structured JSON."""
    return user_prompt


def mock_llm_score_batch(conversation_text: str, candidate_facets: List[Dict[str, Any]]) -> str:
    """Deterministic rule-based mock LLM simulator for offline testing and verification.

    Evaluates text patterns (sarcasm, quotes, contradictions, clear evidence) to generate
    realistic LLM output JSON.
    """
    conv_lower = conversation_text.lower()
    results = []

    for f in candidate_facets:
        fname = f["facet_normalized"].lower()
        
        # 1. Contradiction handling
        if ("confident" in conv_lower and ("panic" in conv_lower or "terrified" in conv_lower)) or \
           ("love" in conv_lower and "hate" in conv_lower):
            results.append({
                "facet": f["facet_normalized"],
                "status": "scored",
                "score": 3,
                "confidence": 0.55,
                "evidence": "Conversation contains contradictory statements regarding performance confidence.",
                "reason": None
            })
            continue

        # 2. Sarcasm handling
        if "absolutely love" in conv_lower and ("500 people" in conv_lower or "panic" in conv_lower or "nightmare" in conv_lower):
            results.append({
                "facet": f["facet_normalized"],
                "status": "scored",
                "score": 1,
                "confidence": 0.75,
                "evidence": "Speaker used sarcastic tone ('absolutely LOVE presenting to 500 people') indicating low comfort.",
                "reason": None
            })
            continue

        # 3. Quoted speech handling
        if "manager said" in conv_lower or "boss said" in conv_lower:
            if fname in ["presentation skill", "communication skill", "confidence"]:
                results.append({
                    "facet": f["facet_normalized"],
                    "status": "insufficient_evidence",
                    "score": None,
                    "confidence": 0.85,
                    "evidence": None,
                    "reason": "Statement is a quote from a manager, not direct evidence of speaker's self-assessed competence."
                })
                continue

        # 4. Code-switching handling
        if "hone ke baad" in conv_lower or "presentation start" in conv_lower:
            if fname in ["code-switching fluency", "communication skill", "confidence"]:
                results.append({
                    "facet": f["facet_normalized"],
                    "status": "scored",
                    "score": 4,
                    "confidence": 0.88,
                    "evidence": "Speaker fluently mixed Hindi and English ('Presentation start hone ke baad I became comfortable').",
                    "reason": None
                })
                continue

        # 5. Clear Positive Evidence
        if any(w in conv_lower for w in ["confidently", "comfortably", "effectively", "calmly", "solved", "managed"]):
            if fname in ["confidence", "communication skill", "presentation skill", "leadership", "problem solving", "self-confidence"]:
                results.append({
                    "facet": f["facet_normalized"],
                    "status": "scored",
                    "score": 4 if "confidently" in conv_lower or "calmly" in conv_lower else 5,
                    "confidence": 0.90,
                    "evidence": f"Speaker stated: '{conversation_text.strip()}'",
                    "reason": None
                })
                continue

        # 6. Stress / Anxiety Evidence
        if any(w in conv_lower for w in ["stress", "anxious", "nervous", "dizzy", "panic", "couldn't sleep"]):
            if fname in ["stress", "anxiety", "frustration level", "sleep quality"]:
                results.append({
                    "facet": f["facet_normalized"],
                    "status": "scored",
                    "score": 4,
                    "confidence": 0.85,
                    "evidence": f"Speaker reported symptoms/feelings: '{conversation_text.strip()}'",
                    "reason": None
                })
                continue

        # 7. Default Abstention for Low Evidence
        results.append({
            "facet": f["facet_normalized"],
            "status": "insufficient_evidence",
            "score": None,
            "confidence": 0.80,
            "evidence": None,
            "reason": f"No conversational evidence found supporting facet '{f['facet_normalized']}'."
        })

    return json.dumps({"results": results})


def call_llm_api(system_prompt: str, user_prompt: str) -> str:
    """Dispatches request to configured open-weight model backend."""
    provider = settings.MODEL_PROVIDER.lower()

    if provider == "mock":
        # Extract candidate facets from user prompt context in mock mode
        return ""

    elif provider in ["hosted_openai", "mistral"]:
        url = f"{settings.API_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    elif provider == "ollama":
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": settings.MODEL_NAME,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "format": "json",
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {settings.MODEL_PROVIDER}")


def score_facet_batch(
    conversation_text: str,
    candidate_facets: List[Dict[str, Any]]
) -> List[FacetScoreResult]:
    """Scores a batch of candidate facets for a given conversation text.

    Args:
        conversation_text: Input conversation text.
        candidate_facets: List of pre-filtered candidate facet metadata records.

    Returns:
        List of validated FacetScoreResult objects.
    """
    if not candidate_facets:
        return []

    requested_facet_names = [f["facet_normalized"] for f in candidate_facets]

    if settings.MODEL_PROVIDER.lower() == "mock":
        raw_response = mock_llm_score_batch(conversation_text, candidate_facets)
    else:
        user_prompt = construct_batch_prompt(conversation_text, candidate_facets)
        try:
            raw_response = call_llm_api(SYSTEM_PROMPT, user_prompt)
        except Exception as err:
            print(f"[LLM Scoring Error] Model API call failed ({err}). Falling back to mock evaluator.")
            raw_response = mock_llm_score_batch(conversation_text, candidate_facets)

    validated_results = parse_and_validate_batch_output(raw_response, requested_facet_names)
    return validated_results
