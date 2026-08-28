"""Unit tests for facet preprocessing module."""

import os
# pyrefly: ignore [missing-import]
from src.preprocessing import normalize_facet, is_header_or_noise, preprocess_facets
# pyrefly: ignore [missing-import]
from src.taxonomy import classify_facet

def test_normalize_facet():
    assert normalize_facet("  Communication Skill  ") == "communication skill"
    assert normalize_facet("COMMUNICATION SKILL") == "communication skill"
    assert normalize_facet("  ") == ""
    assert normalize_facet(None) == ""

def test_is_header_or_noise():
    assert is_header_or_noise("FACET_NAME,CATEGORY,DESCRIPTION") is True
    assert is_header_or_noise("---") is True
    assert is_header_or_noise("INVALID_ROW_###") is True
    assert is_header_or_noise("   ") is True
    assert is_header_or_noise("confidence") is False

def test_taxonomy_classification():
    facet_type, observable, reason = classify_facet("blood pressure", "medical")
    assert facet_type == "medical"
    assert observable is False
    assert "Medical measurements" in reason

    facet_type_comm, obs_comm, _ = classify_facet("communication skill", "communication")
    assert facet_type_comm == "communication"
    assert obs_comm is True

def test_preprocess_facets_pipeline(tmp_path):
    raw_csv = tmp_path / "raw.csv"
    proc_csv = tmp_path / "proc.csv"
    
    raw_csv.write_text(
        "facet_raw,category,notes\n"
        "confidence,behavioral,ok\n"
        "  confidence  ,behavioral,dup\n"
        "blood pressure,medical,lab\n"
        "FACET_NAME,CATEGORY,DESCRIPTION\n"
        "---\n"
    )
    
    df_out = preprocess_facets(str(raw_csv), str(proc_csv))
    assert len(df_out) == 2  # 'confidence' and 'blood pressure'
    assert "confidence" in df_out["facet_normalized"].values
    assert "blood pressure" in df_out["facet_normalized"].values
    assert os.path.exists(proc_csv)
