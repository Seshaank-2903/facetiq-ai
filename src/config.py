import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def _clean(val: Optional[str], default: str = "") -> str:
    if val is None or not val:
        return default
    return val.split("#")[0].strip()

def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets (Streamlit Cloud) or environment variables (local/.env)."""
    # Try Streamlit secrets first (works on Streamlit Cloud)
    try:
        import streamlit as st
        val = st.secrets.get(key, None)
        if val:
            return _clean(str(val), default)
    except Exception:
        pass
    # Fall back to environment variable / .env file
    return _clean(os.getenv(key), default)

@dataclass
class Settings:
    MODEL_NAME: str = field(default_factory=lambda: _get_secret("MODEL_NAME", "mistral-small-latest"))
    MODEL_PROVIDER: str = field(default_factory=lambda: _get_secret("MODEL_PROVIDER", "mistral"))
    API_KEY: str = field(default_factory=lambda: _get_secret("API_KEY", ""))
    API_BASE_URL: str = field(default_factory=lambda: _get_secret("API_BASE_URL", "https://api.mistral.ai/v1"))

    TOP_K_RETRIEVAL: int = field(default_factory=lambda: int(_get_secret("TOP_K_RETRIEVAL", "30")))
    SCORING_BATCH_SIZE: int = field(default_factory=lambda: int(_get_secret("SCORING_BATCH_SIZE", "10")))
    EMBEDDING_MODEL: str = field(default_factory=lambda: _get_secret("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))

    BASE_DIR: str = field(default_factory=lambda: os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    @property
    def RAW_DATA_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "raw", "facets.csv")

    @property
    def PROCESSED_DATA_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "processed", "enriched_facets.csv")

    @property
    def INDEX_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "processed", "facets_index.faiss")

    @property
    def BENCHMARK_CONVERSATIONS_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "benchmark", "conversations.json")

    @property
    def BENCHMARK_LABELS_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "benchmark", "reference_labels.json")

settings = Settings()
