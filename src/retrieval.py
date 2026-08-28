"""FAISS Vector Retrieval Module.

Builds a local FAISS index over precomputed facet embeddings and retrieves top-K
candidate facets relevant to conversation text.
"""

import os
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd

# pyrefly: ignore [missing-import]
from src.config import settings
# pyrefly: ignore [missing-import]
from src.embeddings import encode_texts

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("[Retrieval Warning] faiss-cpu not available. Using NumPy Cosine Similarity Fallback.")


class FacetRetriever:
    def __init__(self, processed_facets_path: Optional[str] = None):
        self.processed_path = processed_facets_path or settings.PROCESSED_DATA_PATH
        self.df_facets: Optional[pd.DataFrame] = None
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index = None

    def build_or_load_index(self, force_rebuild: bool = False):
        """Loads processed facets, generates embeddings, and constructs vector index."""
        if not force_rebuild and self.df_facets is not None and self.embeddings is not None:
            return

        if os.path.exists(self.processed_path) and not (force_rebuild and self.processed_path == settings.PROCESSED_DATA_PATH):
            self.df_facets = pd.read_csv(self.processed_path)
        else:
            from src.preprocessing import preprocess_facets
            self.df_facets = preprocess_facets(output_path=self.processed_path)

        if self.df_facets.empty:
            raise ValueError("Processed facets dataframe is empty.")

        # Prepare facet text representation for indexing
        facet_texts = [
            f"{row['facet_normalized']}: {row['scoring_definition']}"
            for _, row in self.df_facets.iterrows()
        ]

        # Encode facets
        self.embeddings = encode_texts(facet_texts)
        dim = self.embeddings.shape[1]

        if HAS_FAISS:
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(self.embeddings)
            print(f"[Retrieval] Built FAISS Index (IndexFlatIP) with {len(self.df_facets)} facets (Dim={dim}).")
        else:
            self.faiss_index = None

    def retrieve(self, conversation_text: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves top-K candidate facets for a given conversation text.

        Args:
            conversation_text: Raw conversation string.
            top_k: Number of candidate facets to return (default: settings.TOP_K_RETRIEVAL).

        Returns:
            List of facet records enriched with similarity score.
        """
        if self.df_facets is None or self.embeddings is None:
            self.build_or_load_index()

        if self.df_facets is None or self.df_facets.empty or self.embeddings is None:
            return []

        k = top_k or settings.TOP_K_RETRIEVAL
        k = max(1, min(k, len(self.df_facets)))

        conv_str = conversation_text if isinstance(conversation_text, str) else str(conversation_text or "")
        query_vec = encode_texts([conv_str])

        if HAS_FAISS and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query_vec, k)
            top_indices = indices[0]
            top_scores = scores[0]
        else:
            # NumPy Cosine Similarity fallback - reshape to 1D array to avoid 0D scalar squeeze errors when N=1
            similarities = np.dot(self.embeddings, query_vec.T).reshape(-1)
            top_indices = np.argsort(similarities)[::-1][:k]
            top_scores = similarities[top_indices]

        results = []
        for idx, score in zip(top_indices, top_scores):
            if idx < 0 or idx >= len(self.df_facets):
                continue
            row = self.df_facets.iloc[idx].to_dict()
            row["retrieval_score"] = float(score)
            results.append(row)

        return results
