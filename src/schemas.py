"""Pydantic v2 data models for structured output validation."""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field, model_validator


class FacetScoreResult(BaseModel):
    """Schema for individual facet score or abstention result."""
    facet: str = Field(..., min_length=1, description="Normalized name of the facet")
    status: Literal["scored", "insufficient_evidence", "not_observable"] = Field(
        ..., description="Evaluation status"
    )
    score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Ordinal integer score 1-5 when status='scored', else null"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level between 0.0 and 1.0"
    )
    evidence: Optional[str] = Field(
        default=None,
        description="Conversational evidence snippet supporting the score"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Explicit reason for abstention when evidence is insufficient or non-observable"
    )

    @model_validator(mode="after")
    def validate_score_status_consistency(self):
        """Enforces that score is non-null iff status is 'scored'."""
        if self.status == "scored":
            if self.score is None:
                raise ValueError("Score must be an integer between 1 and 5 when status is 'scored'.")
        else:
            if self.score is not None:
                # Auto-repair score to None when abstaining
                self.score = None
        return self


class BatchScoreOutput(BaseModel):
    """Schema for batch LLM JSON response."""
    results: List[FacetScoreResult]
