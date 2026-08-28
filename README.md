# FacetIQ — AI Conversation Facet Evaluation Platform

🌐 **Live Streamlit Application:** [https://facetiq-ai-hdclwo3bmpzwddbd3ptjrz.streamlit.app/](https://facetiq-ai-hdclwo3bmpzwddbd3ptjrz.streamlit.app/)

FacetIQ is an enterprise-grade AI conversation intelligence system designed for evaluating conversational text against defined competency and behavioral facets. The system incorporates vector semantic retrieval, observability & safety abstention logic, batched LLM scoring, and rigorous output JSON schema validation.

---

## 🎯 Architecture Summary

```
Conversation Text Input
         │
         ▼
[ FAISS Vector Index ] ──► Top-K Semantic Retrieval (BAAI/bge-small-en-v1.5)
         │
         ▼
[ Observability & Safety Filter ] ──► Pre-Abstention (Filter Unobservable / Sarcasm / Hearsay)
         │
         ▼
[ Batched LLM Scoring Pipeline ] ──► Structured Output (Groq / Gemini / Mistral LLM)
         │
         ▼
[ Validation & Repair Engine ] ──► Schema Enforcer (JSON Payload Repair & Fallback)
         │
         ▼
[ Dual UI Surfaces ] ──► React SPA (Vite + FastAPI) & Streamlit Dashboard
```

---

## 🚀 Setup & Execution Instructions

### Prerequisites
- Python 3.11+
- Node.js v18+ (for React Frontend)

### 1. Backend Server Setup
```bash
# Clone the repository
git clone https://github.com/Seshaank-2903/facetiq-ai.git
cd facetiq-ai

# Activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your LLM API keys (GROQ_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY)
```

### 2. Launch Streamlit Application (Local)
```bash
streamlit run app.py
```
*Streamlit UI runs locally on `http://localhost:8501`.*

### 3. Deploy to Streamlit Community Cloud
1. Push repository to GitHub: `https://github.com/Seshaank-2903/facetiq-ai`
2. Go to **[share.streamlit.io/deploy](https://share.streamlit.io/deploy)**
3. Configure App:
   - **Repository**: `Seshaank-2903/facetiq-ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. In **Advanced Settings → Secrets**, add:
```toml
API_KEY = "your_mistral_api_key_here"
MODEL_NAME = "mistral-small-latest"
MODEL_PROVIDER = "mistral"
API_BASE_URL = "https://api.mistral.ai/v1"
```
5. Click **Deploy**.

### 4. Launch FastAPI & React Frontend (Optional)
```bash
# Launch FastAPI backend
python -m uvicorn server:app --reload --port 8000

# Launch React frontend
cd frontend && npm install && npm run dev
```

### 4. Running CLI & Unit Tests
```bash
# CLI Single Conversation Evaluation
python main.py --conversation "I presented to the executive board and answered questions calmly."

# Run Systematic Benchmark Evaluation
python main.py --evaluate

# Run Pytest Suite
python -m pytest
```

---

## 🛡️ Safety & Abstention Mechanics
The system strictly enforces an **Evidence-First Policy**:
- **Scored**: Supported by explicit conversational evidence.
- **Insufficient Evidence**: Conversational context is vague or incomplete; system safely abstains with `score: null`.
- **Not Observable**: Internal subjective feelings, sarcasm, or third-person hearsay quotes that cannot be objectively verified.

---

## 📊 Key Features
- **Vector Retrieval**: Fast semantic candidate retrieval over catalog embeddings.
- **Batched Scoring**: Reduces LLM latency and token costs by grouping candidate facets.
- **React + FastAPI**: Sleek, high-contrast dark/light enterprise dashboard with zero blue-tinted dark surfaces.
- **Streamlit Desktop UI**: Alternative pythonic dashboard interface (`python app.py`).
- **Comprehensive Evaluation**: Automated benchmark metrics (Precision, Recall, F1, Abstention Accuracy).

---

## ⚠️ Known Limitations & Future Improvements
- **Multi-Turn Speaker Disambiguation**: Future iterations will parse multi-speaker transcript tags explicitly (`User:`, `Agent:`).
- **Online Fine-Tuning**: Fine-tuning a smaller local model (e.g. Llama-3-8B-Instruct) on domain-specific facet definitions to reduce external API dependency.
