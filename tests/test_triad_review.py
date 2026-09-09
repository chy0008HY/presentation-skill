from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from triad_review import SCHEMA_VERSION, evaluate_review  # noqa: E402


def _packet() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "reviewer": {"type": "model", "name": "independent-deck-reviewer"},
        "dimensions": {
            "content": {"score": 4.4, "rationale": "Claims match the source.", "evidence": ["Slides 3-6"]},
            "design": {"score": 4.1, "rationale": "Hierarchy is readable.", "evidence": ["Contact sheet"]},
            "coherence": {"score": 4.3, "rationale": "The decision follows the evidence.", "evidence": ["Slides 1, 7"]},
        },
        "findings": [],
    }


class TriadReviewTests(unittest.TestCase):
    def test_complete_review_passes(self) -> None:
        result = evaluate_review(_packet())
        self.assertTrue(result["passed"])
        self.assertEqual(result["overall_score"], 4.267)
        self.assertEqual(result["repair_priority"], [])

    def test_low_dimension_blocks_even_when_overall_passes(self) -> None:
        packet = _packet()
        packet["dimensions"]["design"]["score"] = 3.4
        packet["dimensions"]["content"]["score"] = 5.0
        packet["dimensions"]["coherence"]["score"] = 5.0
        result = evaluate_review(packet)
        self.assertFalse(result["passed"])
        self.assertEqual(result["below_threshold"], ["design"])
        self.assertEqual(result["repair_priority"][0]["dimension"], "design")

    def test_unresolved_error_blocks_delivery(self) -> None:
        packet = _packet()
        packet["findings"] = [
            {"dimension": "content", "severity": "error", "slide": 4, "message": "Claim lacks support."}
        ]
        result = evaluate_review(packet)
        self.assertFalse(result["passed"])
        self.assertEqual(result["unresolved_error_count"], 1)
        self.assertEqual(result["repair_priority"][0]["dimension"], "content")

    def test_cli_writes_decision_and_returns_blocking_status(self) -> None:
        packet = _packet()
        packet["dimensions"]["coherence"]["score"] = 2.5
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "review.json"
            output = root / "decision.json"
            source.write_text(json.dumps(packet), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "triad_review.py"),
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--fail-on-block",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(output.read_text(encoding="utf-8"))["passed"])


if __name__ == "__main__":
    unittest.main()
