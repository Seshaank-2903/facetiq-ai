"""Reproducible Facet Preprocessing Pipeline.

Reads raw facet CSV, normalizes strings, filters malformed noise/duplicates/headers,
applies taxonomy rules, and outputs enriched facets to CSV.
"""

import os
import re
import pandas as pd

from src.config import settings
from src.taxonomy import classify_facet

HEADER_KEYWORDS = {"facet_raw", "category", "description", "facet_name"}
NOISE_PATTERNS = [r"^[\-\_\#\*\s]+$", r"invalid\_row", r"unknown\_facet"]


def is_header_or_noise(raw_val: str) -> bool:
    """Detects header-like or corrupted noise strings."""
    if not isinstance(raw_val, str):
        return True
    val_clean = raw_val.strip().lower()
    if not val_clean:
        return True
    if val_clean in ["facet_raw", "facet_name", "facet", "category", "description", "notes"]:
        return True
    if any(hk in val_clean for hk in HEADER_KEYWORDS) and "," in val_clean:
        return True
    for pat in NOISE_PATTERNS:
        if re.search(pat, val_clean):
            return True
    return False


def normalize_facet(raw_val: str) -> str:
    """Normalizes raw facet text by trimming whitespace and lowercasing."""
    if not isinstance(raw_val, str):
        return ""
    # Strip whitespace and collapse internal multi-spaces
    clean = re.sub(r"\s+", " ", raw_val.strip().lower())
    return clean


def generate_scoring_definition(facet_norm: str, facet_type: str) -> str:
    """Generates standard scoring guidance anchor for LLM prompt context."""
    return f"Evaluate degree of conversational evidence supporting {facet_norm} (Type: {facet_type}) on a 1-5 scale."


def preprocess_facets(input_path: str = None, output_path: str = None) -> pd.DataFrame:
    """Runs the complete end-to-end preprocessing pipeline on raw facet CSV.

    Args:
        input_path: Path to raw facets.csv.
        output_path: Path to write enriched_facets.csv.

    Returns:
        Processed pandas DataFrame.
    """
    input_path = input_path or settings.RAW_DATA_PATH
    output_path = output_path or settings.PROCESSED_DATA_PATH

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw facets file not found at: {input_path}")

    try:
        df_raw = pd.read_csv(input_path, skip_blank_lines=False, on_bad_lines="skip", engine="python")
    except Exception as e:
        print(f"[Preprocessing Warning] Direct pandas read failed ({e}). Fallback line-by-line reading.")
        # Fallback reading line by line
        rows = []
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            header = f.readline().strip().split(",")
            for line in f:
                parts = line.strip().split(",")
                rows.append({"facet_raw": parts[0] if parts else "", "category": parts[1] if len(parts) > 1 else "", "notes": parts[2] if len(parts) > 2 else ""})
        df_raw = pd.DataFrame(rows)
    
    enriched_rows = []
    seen_normalized = set()

    for idx, row in df_raw.iterrows():
        raw_val = str(row.get("facet_raw", "")) if pd.notna(row.get("facet_raw")) else ""
        raw_cat = str(row.get("category", "")) if pd.notna(row.get("category")) else ""

        # Step 1: Detect blank or header noise
        if is_header_or_noise(raw_val):
            continue

        # Step 2: Normalize string
        norm_val = normalize_facet(raw_val)

        if not norm_val:
            continue

        # Step 3: Deduplicate
        if norm_val in seen_normalized:
            continue
        seen_normalized.add(norm_val)

        # Step 4: Taxonomy Classification
        facet_type, observable, default_reason = classify_facet(norm_val, raw_cat)

        # Step 5: Assign Sensitivity
        if facet_type in ["sensitive", "financial"]:
            sensitivity = "high"
        elif facet_type in ["medical", "biographical"]:
            sensitivity = "medium"
        else:
            sensitivity = "low"

        # Step 6: Form enriched record
        record = {
            "facet_raw": raw_val,
            "facet_normalized": norm_val,
            "facet_type": facet_type,
            "conversation_observable": observable,
            "sensitivity": sensitivity,
            "scoring_definition": generate_scoring_definition(norm_val, facet_type),
            "abstention_reason": default_reason
        }
        enriched_rows.append(record)

    df_enriched = pd.DataFrame(enriched_rows)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_enriched.to_csv(output_path, index=False)
    print(f"[Preprocessing] Successfully generated enriched facets at: {output_path} ({len(df_enriched)} valid rows)")
    
    return df_enriched


if __name__ == "__main__":
    preprocess_facets()
