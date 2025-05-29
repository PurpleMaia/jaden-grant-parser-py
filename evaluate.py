import argparse
import json
import os
import re
import subprocess
import time
from typing import Any, Dict, List
from dotenv import load_dotenv

from pydantic import BaseModel

import rag


class ScoreModel(BaseModel):
    """Pydantic model for evaluation score."""

    score: float


def evaluate_prediction(pred: Dict[str, Any], expected: Dict[str, Any], guidelines: str) -> float:
    """Use the LLM to score prediction accuracy.

    Parameters
    ----------
    pred : dict
        Parsed JSON from ``grant.py`` output.
    expected : dict
        Reference JSON data for comparison.
    guidelines : str
        Instructions for how the LLM should evaluate the result.

    Returns
    -------
    float
        Score returned by the LLM, or ``0.0`` on error.
    """

    question = (
        f"{guidelines}\n\n"
        "Compare the following grant JSON objects and return a single 'score' "
        "from 0 to 10 representing accuracy."
    )
    context = json.dumps({"expected": expected, "predicted": pred}, indent=2)
    try:
        result = rag.retrieve_data_from_llm(question, context, ScoreModel)
        return float(result.get("score", 0))
    except Exception:
        return 0.0


def build_output_name(entry: Dict[str, Any], model: str | None) -> str:
    """Return the output JSON file name produced by ``grant.py`` for an entry."""

    model_name = model or os.getenv("MODEL", "model")
    if "folder" in entry:
        base = os.path.basename(os.path.normpath(entry["folder"]))
    else:
        names = [os.path.splitext(os.path.basename(f))[0] for f in entry["files"]]
        base = "_".join(names)
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base)
    return f"grant-{model_name}-{base}.json"


def run_grant(entry: Dict[str, Any], model: str | None) -> float:
    """Execute grant.py for the given entry and return runtime in seconds."""

    cmd: List[str] = ["python", "grant.py"]
    if "files" in entry:
        cmd.extend(entry["files"])
    if "folder" in entry:
        cmd.extend(["-f", entry["folder"]])
    if "k" in entry:
        cmd.extend(["-k", str(entry["k"])])
    if model:
        cmd.extend(["-m", model])

    start = time.perf_counter()
    subprocess.run(cmd, check=True)
    end = time.perf_counter()
    return end - start


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Evaluate grant parser output")
    parser.add_argument("config", help="Path to evaluation config JSON")
    parser.add_argument(
        "-m",
        "--model",
        help="Chat completion model name (overrides MODEL env variable)",
    )
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)

    guidelines = (
        "Score how well the predicted JSON matches the expected JSON. "
        "A score of 10 means an exact match; 0 means completely incorrect."
    )

    results = []
    for entry in config:
        runtime = run_grant(entry, args.model)
        output_file = build_output_name(entry, args.model)
        with open(output_file, "r") as f:
            predicted = json.load(f)
        with open(entry["expected"], "r") as f:
            expected = json.load(f)
        score = evaluate_prediction(predicted, expected, guidelines)
        results.append((output_file, runtime, score))

    if results:
        total_time = sum(r[1] for r in results)
        total_score = sum(r[2] for r in results)
        print("\nEvaluation Summary:")
        print(f"{'Output':40} {'Time(s)':>10} {'Score':>10}")
        for name, runtime, score in results:
            print(f"{name:40} {runtime:10.2f} {score:10.2f}")
        print("-" * 62)
        print(
            f"{'AVERAGE':40} {total_time/len(results):10.2f} "
            f"{total_score/len(results):10.2f}"
        )


if __name__ == "__main__":
    main()
