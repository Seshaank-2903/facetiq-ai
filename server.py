"""FastAPI Server for FacetIQ React Frontend Integration.

Preserves existing Python backend logic (src.pipeline, src.evaluate, etc.) while
exposing clean REST API endpoints for the modern React web interface.
"""

import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.pipeline import FacetScoringPipeline
from src.evaluate import run_benchmark_evaluation
from src.config import settings
from src.retrieval import FacetRetriever

app = FastAPI(
    title="FacetIQ API",
    description="AI Conversation Facet Evaluation Platform Backend API",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton pipeline instance
_pipeline: Optional[FacetScoringPipeline] = None

def get_pipeline() -> FacetScoringPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = FacetScoringPipeline()
    return _pipeline


class AnalyzeRequest(BaseModel):
    conversation: str
    top_k: Optional[int] = None
    batch_size: Optional[int] = None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/system")
def get_system_config():
    return {
        "model_provider": settings.MODEL_PROVIDER,
        "model_name": settings.MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL,
        "top_k_retrieval": settings.TOP_K_RETRIEVAL,
        "scoring_batch_size": settings.SCORING_BATCH_SIZE,
        "environment": "enterprise"
    }


@app.post("/api/analyze")
def analyze_conversation(req: AnalyzeRequest):
    if not req.conversation or not req.conversation.strip():
        raise HTTPException(status_code=400, detail="Conversation text cannot be empty.")
    
    start_time = time.time()
    pipeline = get_pipeline()
    result = pipeline.process_conversation(
        conversation_text=req.conversation,
        top_k=req.top_k or settings.TOP_K_RETRIEVAL,
        batch_size=req.batch_size or settings.SCORING_BATCH_SIZE
    )
    result["latency_sec"] = round(time.time() - start_time, 2)
    return result


@app.get("/api/catalog")
def get_facet_catalog(search: Optional[str] = None, observable_only: Optional[bool] = False):
    pipeline = get_pipeline()
    df = pipeline.retriever.df_facets.copy()
    
    if observable_only:
        df = df[df["conversation_observable"] == True]
    
    if search and search.strip():
        q = search.lower().strip()
        df = df[df["facet_normalized"].str.contains(q, na=False)]

    records = df.to_dict(orient="records")
    # Clean up NaNs for JSON serialization
    for r in records:
        for k, v in r.items():
            if str(v) == "nan" or (isinstance(v, float) and (v != v)):
                r[k] = None

    return {
        "total": len(records),
        "facets": records
    }


@app.post("/api/evaluate")
def run_evaluation():
    try:
        start_time = time.time()
        res = run_benchmark_evaluation()
        return {
            "status": "success",
            "latency_sec": round(time.time() - start_time, 2),
            "results": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
