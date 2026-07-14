#!/usr/bin/env python3
"""Run role-complete, identical-content structural diversity fixtures."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from structural_diversity_v2 import DEFAULT_ROLE_POLICIES, evaluate_manifest
from style_treatment_profiles import PROFILE_OVERRIDES, RENDERER_TREATMENT_FIELDS, preset_treatment_profile
from taste_grammar_catalog import PRESET_TO_GRAMMAR


ROOT = Path(__file__).resolve().parent.parent
PRESETS = sorted(PROFILE_OVERRIDES)
ROLE_SLIDES = [
    ("title", 1),
    ("section", 2),
    ("evidence", 3),
    ("comparison", 4),
    ("chart", 5),
    ("table", 6),
    ("decision", 7),
    ("references", 8),
    ("dense_title_evidence", 9),
]


def _run(parts: list[str]) -> str:
    result = subprocess.run(parts, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(parts) + "\n" + result.stdout)
    return result.stdout


def _outline() -> dict[str, Any]:
    footer = "Synthetic controlled fixture | identical content across presets"
    return {
        "title": "Controlled Structural Diversity v2",
        "subtitle": "Role-complete fixtures with paint-neutral geometry scoring",
        "slides": [
            {
                "type": "title",
                "role": "title",
                "title": "Regional Service Recovery",
                "subtitle": "A controlled operating review with identical evidence and wording.",
                "footer": footer,
            },
            {
                "type": "section",
                "role": "section",
                "title": "Evidence to decision",
                "subtitle": "The same narrative turn rendered through every structural identity.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "evidence",
                "treatment_key": "dashboard",
                "variant": "stats",
                "title": "Recovery is accelerating, but the final cohort remains exposed",
                "subtitle": "Three controlled proof points",
                "facts": [
                    {"value": "78%", "label": "Complete", "detail": "+15 pts week over week"},
                    {"value": "22", "label": "Open", "detail": "cases need closure"},
                    {"value": "4d", "label": "Median age", "detail": "down from seven"},
                ],
                "summary_callout": "The residual queue is concentrated in one dependency class.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "comparison",
                "treatment_key": "comparison",
                "variant": "comparison-2col",
                "title": "The decision is speed versus control, not growth versus safety",
                "subtitle": "Two bounded operating choices",
                "left": {
                    "title": "Accelerate",
                    "bullets": ["Parallel reviews", "Daily owner queue", "Faster customer response"],
                },
                "right": {
                    "title": "Control",
                    "bullets": ["Single approval gate", "Weekly audit sample", "Lower exception risk"],
                },
                "verdict": "Use parallel reviews with one explicit exception gate.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "chart",
                "treatment_key": "chart",
                "variant": "chart",
                "title": "Weekly completion has moved from recovery into closure",
                "subtitle": "Completion rate by operating week",
                "chart": {
                    "type": "bar",
                    "title": "Weekly completion rate",
                    "labels": ["W1", "W2", "W3", "W4"],
                    "values": [42, 57, 63, 78],
                    "facts": [
                        {"value": "78%", "label": "Latest", "detail": "+15 pts"},
                        {"value": "22", "label": "Open", "detail": "cases"},
                    ],
                    "notes": "The same native chart data is rendered by every preset.",
                },
                "caption": "Synthetic weekly completion fixture.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "table",
                "treatment_key": "table",
                "variant": "table",
                "title": "Ownership is clear; two dependencies still need intervention",
                "subtitle": "Editable operating ledger",
                "headers": ["Workstream", "Status", "Owner", "Next check"],
                "rows": [
                    ["Intake", "On track", "Maya", "Mon"],
                    ["Validation", "Watch", "Jon", "Tue"],
                    ["Escalation", "At risk", "Priya", "Today"],
                    ["Closure", "On track", "Luis", "Fri"],
                ],
                "caption": "Same rows, labels, and density across all presets.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "decision",
                "treatment_key": "decision",
                "variant": "matrix",
                "title": "Approve the faster path with one bounded exception gate",
                "subtitle": "Decision conditions and explicit ownership",
                "quadrants": [
                    {"title": "Proceed", "body": "Parallel review for standard cases"},
                    {"title": "Gate", "body": "Single approval for exceptions"},
                    {"title": "Measure", "body": "Daily age and closure rate"},
                    {"title": "Owner", "body": "Regional operations lead"},
                ],
                "summary_callout": "Decision: launch Monday and audit the first twenty closures.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "references",
                "treatment_key": "references",
                "variant": "table",
                "table_style": "references",
                "title": "References",
                "subtitle": "Synthetic sources used only for controlled layout evaluation",
                "headers": ["ID", "Source", "Use"],
                "rows": [
                    ["S1", "Weekly completion fixture", "Trend and latest value"],
                    ["S2", "Open case ledger fixture", "Queue and ownership"],
                    ["S3", "Exception audit fixture", "Decision gate"],
                ],
                "caption": "No external claims are made by this synthetic fixture.",
                "footer": footer,
            },
            {
                "type": "content",
                "role": "dense_title_evidence",
                "treatment_key": "dashboard",
                "variant": "stats",
                "title": "A deliberately dense title tests whether structural identity survives longer evidence-led editorial framing without clipping or collapsing into one universal template",
                "subtitle": "Stress fixture: identical long copy, five proof points, and one explicit synthesis line",
                "facts": [
                    {"value": "78%", "label": "Complete", "detail": "+15 points"},
                    {"value": "22", "label": "Open", "detail": "one cohort"},
                    {"value": "4d", "label": "Median age", "detail": "down three"},
                    {"value": "2", "label": "Dependencies", "detail": "both owned"},
                    {"value": "Mon", "label": "Launch", "detail": "audit at 20"},
                ],
                "summary_callout": "Long-title resilience matters only if the evidence hierarchy remains legible and structurally distinct.",
                "footer": footer,
            },
        ],
    }


def _javascript_preset_treatments() -> dict[str, dict[str, Any]]:
    output = _run(
        [
            "node",
            "-e",
            "const m=require('./scripts/build_deck_pptxgenjs.js');process.stdout.write(JSON.stringify(m.PRESET_TREATMENTS));",
        ]
    )
    payload = json.loads(output)
    return payload if isinstance(payload, dict) else {}


def _static_contract() -> tuple[dict[str, Any], list[str]]:
    profiles = [preset_treatment_profile(preset) for preset in PRESETS]
    javascript_treatments = _javascript_preset_treatments()
    motifs = [str(profile["renderer_treatment_defaults"].get("structural_motif") or "") for profile in profiles]
    signatures = [str(profile.get("renderer_treatment_signature") or "") for profile in profiles]
    failures: list[str] = []
    parity_mismatches: list[dict[str, str]] = []
    if len(set(motifs)) != len(PRESETS):
        failures.append(f"structural_motif_count={len(set(motifs))} expected={len(PRESETS)}")
    if len(set(signatures)) != len(PRESETS):
        failures.append(f"renderer_signature_count={len(set(signatures))} expected={len(PRESETS)}")
    for profile in profiles:
        preset = str(profile.get("style_preset") or "")
        expected = profile.get("renderer_treatment_defaults") or {}
        actual = javascript_treatments.get(preset) or {}
        for field in RENDERER_TREATMENT_FIELDS:
            left = str(expected.get(field) or "")
            right = str(actual.get(field) or "")
            if left != right:
                parity_mismatches.append({"preset": preset, "field": field, "python": left, "javascript": right})
    if parity_mismatches:
        failures.append(f"python_javascript_treatment_mismatches={len(parity_mismatches)}")
    fixture_roles = [str(slide.get("role") or "") for slide in _outline()["slides"]]
    expected_roles = [role for role, _ in ROLE_SLIDES]
    if fixture_roles != expected_roles:
        failures.append(f"fixture_roles={fixture_roles!r} expected={expected_roles!r}")
    return (
        {
            "preset_count": len(PRESETS),
            "unique_structural_motif_count": len(set(motifs)),
            "unique_renderer_signature_count": len(set(signatures)),
            "python_javascript_parity": not parity_mismatches,
            "parity_mismatches": parity_mismatches,
            "fixture_roles": fixture_roles,
            "role_policies": {role: vars(DEFAULT_ROLE_POLICIES[role]) for role, _ in ROLE_SLIDES},
        },
        failures,
    )


def _build_case(preset: str, outline_path: Path, outdir: Path, dpi: int, force: bool) -> dict[str, Any]:
    case_dir = outdir / "cases" / preset
    pptx_path = case_dir / f"{preset}.pptx"
    render_dir = case_dir / "renders"
    case_dir.mkdir(parents=True, exist_ok=True)
    images = sorted(render_dir.glob("slide-*.jpg"))
    if force or not pptx_path.is_file() or len(images) != len(ROLE_SLIDES):
        _run(
            [
                "node",
                "scripts/build_deck_pptxgenjs.js",
                "--outline",
                str(outline_path),
                "--output",
                str(pptx_path),
                "--style-preset",
                preset,
            ]
        )
        _run(
            [
                "python3",
                "scripts/render_slides.py",
                "--input",
                str(pptx_path),
                "--outdir",
                str(render_dir),
                "--dpi",
                str(dpi),
                "--format",
                "jpeg",
            ]
        )
        images = sorted(render_dir.glob("slide-*.jpg"))
    if len(images) != len(ROLE_SLIDES):
        raise RuntimeError(f"{preset}: rendered_slide_count={len(images)} expected={len(ROLE_SLIDES)}")
    return {
        "id": preset,
        "pptx": str(pptx_path),
        "slides": [
            {"role": role, "index": index, "render": str(images[index - 1])}
            for role, index in ROLE_SLIDES
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--dpi", type=int, default=100)
    parser.add_argument("--jobs", type=int, default=1, help="Accepted for compatibility; rendering remains serialized.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--repeated-pair-role-limit", type=int, default=5)
    args = parser.parse_args()

    static_contract, static_failures = _static_contract()
    payload: dict[str, Any] = {
        "schema_version": "controlled-style-diversity-smoke-v2",
        "passed": not static_failures,
        "rendered": False,
        **static_contract,
        "failures": static_failures,
    }
    if not args.render:
        print(json.dumps(payload, indent=2))
        return 0 if payload["passed"] else 1
    if not shutil.which("soffice"):
        payload["passed"] = False
        payload["failures"] = static_failures + ["soffice is required for --render"]
        print(json.dumps(payload, indent=2))
        return 1

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.outdir:
        outdir = args.outdir.resolve()
        outdir.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="presentation-skill-structural-diversity-v2-")
        outdir = Path(temporary.name)
    outline_path = outdir / "controlled_role_complete_outline.json"
    outline_path.write_text(json.dumps(_outline(), indent=2) + "\n", encoding="utf-8")

    deck_entries: list[dict[str, Any]] = []
    build_failures: list[str] = []
    for preset in PRESETS:
        try:
            deck_entries.append(_build_case(preset, outline_path, outdir, args.dpi, args.force))
        except Exception as exc:
            build_failures.append(f"{preset}: {exc}")
    manifest = {
        "schema_version": "structural-diversity-v2-manifest",
        "decks": deck_entries,
        "coherent_groups": {preset: PRESET_TO_GRAMMAR[preset] for preset in PRESETS},
    }
    manifest_path = outdir / "structural_diversity_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    evaluator_report: dict[str, Any] | None = None
    evaluator_failure: str | None = None
    if len(deck_entries) == len(PRESETS):
        try:
            evaluator_report = evaluate_manifest(
                manifest,
                manifest_base=outdir,
                artifacts_dir=outdir / "structural_proof",
                repeated_pair_role_limit=args.repeated_pair_role_limit,
            )
        except Exception as exc:
            evaluator_failure = str(exc)
    all_failures: list[Any] = list(static_failures) + build_failures
    if evaluator_failure:
        all_failures.append(f"structural_evaluator_error: {evaluator_failure}")
    if evaluator_report and not evaluator_report["passed"]:
        all_failures.extend(evaluator_report["failures"])
    payload.update(
        {
            "passed": not all_failures,
            "rendered": True,
            "outdir": str(outdir),
            "outline": str(outline_path),
            "manifest": str(manifest_path),
            "rendered_preset_count": len(deck_entries),
            "structural_evaluator": evaluator_report,
            "failures": all_failures,
        }
    )
    report_path = outdir / "controlled_style_diversity_report_v2.json"
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": payload["passed"],
                "report": str(report_path),
                "manifest": str(manifest_path),
                "rendered_preset_count": len(deck_entries),
                "role_clusters": {
                    role: evaluator_report["role_reports"][role]["cluster_count"]
                    for role, _ in ROLE_SLIDES
                }
                if evaluator_report
                else {},
                "failure_count": len(all_failures),
            },
            indent=2,
        )
    )
    if temporary is not None:
        temporary.cleanup()
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
