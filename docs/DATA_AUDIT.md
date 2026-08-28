# Data Audit Report — `facets.csv`

## Executive Summary
This document provides an empirical audit of the raw dataset stored at `data/raw/facets.csv`. The audit evaluates dataset structure, row counts, schema consistency, data quality anomalies, and facet category heterogeneity prior to pipeline preprocessing.

---

## 1. File & Schema Overview
- **File Location**: `data/raw/facets.csv`
- **Total Raw Lines**: 61 (1 header + 60 data rows)
- **Detected Columns**:
  1. `facet_raw`: Raw string value of the facet.
  2. `category`: Raw category label provided in input.
  3. `notes`: Contextual description or measurement unit.

---

## 2. Quality & Anomaly Breakdown

| Anomaly Type | Count | Example Raw Entries | Pipeline Handling Strategy |
| :--- | :---: | :--- | :--- |
| **Leading/Trailing Whitespace** | 2 | `" communication skill "`, `"   "` | Strip whitespace via `.strip()` |
| **Case Inconsistencies** | 2 | `"COMMUNICATION SKILL"`, `"confidence"` | Normalize to lowercase (`.lower()`) |
| **Exact Duplicates** | 2 | `"blood pressure"`, `"COMMUNICATION SKILL"` (after normalization) | Deduplicate keeping first valid instance |
| **Header-like Entries** | 1 | `"FACET_NAME,CATEGORY,DESCRIPTION"` | Filter using header keyword matching |
| **Blank / Empty Rows** | 1 | `"   ,,"` | Drop rows where normalized value length is 0 |
| **Malformed / Corrupted Lines**| 2 | `"---"`, `"INVALID_ROW_###"` | Filter out non-alphanumeric noise patterns |
| **Clean Scorable Facets** | 50 | `"confidence"`, `"presentation skill"` | Retain for enrichment & indexing |

---

## 3. Category Heterogeneity Audit

The raw dataset spans multiple domain types requiring distinct scoring and safety treatment:

1. **Directly Observable Conversational Attributes**:
   - Communication: `communication skill`, `presentation skill`, `listening skill`, `spoken english fluency`.
   - Behavioral & Emotional: `confidence`, `leadership`, `stress`, `anxiety`, `frustration level`.
   - Demonstrated Skills: `problem solving`, `python programming competence`, `SQL query writing`.

2. **Non-Observable Medical / Clinical Attributes (Hallucination Traps)**:
   - Lab Measurements: `blood pressure` (mmHg), `cholesterol level` (mg/dL), `heart rate` (BPM).
   - Diagnoses: `diabetes diagnosis`, `depression diagnosis`, `medical conditions`.
   - *Policy*: Reject from direct LLM inference unless explicit clinical test values are stated in text.

3. **Third-Person & External Facts**:
   - Third-Person Context: `father's employment status`, `friend's salary`, `mother's medical history`, `manager rating`.
   - *Policy*: Abstain because evidence pertains to external entities, not the speaker.

4. **Private / Sensitive Financial & Biographical Attributes**:
   - Financial: `bank account balance`, `credit score`, `salary expectations`.
   - Sensitive: `criminal record`, `political affiliation`, `religious background`, `home address`.
   - *Policy*: Flag as non-observable without direct, explicit self-disclosure.

---

## 4. Conclusion & Next Steps
The dataset contains structured noise, duplicate entries, malformed syntax, and high category heterogeneity.
A reproducible Python preprocessing pipeline (`src/preprocessing.py`) will normalize, filter, and enrich these raw facets into `data/processed/enriched_facets.csv`.
