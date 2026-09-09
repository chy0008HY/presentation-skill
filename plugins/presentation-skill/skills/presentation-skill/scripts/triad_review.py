#!/usr/bin/env python3
"""Validate a content/design/coherence review before deck delivery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "presentation_triad_review_v1"
DIMENSIONS = ("content", "design", "coherence")
REPAIR_GUIDANCE = {
    "content": "Repair unsupported claims, evidence coverage, hierarchy, and audience relevance.",
    "design": "Repair visual hierarchy, readability, composition, contrast, and editability.",
    "coherence": "Repair narrative flow, slide transitions, terminology, and conclusion alignment.",
}


def _score(value: Any, *, dimension: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{dimension}.score must be a number from 0 to 5")
    result = float(value)
    if not 0.0 <= result <= 5.0:
        raise ValueError(f"{dimension}.score must be a number from 0 to 5")
    return result


def _nonempty_text(value: Any, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def _evidence(value: Any, *, dimension: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{dimension}.evidence must be a non-empty list")
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        raise ValueError(f"{dimension}.evidence must be a non-empty list")
    return items


def evaluate_review(
    payload: dict[str, Any],
    *,
    min_dimension: float = 3.5,
    min_overall: float = 4.0,
) -> dict[str, Any]:
    """Validate a review packet and return a deterministic delivery decision."""
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    if not 0.0 <= min_dimension <= 5.0 or not 0.0 <= min_overall <= 5.0:
        raise ValueError("review thresholds must be between 0 and 5")

    reviewer = payload.get("reviewer")
    if not isinstance(reviewer, dict):
        raise ValueError("reviewer must be an object")
    reviewer_type = str(reviewer.get("type") or "").strip().lower()
    if reviewer_type not in {"human", "model"}:
        raise ValueError("reviewer.type must be 'human' or 'model'")
    reviewer_name = _nonempty_text(reviewer.get("name"), field="reviewer.name")

    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, dict):
        raise ValueError("dimensions must be an object")
    missing = [name for name in DIMENSIONS if name not in dimensions]
    extra = sorted(set(dimensions) - set(DIMENSIONS))
    if missing or extra:
        raise ValueError(f"dimensions must contain exactly {list(DIMENSIONS)}")

    normalized: dict[str, dict[str, Any]] = {}
    for name in DIMENSIONS:
        item = dimensions[name]
        if not isinstance(item, dict):
            raise ValueError(f"{name} must be an object")
        normalized[name] = {
            "score": _score(item.get("score"), dimension=name),
            "rationale": _nonempty_text(item.get("rationale"), field=f"{name}.rationale"),
            "evidence": _evidence(item.get("evidence"), dimension=name),
        }

    findings = payload.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")
    normalized_findings: list[dict[str, Any]] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValueError(f"findings[{index}] must be an object")
        dimension = str(finding.get("dimension") or "").strip().lower()
        severity = str(finding.get("severity") or "").strip().lower()
        if dimension not in DIMENSIONS:
            raise ValueError(f"findings[{index}].dimension must be one of {list(DIMENSIONS)}")
        if severity not in {"info", "warning", "error"}:
            raise ValueError(f"findings[{index}].severity must be info, warning, or error")
        normalized_findings.append(
            {
                "dimension": dimension,
                "severity": severity,
                "message": _nonempty_text(finding.get("message"), field=f"findings[{index}].message"),
                **({"slide": int(finding["slide"])} if finding.get("slide") is not None else {}),
            }
        )

    scores = {name: normalized[name]["score"] for name in DIMENSIONS}
    overall = round(sum(scores.values()) / len(DIMENSIONS), 3)
    below_threshold = [name for name in DIMENSIONS if scores[name] < min_dimension]
    unresolved_errors = [item for item in normalized_findings if item["severity"] == "error"]
    passed = overall >= min_overall and not below_threshold and not unresolved_errors

    repair_dimensions = sorted(
        set(below_threshold).union(item["dimension"] for item in unresolved_errors),
        key=lambda name: (scores[name], DIMENSIONS.index(name)),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "reviewer": {"type": reviewer_type, "name": reviewer_name},
        "thresholds": {"min_dimension": min_dimension, "min_overall": min_overall},
        "dimensions": normalized,
        "scores": scores,
        "overall_score": overall,
        "below_threshold": below_threshold,
        "unresolved_error_count": len(unresolved_errors),
        "findings": normalized_findings,
        "repair_priority": [
            {"dimension": name, "score": scores[name], "guidance": REPAIR_GUIDANCE[name]}
            for name in repair_dimensions
        ],
        "passed": passed,
    }


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input presentation_triad_review_v1 JSON")
    parser.add_argument("--output", help="Decision JSON (default: next to input)")
    parser.add_argument("--min-dimension", type=float, default=3.5)
    parser.add_argument("--min-overall", type=float, default=4.0)
    parser.add_argument("--fail-on-block", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name("triad_review_decision.json")
    )
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    result = evaluate_review(
        payload,
        min_dimension=args.min_dimension,
        min_overall=args.min_overall,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path), "passed": result["passed"], "scores": result["scores"]}, indent=2))
    return 1 if args.fail_on_block and not result["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
