# Phase 15 notes — secondary effects: less meat, freed land, a vegetable sketch

Post-launch addition, prompted by the user asking, right after learning vegetables are Estonia's
weakest self-sufficiency category (46%, falling further under every alternative diet scenario):
"if less meat is produced, some crops could go for food, maybe some land could be used to grow more
stuff? how difficult would it be?" Scoped after a difficulty assessment and an explicit choice
(via AskUserQuestion) to build both the solid and speculative halves, kept clearly separated
rather than presented at the same confidence level — this is a genuinely new kind of question for
this project, distinct from every prior phase.

## 1. Why this is a different kind of question

Every scenario built so far (A/B/C/C2) holds domestic production fixed and only varies demand —
that convention is stated explicitly throughout `docs/methodology.md`. This question asks what
happens if production actually follows demand downward, which is precisely the "theoretical
production-capacity / land-reallocation modelling" that `plans/PLAN.md` Section 10 flagged as
**out of scope for v1** from the very first phase, for exactly the reason it turns "are we
self-sufficient today" into "could we be, if we changed what we grow." This phase doesn't reverse
that scoping decision — it takes one small, clearly-bounded, clearly-labelled step into it, kept
structurally and visually separate from the rest of the project's measured-data results.

## 2. Two tiers, not one number

**Tier 1 (solid arithmetic)**: demand for poultry/eggs/red meat drops under a scenario -> if
production scaled down proportionally (one new, explicitly-flagged behavioural assumption — every
other scenario holds production fixed; this is the one place it's allowed to move) -> less feed
grain is needed -> since feed grain is overwhelmingly barley, that converts cleanly to hectares no
longer needed for it, using barley's own 2024 Estonian yield (already in this project's PM20 data,
no new pull required).

Deliberately **not** framed as "feed grain redirected to human food," because Estonia's barley is
already a large net export crop (2024: 315.2kt produced vs. 177.1kt domestic use, 179.8kt
exported) with feed as the dominant domestic use. Self-sufficiency is production ÷ domestic use;
shuffling already-produced grain between feed-use and export doesn't move that ratio for any
category. The only lever that can actually help a weak category like vegetables is the *land*
itself growing something else — which is Tier 2.

**Tier 2 (illustrative sketch, explicitly not a projection)**: that freed cropland, if switched to
vegetables, at a **generic EU-wide average yield** (Eurostat 2022: 59.8Mt / 2.0M ha = 29.9 t/ha —
no Estonia-specific field-vegetable yield figure was available in this project's data or found in
a search). This tier stacks new uncertainty on top of Tier 1's assumption and checks nothing about
soil suitability, drainage, capital, labour, storage, or market absorption — it answers "is the
land arithmetic even in the right ballpark," not "what would actually happen."

Deliberately excluded from both tiers: dairy cattle (feed is predominantly grass/silage, not a
grain tonnage convertible to hectares with any confidence — same reason Phase 6's
`feed_dependency_model.csv` excludes dairy from its own feed-tonnage table) and permanent
pasture/grazing land generally (a far less certain conversion candidate than already-arable
feed-cropland, with no Estonia-specific land-use-by-category data available to even attempt it).

## 3. Result

| Scenario | Feed no longer needed | Cropland no longer needed | % of 2024 barley area | Illustrative veg. output | % of vegetable gap | Land needed to close entire gap |
|---|---|---|---|---|---|---|
| B (TAI) | 140.0 kt | 42,217 ha | 44.4% | 1,262,288 t | 1,557% | only 6.4% of freed land |
| C (EAT-Lancet 2019) | 196.9 kt | 59,367 ha | 62.5% | 1,775,073 t | 2,190% | only 4.6% of freed land |
| C.2 (EAT-Lancet 2025) | 173.6 kt | 52,358 ha | 55.1% | 1,565,504 t | 1,931% | only 5.2% of freed land |

The C/C2 rows were recalculated in Phase 21 after their demand masses were normalized from mixed
EAT source weights to the TAI edible/ready-to-eat basis. Scenario B is unchanged.

(Vegetable gap = 2024 domestic use minus production, both from PM33: 114,297t − 33,229t = 81,068t —
computed directly from raw tonnages rather than any of the three disagreeing self-sufficiency
percentages already on record for this category, to keep this analysis on one transparent,
internally-consistent 2024 basis.)

Two things worth flagging honestly. First, under Scenario B specifically, poultry and egg demand
actually *rise* relative to today (TAI recommends eating more of both, less red meat) — so those
two components show up as slightly *negative* freed feed in the table (more feed needed, not
less), and the net positive result is driven almost entirely by the much larger red meat reduction.
Second, and more importantly: the freed land implied here is large relative to Estonia's own
barley acreage (44-64% of all 2024 barley sown area) and a meaningful slice of the country's total
utilised agricultural area (~980,000 ha, Statistikaamet 2023 — 4.3-6.2% of it). That scale is
itself a reason for skepticism about the underlying "production follows demand" assumption: a
change of that size to Estonia's actual land use is a much bigger claim than the tonnage-only
framing might suggest at first glance.

The genuinely useful finding, held at arm's length appropriately: even the most conservative
scenario would only need about 6% of its own freed land to close the *entire* current vegetable
gap, at a generic yield. That says the land arithmetic isn't the binding constraint on vegetable
self-sufficiency — but real-world adoption, agronomic suitability, capital, labour, and time very
plausibly are, and none of those are modelled here.

## 4. Build

- `src/land_reallocation_analysis.py` — computes both tiers from existing project data
  (`feed_dependency_model.csv`, `scenario_comparison.csv`'s demand ratios, PM20's 2024 barley
  yield) plus two new external citations (EU vegetable yield, Estonia's total utilised
  agricultural area), writing `data/processed/land_reallocation_scenario.csv`.
- `output/secondary_effects.html` — a genuinely separate, self-contained second page (not merged
  into the main dashboard), reusing the main dashboard's visual language (same CSS token system)
  but with the two tiers visually distinguished: Tier 1 in the dashboard's normal card styling with
  a green "solid arithmetic" badge, Tier 2 in a dashed-border, amber-tinted card with an
  "illustrative sketch" badge — so the confidence difference is visible at a glance, not just
  stated in prose. Verified via headless Playwright against a staged copy: both tables render with
  correct row counts and no JS errors.

## 5. Deliverables

- `src/land_reallocation_analysis.py` — new analysis script.
- `data/processed/land_reallocation_scenario.csv` — new output (3 rows, one per scenario B/C/C2).
- `output/secondary_effects.html` — new standalone page.
- `docs/methodology.md` — new section documenting this phase (see below).
- This file.
