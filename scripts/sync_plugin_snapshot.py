#!/usr/bin/env python3
"""Refresh the Codex plugin skill snapshot from the repo-root skill."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO / "plugins" / "presentation-skill"
PLUGIN_SKILL_ROOT = PLUGIN_ROOT / "skills" / "presentation-skill"
PLUGIN_ASSETS = PLUGIN_ROOT / "assets"

FILES = [
    "SKILL.md",
    "DESIGN.md",
    "LICENSE",
    "package.json",
    "package-lock.json",
    "examples/outline.json",
    "agents/openai.yaml",
]

DIRECTORIES = [
    "references",
    "schemas",
    "scripts",
    "templates",
]

RUNTIME_EXCLUDES = {
    "large_style_corpus_catalog.json",
    "large_style_corpus_catalog_enriched.json",
    "large_style_corpus_catalog.md",
}

SCRIPT_DEVELOPMENT_ONLY = {
    "atomize_corpus.py",
    "enrich_corpus_structure.py",
    "enrich_corpus_vocabulary.py",
    "large_style_corpus.py",
    "run_focused_workflow_checks.py",
    "sync_plugin_snapshot.py",
    "validate_distribution.py",
}

SCREENSHOTS = {
    "v0.9_narrative_structures.jpg": REPO / "examples/v0.9_narrative_structures.jpg",
    "v0.9_evidence_data_structures.jpg": REPO / "examples/v0.9_evidence_data_structures.jpg",
    "v0.9_decisions_sources.jpg": REPO / "examples/v0.9_decisions_sources.jpg",
    "presentation_skill_variant_proof.png": REPO
    / "decks/native-vs-latest-random-topics-20260623/readme_images/presentation_skill_variant_proof.png",
    "presentation_skill_style_family_proof.png": REPO
    / "decks/native-vs-latest-random-topics-20260623/readme_images/presentation_skill_style_family_proof.png",
    "codex_native_vs_updated_clean_three_topics.png": REPO
    / "decks/native-vs-latest-random-topics-20260623/readme_images/codex_native_vs_updated_clean_three_topics.png",
}


def _ignore(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    in_scripts = Path(_dir).name == "scripts"
    for name in names:
        if name in {"__pycache__", ".pytest_cache", ".mypy_cache", "node_modules"}:
            ignored.add(name)
        elif name in RUNTIME_EXCLUDES:
            ignored.add(name)
        elif in_scripts and (
            name in SCRIPT_DEVELOPMENT_ONLY
            or (name.startswith("run_") and (name.endswith("_smoke.py") or name.endswith("_smoke.js")))
            or name == "run_pptxgenjs_regression.py"
            or (
                name.startswith("build_")
                and any(token in name for token in ("showcase", "gallery", "comparison", "readme", "native_vs"))
            )
        ):
            ignored.add(name)
        elif name.endswith((".pyc", ".pyo", ".DS_Store")):
            ignored.add(name)
    return ignored


def _copy_file(relative_path: str) -> None:
    src = REPO / relative_path
    if not src.is_file():
        raise FileNotFoundError(src)
    dst = PLUGIN_SKILL_ROOT / relative_path
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(relative_path: str) -> None:
    src = REPO / relative_path
    if not src.is_dir():
        raise FileNotFoundError(src)
    dst = PLUGIN_SKILL_ROOT / relative_path
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=_ignore)


def _write_runtime_package_manifest() -> None:
    package_path = PLUGIN_SKILL_ROOT / "package.json"
    payload = json.loads(package_path.read_text(encoding="utf-8"))
    payload["scripts"] = {
        "setup:python": "python3 scripts/runtime_doctor.py --bootstrap",
        "doctor": "python3 scripts/runtime_doctor.py",
        "check:runtime": "python3 scripts/runtime_doctor.py",
    }
    payload.pop("files", None)
    package_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if PLUGIN_SKILL_ROOT.exists():
        shutil.rmtree(PLUGIN_SKILL_ROOT)
    PLUGIN_SKILL_ROOT.mkdir(parents=True, exist_ok=True)

    for relative_path in FILES:
        _copy_file(relative_path)
    for relative_path in DIRECTORIES:
        _copy_tree(relative_path)
    _write_runtime_package_manifest()

    PLUGIN_ASSETS.mkdir(parents=True, exist_ok=True)
    for name, src in SCREENSHOTS.items():
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, PLUGIN_ASSETS / name)

    print(f"Synced plugin snapshot: {PLUGIN_SKILL_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
