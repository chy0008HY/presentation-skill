# Integrated Generation Loop

Use this reference when a deck needs more than clean rendering: strong first-pass
visual direction, native PowerPoint editability, and an explicit post-render
quality decision.

## Three-layer contract

1. **Editable PPTX core.** Treat source files as authoritative and prefer native
   text, shapes, charts, tables, notes, and template layouts. Rasterize only when
   editability is not practical and record that choice. This adopts the useful
   output principle demonstrated by PPT Master without importing its runtime.
2. **Design-system routing.** Select a composition grammar and bounded style
   treatment before authoring. Reuse a verified starter, reference-deck signal,
   or repository grammar when one fits; do not improvise every slide from a
   blank canvas. This incorporates IFQ Design Skills' route-before-build idea
   into this repository's own renderer and style corpus.
3. **Reflective quality loop.** After deterministic checks and rendered review,
   judge content, design, and coherence separately. Repair the weakest blocking
   dimension in source, rebuild, and review again. This adapts the evaluation
   structure described by PPTAgent/PPTEval; it does not import model weights,
   services, or project code.

The three layers are complementary. A visually strong raster deck does not
satisfy the editable-output contract, and a technically valid PPTX does not pass
when its argument or narrative is weak.

## Review packet

Create a JSON file with this minimum shape after inspecting the final rendered
slides and the source/evidence plan:

```json
{
  "schema_version": "presentation_triad_review_v1",
  "reviewer": {"type": "model", "name": "independent-deck-reviewer"},
  "dimensions": {
    "content": {"score": 4.2, "rationale": "Claims are supported.", "evidence": ["Slides 3-6"]},
    "design": {"score": 4.0, "rationale": "Hierarchy is readable.", "evidence": ["Contact sheet"]},
    "coherence": {"score": 4.1, "rationale": "The close follows the evidence.", "evidence": ["Slides 1, 7"]}
  },
  "findings": []
}
```

Scores run from 0 to 5. Rationales and concrete review evidence are mandatory;
the gate rejects unsupported scores. Findings may use `info`, `warning`, or
`error` severity and must identify one of the three dimensions.

Run the gate:

```bash
python3 scripts/triad_review.py \
  --input /absolute/path/triad_review.json \
  --output /absolute/path/triad_review_decision.json \
  --fail-on-block
```

The default gate requires every dimension to score at least 3.5, the equal-weight
mean to reach 4.0, and no unresolved error finding. When blocked, repair the
first item in `repair_priority`, rebuild from source, and replace the review
packet with evidence from the new render. Do not raise a score without a visible
or source-backed change.

## When it is required

Run the triad gate for quality-first work, public or high-stakes delivery,
research/teaching decks whose claims matter, and generator comparisons. It is
optional for explicitly rough drafts, but a rough draft must not be represented
as delivery-ready.

## Source and license boundary

This integration is an original workflow adaptation. It stores no third-party
templates, brand assets, model weights, or copied implementation code.

- PPT Master — <https://github.com/hugohe3/ppt-master> — MIT
- IFQ Design Skills — <https://github.com/peixl/ifq-design-skills> — Apache-2.0
- PPTAgent / PPTEval — <https://github.com/icip-cas/PPTAgent> — MIT

Keep those projects as methodological references. Review their current licenses
before any future code or asset import.
