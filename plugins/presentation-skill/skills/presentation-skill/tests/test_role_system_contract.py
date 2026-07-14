from __future__ import annotations

import copy
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from composition_grammar_catalog import (  # noqa: E402
    build_composition_grammar_catalog,
    route_composition_grammars,
    validate_composition_grammar_catalog,
)
from init_deck_workspace import _design_brief_stub, _starter_outline, _style_contract  # noqa: E402
from style_treatment_profiles import (  # noqa: E402
    PROFILE_OVERRIDES,
    RENDERER_TREATMENT_FIELDS,
    preset_treatment_profile,
)
from taste_grammar_catalog import (  # noqa: E402
    COMPOSITION_GRAMMARS,
    PRESET_TO_GRAMMAR,
    renderer_role_systems_for_preset,
    validate_renderer_role_systems_v1,
    validate_taste_grammar_catalog,
)
from validate_planning import _validate_renderer_role_systems_contract  # noqa: E402
from workflow_atom_context import build_workflow_atom_context, compact_workflow_atom_context  # noqa: E402


EXPECTED_GRAMMARS = {
    "consulting-answer-pyramid",
    "scientific-evidence-plate",
    "clinical-care-pathway",
    "editorial-spread",
    "investor-thesis-stage",
    "operations-grid",
    "policy-public-docket",
    "technical-telemetry-canvas",
}


class TasteGrammarCatalogTests(unittest.TestCase):
    def test_catalog_cardinality_and_preset_distribution(self) -> None:
        taste_summary = validate_taste_grammar_catalog()
        composition_summary = validate_composition_grammar_catalog()

        self.assertTrue(taste_summary["passed"], taste_summary["failures"])
        self.assertTrue(composition_summary["passed"], composition_summary["failures"])
        self.assertEqual(set(COMPOSITION_GRAMMARS), EXPECTED_GRAMMARS)
        self.assertEqual(taste_summary["grammar_count"], 8)
        self.assertEqual(taste_summary["preset_count"], 13)
        self.assertEqual(set(PRESET_TO_GRAMMAR), set(PROFILE_OVERRIDES))
        self.assertLessEqual(max(Counter(PRESET_TO_GRAMMAR.values()).values()), 2)

        counts = taste_summary["role_system_counts"]
        self.assertEqual(counts["title"], 8)
        self.assertGreaterEqual(counts["section"], 6)
        self.assertGreaterEqual(counts["evidence"], 8)
        self.assertGreaterEqual(counts["data"], 8)
        self.assertGreaterEqual(taste_summary["narrative_arc_count"], 6)

    def test_profiles_add_role_systems_without_removing_legacy_treatments(self) -> None:
        for preset in PROFILE_OVERRIDES:
            with self.subTest(preset=preset):
                profile = preset_treatment_profile(preset)
                self.assertEqual(profile["profile_version"], "deck_preset_treatment_profiles_v1")
                self.assertIn("style_mix_matrix", profile)
                self.assertIn("renderer_treatment_signature", profile)
                self.assertEqual(profile["renderer_treatment_fields"], list(RENDERER_TREATMENT_FIELDS))
                self.assertTrue(
                    set(RENDERER_TREATMENT_FIELDS).issubset(profile["renderer_treatment_defaults"])
                )
                role_systems = profile["renderer_role_systems_v1"]
                self.assertFalse(
                    validate_renderer_role_systems_v1(role_systems, expected_preset=preset)
                )

    def test_routing_honors_preset_lock_and_exposes_role_contract(self) -> None:
        route = route_composition_grammars(
            topic="Assay validation",
            user_prompt="investor market story with a hero metric",
            style_preset="lab-report",
        )
        primary = route["primary"]
        self.assertEqual(primary["grammar_id"], "scientific-evidence-plate")
        self.assertEqual(primary["renderer_role_systems_v1"]["schema_version"], "renderer_role_systems_v1")
        for role in ("title", "section", "evidence", "comparison", "data", "decision", "references"):
            self.assertTrue(primary[f"{role}_system_id"])
        self.assertTrue(primary["narrative_arc"])
        self.assertTrue(primary["density"])
        self.assertTrue(primary["grid"])
        self.assertTrue(primary["reading_path"])
        self.assertTrue(primary["preferred_role_variants"])
        self.assertTrue(primary["invariant_moves"])
        self.assertTrue(primary["forbidden_moves"])

    def test_normal_workflow_persists_role_systems(self) -> None:
        context = compact_workflow_atom_context(
            build_workflow_atom_context(
                user_prompt="Clinical evidence and care pathway review",
                style_preset="executive-clinical",
                include_prompt=False,
            )
        )
        role_systems = context["renderer_role_systems_v1"]
        self.assertEqual(role_systems["composition_grammar_id"], "clinical-care-pathway")
        self.assertEqual(
            context["style_execution_plan"]["renderer_role_systems_v1"],
            role_systems,
        )

        brief = _design_brief_stub(
            "Clinical evidence review",
            "executive-clinical",
            user_prompt="Clinical evidence and care pathway review",
        )
        outline = _starter_outline(
            "Clinical evidence review",
            "executive-clinical",
            None,
            None,
            user_prompt="Clinical evidence and care pathway review",
        )
        contract = _style_contract(
            title="Clinical evidence review",
            slug="clinical-evidence-review",
            style_preset="executive-clinical",
            font_pair=None,
            palette_key=None,
            reference_pptx=None,
            user_prompt="Clinical evidence and care pathway review",
        )
        self.assertEqual(brief["style_system"]["renderer_role_systems_v1"], role_systems)
        self.assertEqual(outline["metadata"]["renderer_role_systems_v1"], role_systems)
        self.assertEqual(contract["renderer_role_systems_v1"], role_systems)
        self.assertFalse(_validate_renderer_role_systems_contract(brief))

    def test_strict_validation_rejects_unknown_or_inconsistent_system_ids(self) -> None:
        brief = _design_brief_stub("Operations review", "lavender-ops", user_prompt="operations review")
        broken = copy.deepcopy(brief)
        broken["style_system"]["renderer_role_systems_v1"]["title_system_id"] = "title-unknown"
        issues = _validate_renderer_role_systems_contract(broken)
        self.assertTrue(issues)
        self.assertTrue(all(issue["severity"] == "error" for issue in issues))
        self.assertTrue(any("title_system_id" in issue["message"] for issue in issues))

    def test_composition_catalog_records_are_exactly_eight(self) -> None:
        catalog = build_composition_grammar_catalog()
        self.assertEqual(catalog["grammar_count"], 8)
        self.assertEqual(
            {record["grammar_id"] for record in catalog["records"]},
            EXPECTED_GRAMMARS,
        )
        for preset in PROFILE_OVERRIDES:
            self.assertEqual(
                renderer_role_systems_for_preset(preset)["composition_grammar_id"],
                PRESET_TO_GRAMMAR[preset],
            )


if __name__ == "__main__":
    unittest.main()
