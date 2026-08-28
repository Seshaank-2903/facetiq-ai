"""Master Facet Scoring Pipeline.

End-to-end orchestration: Retrieval -> Observability/Safety Filtering ->
Batched LLM Scoring -> Output Validation & Formatting.
"""

from typing import Dict, Any, Optional
import math

try:
    from .config import settings
    from .retrieval import FacetRetriever
    from .abstention import check_observability_and_safety
    from .scoring import score_facet_batch
    from .schemas import FacetScoreResult
except ImportError:
    # pyrefly: ignore [missing-import]
    from src.config import settings
    # pyrefly: ignore [missing-import]
    from src.retrieval import FacetRetriever
    from src.abstention import check_observability_and_safety
    from src.scoring import score_facet_batch
    from src.schemas import FacetScoreResult


class FacetScoringPipeline:
    def __init__(self, retriever: Optional[FacetRetriever] = None):
        self.retriever = retriever or FacetRetriever()
        self.retriever.build_or_load_index()

    def process_conversation(
        self,
        conversation_text: str,
        top_k: Optional[int] = None,
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Runs the complete pipeline for a single conversation snippet.

        Args:
            conversation_text: Input conversation string.
            top_k: Number of candidate facets to retrieve (default: settings.TOP_K_RETRIEVAL).
            batch_size: Number of facets per LLM scoring call (default: settings.SCORING_BATCH_SIZE).

        Returns:
            Dictionary containing:
                - conversation: input text
                - retrieved_candidates_count: total candidates retrieved from FAISS
                - scorable_candidates_count: candidates passing safety/observability filter
                - pre_abstained_count: candidates rejected by observability filter
                - llm_calls_made: total batched LLM calls executed
                - results: list of serialized FacetScoreResult dictionaries
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        batch_size = batch_size or settings.SCORING_BATCH_SIZE

        # Step 1: Retrieval
        retrieved_facets = self.retriever.retrieve(conversation_text, top_k=top_k)

        # Step 2: Observability & Safety Filtering
        scorable_facets = []
        final_results = []
        pre_abstained_count = 0

        for f in retrieved_facets:
            is_scorable, status, reason = check_observability_and_safety(f, conversation_text)
            if is_scorable:
                scorable_facets.append(f)
            else:
                pre_abstained_count += 1
                final_results.append(
                    FacetScoreResult(
                        facet=f["facet_normalized"],
                        status=status,
                        score=None,
                        confidence=0.95,
                        evidence=None,
                        reason=reason
                    )
                )

        # Step 3: Batched LLM Scoring
        num_batches = math.ceil(len(scorable_facets) / batch_size) if scorable_facets else 0
        llm_calls_made = 0

        for i in range(num_batches):
            batch = scorable_facets[i * batch_size : (i + 1) * batch_size]
            batch_results = score_facet_batch(conversation_text, batch)
            final_results.extend(batch_results)
            llm_calls_made += 1

        # Step 4: Serialize results
        serialized_results = [r.model_dump() for r in final_results]

        return {
            "conversation": conversation_text,
            "retrieved_candidates_count": len(retrieved_facets),
            "scorable_candidates_count": len(scorable_facets),
            "pre_abstained_count": pre_abstained_count,
            "llm_calls_made": llm_calls_made,
            "results": serialized_results
        }
