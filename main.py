"""Command Line Interface (CLI) for Facet Scoring System.

Usage:
  python main.py --conversation "Text to evaluate"
  python main.py --file conversation.txt
  python main.py --evaluate
"""

import sys
import os
import json
import argparse

# pyrefly: ignore [missing-import]
from src.pipeline import FacetScoringPipeline
# pyrefly: ignore [missing-import]
from src.evaluate import run_benchmark_evaluation


def main():
    parser = argparse.ArgumentParser(description="Evaluate conversation text against facet catalog.")
    parser.add_argument("--conversation", "-c", type=str, help="Direct conversation text string to evaluate.")
    parser.add_argument("--file", "-f", type=str, help="Path to text file containing conversation text.")
    parser.add_argument("--evaluate", "-e", action="store_true", help="Run benchmark evaluation against reference labels.")
    parser.add_argument("--top-k", type=int, default=None, help="Top-K candidates to retrieve.")

    args = parser.parse_args()

    if args.evaluate:
        print("[CLI] Running Benchmark Evaluation...")
        run_benchmark_evaluation()
        return

    conversation_text = None
    if args.conversation:
        conversation_text = args.conversation
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found at '{args.file}'", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            conversation_text = f.read()

    if not conversation_text:
        # If no arguments provided, show example usage
        print("[CLI Info] No conversation text supplied. Running default sample evaluation:\n")
        conversation_text = "I gave a presentation yesterday to the executive team and answered all questions calmly and confidently."

    pipeline = FacetScoringPipeline()
    result = pipeline.process_conversation(conversation_text, top_k=args.top_k)

    # Output formatted JSON
    print(json.dumps(result, indent=2))

    # Also save to outputs/sample_scores.json
    output_sample_path = os.path.join(pipeline.retriever.processed_path, "..", "..", "outputs", "sample_scores.json")
    output_sample_path = os.path.abspath(output_sample_path)
    os.makedirs(os.path.dirname(output_sample_path), exist_ok=True)
    with open(output_sample_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n[CLI] Sample output saved to: {output_sample_path}")


if __name__ == "__main__":
    main()
