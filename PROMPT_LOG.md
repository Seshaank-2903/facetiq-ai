# PROMPT_LOG.md — AI Usage Log & Supervision Evidence

This document records the material AI prompts, tools, decisions, and manual code corrections executed during the development of the FacetIQ platform.

---

## 🤖 Material AI Prompts & Iterations

### 1. Vector Index & Facet Retrieval System
- **Tool / Model**: Antigravity / Gemini 3.6 Flash
- **Prompt**: *"Design a semantic candidate retrieval engine using FAISS and sentence-transformers to index facet definitions from CSV files."*
- **What Was Used**: Implemented `FacetRetriever` class with L2 vector similarity indexing over normalized facet definitions.
- **What Was Changed**: Modified similarity threshold from strict distance cutoff to top-K dynamic retrieval (`TOP_K_RETRIEVAL=30`), ensuring broad candidate recall prior to LLM evaluation.
- **Verification**: Verified using `tests/test_retrieval.py` (`3 passed`).

### 2. Observability & Safety Filter Logic
- **Tool / Model**: Antigravity / Gemini 3.6 Flash
- **Prompt**: *"Implement abstention logic to detect unobservable subjective states, sarcasm, and third-person quotes before calling LLM scoring."*
- **What Was Used**: `check_observability_and_safety` filter in `src/abstention.py`.
- **What Was Changed**: Added regex phrase matching for physiological/medical indicators and hearsay quote patterns ("my manager said", "doctor checked").
- **Verification**: Verified using `tests/test_abstention.py` (`3 passed`).

### 3. FastAPI REST Wrapper & React Frontend Design System
- **Tool / Model**: Antigravity / Gemini 3.6 Flash
- **Prompt**: *"Build a FastAPI REST server wrapping the pipeline and create a React Vite frontend with custom dark/light theme tokens."*
- **What Was Used**: Created `server.py` with `/api/analyze`, `/api/catalog`, `/api/system`, `/api/evaluate` endpoints, and a Vite React frontend in `frontend/`.
- **What Was Changed**: Updated dark mode theme tokens from navy/blue slate (`#0f172a`, `#1e293b`) to neutral dark charcoal (`#09090b`, `#18181c`) per user styling feedback.
- **Verification**: Tested API via `urllib.request` and verified React app renders cleanly on `http://localhost:5173`.

---

## ❌ What AI Got Wrong & What I Corrected

### Example 1: CSS f-string Variable Interpolation Bug in Python
- **Symptom / AI Error**: When generating dynamic CSS in `app.py`, the AI introduced single curly braces inside a Python f-string (`.deploy-style-theme-btn div.stButton > button { background-color: {ACCENT_BLUE} ... }`).
- **Root Cause**: Python's f-string parser tried to interpret `{ background-color: {ACCENT_BLUE} }` as a Python dictionary expression, raising a `NameError: name 'background' is not defined`.
- **Correction**: Escaped all literal CSS curly braces with double braces `{{ ... }}` while preserving single braces `{ACCENT_BLUE}` for Python variable interpolation.

### Example 2: Strict JSON Parsing Failure on LLM Markdown Code Block Wrapping
- **Symptom / AI Error**: The LLM occasionally returned JSON wrapped in triple backtick markdown blocks (````json { ... } `````), which broke `json.loads()`.
- **Root Cause**: Standard `json.loads()` fails when string contains markdown code block wrappers or leading prose.
- **Correction**: Built `extract_json_payload` and `validate_and_repair_facet_result` in `src/validation.py` using regular expressions to extract clean JSON payloads and supply fallback abstention schemas if parsing fails.
