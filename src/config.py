import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def _clean(val: Optional[str], default: str = "") -> str:
    if val is None or not val:
        return default
    return val.split("#")[0].strip()

@dataclass
class Settings:
    MODEL_NAME: str = _clean(os.getenv("MODEL_NAME"), "mistral-small-latest")
    MODEL_PROVIDER: str = _clean(os.getenv("MODEL_PROVIDER"), "mistral")  # mistral, hosted_openai, mock, ollama
    API_KEY: str = _clean(os.getenv("API_KEY"), "")
    API_BASE_URL: str = _clean(os.getenv("API_BASE_URL"), "https://api.mistral.ai/v1")
    
    TOP_K_RETRIEVAL: int = int(_clean(os.getenv("TOP_K_RETRIEVAL"), "30"))
    SCORING_BATCH_SIZE: int = int(_clean(os.getenv("SCORING_BATCH_SIZE"), "10"))
    EMBEDDING_MODEL: str = _clean(os.getenv("EMBEDDING_MODEL"), "BAAI/bge-small-en-v1.5")
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    RAW_DATA_PATH: str = os.path.join(BASE_DIR, "data", "raw", "facets.csv")
    PROCESSED_DATA_PATH: str = os.path.join(BASE_DIR, "data", "processed", "enriched_facets.csv")
    INDEX_PATH: str = os.path.join(BASE_DIR, "data", "processed", "facets_index.faiss")
    
    BENCHMARK_CONVERSATIONS_PATH: str = os.path.join(BASE_DIR, "data", "benchmark", "conversations.json")
    BENCHMARK_LABELS_PATH: str = os.path.join(BASE_DIR, "data", "benchmark", "reference_labels.json")

settings = Settings()
