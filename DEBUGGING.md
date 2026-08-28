# DEBUGGING.md — Real Issues, Failed Assumptions & Diagnostic Records

This document records real engineering issues, unexpected failure modes, and root-cause diagnostic steps encountered during development and testing.

---

## Issue 1: Module Import Failures During Standalone Pytest Execution

### Symptom
Executing `pytest` from the command line resulted in 4 collection errors:
`ModuleNotFoundError: No module named 'src'` across `test_abstention.py`, `test_preprocessing.py`, `test_retrieval.py`, and `test_validation.py`.

### Diagnosis
Running `pytest` directly invokes the standalone pytest runner script, which does not automatically append the current working directory (`.`) to Python's `sys.path` when test files import `src.pipeline` or `src.retrieval`.

### Root Cause
Python's import resolution mechanism requires the project root to be present in `sys.path`. When pytest is invoked as `pytest`, Python executes the pytest entry point executable rather than running Python from the root directory context.

### Fix
In `conftest.py` (and when running via `python -m pytest`), explicitly insert the repository root into `sys.path`:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
```

### Verification
Ran `python -m pytest` in terminal. All 13 tests passed cleanly (`13 passed in 14.43s`).

---

## Issue 2: Malformed JSON Output & Markdown Code Block Wrapping from LLM API

### Symptom
Batch LLM scoring calls occasionally triggered runtime exceptions during JSON parsing:
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`.

### Diagnosis
Inspecting raw LLM completion payloads revealed that certain model providers (e.g. Mistral / Groq) wrapped their JSON responses in markdown code fences:
````
```json
[
  {"facet": "presentation_skills", "score": 4, "confidence": 0.9}
]
```
````

### Root Cause
Standard `json.loads()` cannot parse strings prefixed with backtick markdown headers (```` ```json ````) or containing trailing conversational commentary.

### Fix
Created `extract_json_payload` in `src/validation.py` using regular expression extraction:
```python
def extract_json_payload(text: str) -> str:
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
```
Additionally, `validate_and_repair_facet_result` safe-checks every score field and injects default abstention fallbacks (`status: "insufficient_evidence"`, `score: None`) if a required key is missing or malformed.

### Verification
Executed `tests/test_validation.py` against raw markdown-wrapped JSON payloads (`3 passed`).
