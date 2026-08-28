"""Benchmark Evaluation Module.

Evaluates pipeline predictions against human-reviewed ground truth reference labels,
reporting score agreement, abstention accuracy, and common failure modes.
"""

import os
import json
from typing import Dict, Any

from src.config import settings
from src.pipeline import FacetScoringPipeline


def run_benchmark_evaluation(
    conversations_path: str = None,
    labels_path: str = None,
    output_report_path: str = None
) -> Dict[str, Any]:
    """Runs evaluation on benchmark conversations and calculates agreement metrics.

    Args:
        conversations_path: Path to conversations.json.
        labels_path: Path to reference_labels.json.
        output_report_path: Path to save output benchmark report.

    Returns:
        Evaluation metrics dictionary.
    """
    conversations_path = conversations_path or settings.BENCHMARK_CONVERSATIONS_PATH
    labels_path = labels_path or settings.BENCHMARK_LABELS_PATH
    output_report_path = output_report_path or os.path.join(settings.BASE_DIR, "outputs", "benchmark_results.json")

    if not os.path.exists(conversations_path) or not os.path.exists(labels_path):
        raise FileNotFoundError("Benchmark conversations or reference labels JSON file not found.")

    with open(conversations_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    with open(labels_path, "r", encoding="utf-8") as f:
        labels_data = json.load(f)
        reference_labels = labels_data.get("labels", [])

    conv_map = {c["id"]: c["text"] for c in conversations}
    pipeline = FacetScoringPipeline()

    total_evaluated = 0
    correct_score_agreements = 0
    incorrect_scores = 0
    correct_abstentions = 0
    incorrect_abstentions = 0

    detailed_comparisons = []
    failure_modes = []

    # Map labels by conversation_id and facet
    for ref in reference_labels:
        conv_id = ref["conversation_id"]
        facet_target = ref["facet"].lower().strip()
        exp_status = ref["expected_status"]
        exp_score = ref.get("expected_score")
        text = conv_map.get(conv_id, "")

        if not text:
            continue

        total_evaluated += 1

        # Run pipeline prediction
        pipe_output = pipeline.process_conversation(text, top_k=settings.TOP_K_RETRIEVAL)
        pred_results = pipe_output["results"]

        # Find predicted record matching facet_target
        pred_match = None
        for res in pred_results:
            if res["facet"].lower().strip() == facet_target:
                pred_match = res
                break

        if not pred_match:
            # If not retrieved or scored, treat as abstained
            pred_status = "insufficient_evidence"
            pred_score = None
            pred_reason = "Facet not retrieved in top-K candidate set."
        else:
            pred_status = pred_match["status"]
            pred_score = pred_match.get("score")
            pred_reason = pred_match.get("reason") or pred_match.get("evidence")

        # Evaluate Agreement
        is_abstention_correct = False
        is_score_correct = False

        if exp_status in ["not_observable", "insufficient_evidence"]:
            if pred_status in ["not_observable", "insufficient_evidence"]:
                correct_abstentions += 1
                is_abstention_correct = True
            else:
                incorrect_scores += 1
                failure_modes.append(f"False Positive Score: '{facet_target}' in '{conv_id}' (Expected Abstain, got Score {pred_score})")
        else:
            # Expected to be scored
            if pred_status == "scored":
                if pred_score == exp_score or (exp_score is not None and abs(pred_score - exp_score) <= 1):
                    correct_score_agreements += 1
                    is_score_correct = True
                else:
                    incorrect_scores += 1
                    failure_modes.append(f"Score Variance: '{facet_target}' in '{conv_id}' (Expected {exp_score}, got {pred_score})")
            else:
                incorrect_abstentions += 1
                failure_modes.append(f"False Abstention: '{facet_target}' in '{conv_id}' (Expected Score {exp_score}, got {pred_status})")

        detailed_comparisons.append({
            "conversation_id": conv_id,
            "facet": facet_target,
            "expected_status": exp_status,
            "expected_score": exp_score,
            "predicted_status": pred_status,
            "predicted_score": pred_score,
            "is_match": is_score_correct or is_abstention_correct,
            "predicted_reason_or_evidence": pred_reason
        })

    accuracy_pct = round(((correct_score_agreements + correct_abstentions) / max(1, total_evaluated)) * 100, 2)

    report = {
        "summary": {
            "total_reference_labels": total_evaluated,
            "correct_score_agreements": correct_score_agreements,
            "incorrect_scores": incorrect_scores,
            "correct_abstentions": correct_abstentions,
            "incorrect_abstentions": incorrect_abstentions,
            "overall_accuracy_percentage": accuracy_pct
        },
        "failure_analysis": failure_modes,
        "detailed_comparisons": detailed_comparisons
    }

    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n================ BENCHMARK EVALUATION REPORT ================")
    print(f"Total Reference Labels Evaluated : {total_evaluated}")
    print(f"Correct Score Agreements         : {correct_score_agreements}")
    print(f"Incorrect Scores                 : {incorrect_scores}")
    print(f"Correct Abstentions              : {correct_abstentions}")
    print(f"Incorrect Abstentions            : {incorrect_abstentions}")
    print(f"Overall Accuracy Percentage      : {accuracy_pct}%")
    print(f"Full Report Saved To             : {output_report_path}")
    print("=============================================================\n")

    return report


if __name__ == "__main__":
    run_benchmark_evaluation()
