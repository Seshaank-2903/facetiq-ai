"""Unit tests for vector retrieval and embedding modules."""

import pandas as pd
# pyrefly: ignore [missing-import]
from src.retrieval import FacetRetriever
# pyrefly: ignore [missing-import]
from src.embeddings import encode_texts


def test_encode_texts():
    texts = ["confidence in presentation", "blood pressure measurement"]
    embeddings = encode_texts(texts)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] > 0

    # Single string input handling
    emb_single = encode_texts("single string test")
    assert emb_single.shape[0] == 1

    # Empty input handling
    emb_empty = encode_texts([])
    assert emb_empty.shape[0] == 0


def test_facet_retriever():
    retriever = FacetRetriever()
    retriever.build_or_load_index()

    results = retriever.retrieve("I gave a great presentation and felt confident", top_k=5)
    assert len(results) > 0
    assert "facet_normalized" in results[0]
    assert "retrieval_score" in results[0]


def test_retriever_single_facet_edge_case(tmp_path):
    # Test N=1 dataset edge case to ensure no 0D array squeeze errors
    csv_path = tmp_path / "single_facet.csv"
    df = pd.DataFrame([{
        "facet_raw": "confidence",
        "facet_normalized": "confidence",
        "facet_type": "behavioral",
        "conversation_observable": True,
        "sensitivity": "low",
        "scoring_definition": "Evaluate confidence level on a 1-5 scale.",
        "abstention_reason": ""
    }])
    df.to_csv(csv_path, index=False)

    retriever = FacetRetriever(processed_facets_path=str(csv_path))
    retriever.build_or_load_index(force_rebuild=True)

    results = retriever.retrieve("I was feeling very confident today", top_k=1)
    assert len(results) == 1
    assert results[0]["facet_normalized"] == "confidence"
    assert "retrieval_score" in results[0]
