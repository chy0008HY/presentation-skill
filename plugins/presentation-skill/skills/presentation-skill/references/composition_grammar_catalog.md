# Composition Grammar Catalog

Use this reference when a deck needs a recognizable argument and page system,
not merely a preset palette. Eight first-class grammars sit above the 13 style
presets:

| Grammar | Reading path | Persistent frame | Primary proof |
|---|---|---|---|
| `consulting-answer-pyramid` | answer -> proof -> action | report bands | exhibit + implication |
| `scientific-evidence-plate` | question -> method -> result -> limit | figure plate | controlled figure/table |
| `clinical-care-pathway` | cohort -> threshold -> care action | pathway rail | endpoint + action sidecar |
| `editorial-spread` | premise -> scene -> evidence -> close | asymmetric spread | image, quote, annotated graphic |
| `investor-thesis-stage` | problem -> proof -> economics -> ask | reveal stage | product or growth proof |
| `operations-grid` | state -> variance -> owner -> due | stable operating grid | target/actual/owner register |
| `policy-public-docket` | public question -> options -> accountability | docket index | map or option matrix |
| `technical-telemetry-canvas` | state -> signal -> failure -> recovery | telemetry frame | aligned signals and event log |

Each grammar provides `renderer_role_systems_v1` with system IDs for title,
section, evidence, comparison, data, decision, and references. It also carries
one narrative arc, grid, density, reading path, preferred role variants,
invariant moves, and forbidden moves. A grammar may serve at most two presets.

## Route A Request

```bash
python3 scripts/composition_grammar_catalog.py \
  --topic "Q3 retention operating review" \
  --user-prompt "Board decision with variance chart, owner table, and risk tradeoff" \
  --style-preset data-heavy-boardroom
```

Validate the catalog:

```bash
python3 scripts/composition_grammar_catalog.py --summary
```

Normal workspace initialization persists the result in:

- `design_brief.json:style_system.renderer_role_systems_v1`
- `design_brief.json:style_system.style_execution_plan`
- `design_brief.json:structure_strategy.composition_grammar`
- `style_contract.json:renderer_role_systems_v1`
- `outline.json:metadata.renderer_role_systems_v1`

## Mixing Rules

1. Keep the primary grammar's frame, navigation, reading path, and role-system
   IDs coherent.
2. Treat preferred variants as candidates ordered by the argument, never as a
   mandatory template sequence.
3. Borrow at most two bounded treatments from secondary influences. Do not
   borrow another grammar's complete cover, frame, or navigation.
4. Explicit user, brand, accessibility, and evidence constraints override the
   default route and must be recorded.
5. A slide may override its variant when the evidence shape requires it; keep
   the grammar's role intent and usable geometry.
6. Avoid repeating one skeleton more than twice unless the repeated evidence
   truly needs synchronized comparison.

## Diversity Gate

```bash
python3 scripts/run_controlled_style_diversity_smoke.py --render \
  --outdir /tmp/presentation-skill-structural-diversity
```

The v2 evaluator ignores color, fills, strokes, and decorative-only shapes. It
clusters semantic occupancy, topology, anchor geometry, hierarchy/reading
order, and whitespace zoning for nine controlled roles. Same-grammar pairs may
form a cluster of two; cross-grammar pairs must not repeat across five or more
roles. Edge hashes remain diagnostics, not proof of taste.
