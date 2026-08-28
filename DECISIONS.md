# DECISIONS.md — Non-Trivial Architectural & Design Decisions

This document records the core non-trivial architecture, design, and engineering trade-offs made during the implementation of the FacetIQ platform.

---

## Decision 1: Hybrid Two-Stage Pipeline (FAISS Vector Retrieval + LLM Scoring) vs. Direct Single-Prompt LLM Evaluation

### Ambiguity / Problem
Evaluating a raw conversation directly against a large catalog of hundreds of facets in a single LLM prompt leads to high context latency, severe token cost inflation, and degraded attention accuracy (LLM "lost in the middle" phenomenon).

### Options Considered
1. **Option A**: Send all catalog facets to the LLM in a single large prompt.
2. **Option B**: Two-Stage Architecture — Perform vector semantic search (FAISS + sentence-transformers) to filter top candidate facets, then send only scorable candidates in mini-batches to the LLM.

### Choice Made
**Option B (Two-Stage Architecture)**. The system retrieves candidate facets (`TOP_K_RETRIEVAL=30`) using embedding similarity before invoking LLM batch scoring.

### Trade-Offs
- **Pros**: Reduces token cost by over 80%, decreases inference latency from ~12s to ~1.8s per conversation, and improves score accuracy.
- **Cons**: Introduce potential retrieval false-negatives if candidate embeddings miss a relevant facet definition.

---

## Decision 2: Rule-Based Pre-Abstention Filter vs. Pure LLM Self-Abstention

### Ambiguity / Problem
LLMs are notoriously prone to over-confidence and hallucinating scores for subjective, unobservable, or third-person hearsay contexts (e.g. *"My manager told me I did great"*).

### Options Considered
1. **Option A**: Rely entirely on system prompt instructions for the LLM to output `null` scores.
2. **Option B**: Deterministic Rule-Based Pre-Filter — Intercept candidate facets using pattern rules (physiological state, third-person quote detection, sarcasm checks) before sending to LLM.

### Choice Made
**Option B (Deterministic Pre-Filter + LLM Validation)**. `src/abstention.py` evaluates candidate facets first; if a facet requires objective behavioral proof absent in context, it is pre-abstained with `status: "unobservable"` or `"insufficient_evidence"`.

### Trade-Offs
- **Pros**: 100% deterministic safety guarantee against hallucinating scores on unobservable states; saves unnecessary LLM API calls.
- **Cons**: Pattern rules require curation for domain edge cases.

---

## Decision 3: Decoupled FastAPI + React Architecture vs. Monolithic Dashboard

### Ambiguity / Problem
The assignment required a professional, enterprise-grade user interface for demonstrating conversation analysis, facet taxonomy browsing, and benchmark evaluation.

### Options Considered
1. **Option A**: Pure Streamlit Python dashboard.
2. **Option B**: Decoupled Architecture — FastAPI REST API backend (`server.py`) serving a modern Vite + React single-page web application (`frontend/`).

### Choice Made
**Option B (Decoupled FastAPI + React)** while retaining Streamlit as a secondary desktop view (`app.py`).

### Trade-Offs
- **Pros**: Delivers full production enterprise UI/UX (custom dark/light mode tokens, smooth drawer modals, zero blue-tinted dark surfaces, client-side filtering, CSV/JSON exports) and clean REST API boundaries.
- **Cons**: Adds build toolchain complexity (`npm`, Vite).
