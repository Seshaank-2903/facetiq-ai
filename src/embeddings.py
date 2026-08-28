"""Embedding generator module.

Uses SentenceTransformers (BAAI/bge-small-en-v1.5 or all-MiniLM-L6-v2) for dense text embeddings,
with a deterministic fallback encoder for offline/constrained environments.
"""

import hashlib
from typing import List, Union
import numpy as np

from src.config import settings

_model_instance = None


def get_embedding_model():
    """Lazy loader for SentenceTransformer model with fallback."""
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    try:
        from sentence_transformers import SentenceTransformer
        print(f"[Embeddings] Loading SentenceTransformer model: {settings.EMBEDDING_MODEL}")
        _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL)
        return _model_instance
    except Exception as e:
        print(f"[Embeddings Warning] Could not load SentenceTransformer ({e}). Using Fallback Hash Encoder.")
        _model_instance = "fallback"
        return _model_instance


def encode_texts(texts: Union[List[str], str]) -> np.ndarray:
    """Encodes text or list of texts into normalized float32 embedding vectors.

    Args:
        texts: Input string or list of input strings.

    Returns:
        np.ndarray of shape (len(texts), dim) normalized L2.
    """
    if isinstance(texts, str):
        texts = [texts]
    elif not texts:
        return np.empty((0, 384), dtype=np.float32)

    clean_texts = [str(t) if t is not None else "" for t in texts]

    model = get_embedding_model()
    
    if model != "fallback":
        try:
            embeddings = model.encode(clean_texts, convert_to_numpy=True, show_progress_bar=False)
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings, dtype=np.float32)
            # L2 Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1e-10
            normalized = embeddings / norms
            return normalized.astype(np.float32)
        except Exception as err:
            print(f"[Embeddings Warning] Model encoding failed ({err}). Falling back to hash vectorizer.")

    # Deterministic fallback hashing vectorizer (384 dimensional) for offline/testing guarantees
    dim = 384
    matrix = np.zeros((len(clean_texts), dim), dtype=np.float32)
    for i, txt in enumerate(clean_texts):
        words = txt.lower().split()
        for w in words:
            # Deterministic MD5 hash integer mapping
            idx = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % dim
            matrix[i, idx] += 1.0
        norm = np.linalg.norm(matrix[i])
        if norm > 0:
            matrix[i] /= norm
    return matrix
