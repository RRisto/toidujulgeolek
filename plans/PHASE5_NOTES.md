# Phase 5 notes — domestic supply / self-sufficiency model

Phase 5 of PLAN.md Section 7 / Section 5.3: a self-sufficiency ratio (production / domestic
utilization) per pyramid food group and sub-item, calibrated against the official 2023+ strategy
document. Status: done.

## What Phase 5 delivered

The core deliverable is `data/processed/self_sufficiency_model.csv` (18 rows) — every pyramid
sub-item's self-sufficiency ratio, tagged with a `data_status` (derived / derived+official_avg /
derived+official_preferred / derived_matches_official / gap_range / gap_assumed / gap_unknown) so
a reader can tell at a glance how solid each number is.

### Calibration against the official strategy-document figures (the Section 7 checkpoint)

Most categories land close to the official 5-year-average figures already sourced in
`DATA_SOURCES.md` Section 6 — eggs (53.2% vs 54%), poultry (58.4% vs 57%), and fruit+berries (8%
vs 8%, an exact match) all agree within a couple of points, so their headline figure is a simple
average of the two. Three categories diverge enough to need explanation and a documented decision
on which figure to report as the headline:

- **Vegetables**: 29% (this pull, single 2024 year) vs. 46% (official 5-year average) — a large
  gap already flagged in `PHASE1_NOTES.md`, plausibly single-year output volatility (vegetables are
  a high-variance crop) or a category-definition difference (fresh-only vs. all vegetables incl.
  processed). **Headline uses the official 46%**, since the gap is too large to treat the
  single-year figure as more reliable.
- **Dairy**: 134.9% (this phase's own milk-equivalent build across PM47's 9 product lines, using
  generic/illustrative conversion factors — see below) vs. 166% (official). **Headline uses the
  official 166%**; the derived figure is kept in the table for transparency about the method, not
  as the recommended number.
- **Potato**: 63.7% vs. 70% — a smaller, single-year-plausible gap; headline uses the midpoint
  (66.9%) rather than picking one side.

### New conversions built this phase (with explicitly generic, non-Estonia-specific factors)

- **Dairy milk-equivalent aggregation**: PM47 publishes 9 separate dairy product balances (fresh
  milk, cream, concentrated milk, powders, butter, cheese, processed cheese) that can't be summed
  directly — a kilogram of butter represents far more raw milk than a kilogram of liquid milk.
  Used standard order-of-magnitude FAO-style conversion factors (fresh products 1.0x, cream 6x,
  concentrated milk 2.3x, milk powders 8-9x, butter 20x, cheese 10x, processed cheese 8x) —
  explicitly flagged in the model as generic/illustrative, not independently verified against
  FAO's own published conversion table or Estonia-specific dairy-industry figures. Two minor
  product lines (whole/skimmed milk powder) had no published `domestic_use_total` in Statistikaamet's
  table; their domestic use was inferred as production+imports−exports (floored at zero after one
  inference came out negative, likely a stock-drawdown accounting quirk) — both lines are tiny
  relative to the fresh-milk and cheese lines that dominate the aggregate, so this inference barely
  moves the headline number either way.
- **Bread and rapeseed-oil "yield cancellation" argument**: converting raw wheat/rye tonnage to
  bread tonnage, or raw rapeseed tonnage to refined-oil tonnage, would normally need a
  milling/baking yield or an oil-extraction yield. This phase instead argues that *if* the same
  yield factor applies uniformly to both domestically-grown-and-processed and imported-and-processed
  raw material, that factor cancels out of the production/domestic-use ratio — so the raw-commodity
  self-sufficiency ratio approximates the processed-product ratio without needing to pick and
  defend a specific yield number. This is flagged as a real simplifying assumption, not a proof:
  it breaks down if a meaningful share of Estonia's bread or edible-oil trade happens at the
  already-processed stage (imported flour, imported refined oil) rather than as raw grain/seed,
  which Statistikaamet's PM-series tables can't distinguish.
- **Red meat aggregate**: beef+pork+sheep-goat+offal combined (matching Phase 4's red-meat
  grouping) computes to 78.1% self-sufficient — no single official comparator exists for this exact
  bundle, but every component is individually close to or matching its own official figure (beef
  109% vs 95%, pork 72% vs 78%, sheep-goat 80% vs 90%), so the aggregate is reported with reasonable
  confidence despite lacking a direct official anchor.

### Genuine gaps — reported as gaps, not fabricated numbers

- **Porridges/pasta/rice/grain products**: RTU011 (and the pyramid taxonomy generally) bundles
  oats/barley porridge (well covered domestically — barley alone is 178% self-sufficient) with rice
  (0%, not grown in Estonia at all) and pasta (typically durum wheat, which PM20 shows zero Estonian
  production of). With no data on the consumption mix between these three very different
  sub-categories, this phase reports a **range (0%-178%+) rather than a fabricated point estimate**
  — a genuinely wide, currently unresolved uncertainty, flagged for whoever next has time to find a
  consumption-mix split (Eurostat or a more granular RTU pull might help).
- **Legumes, nuts, seeds/cocoa**: no Statistikaamet production table exists for any of these — a
  Phase 5 web search for Estonian legume production and sugar-beet self-sufficiency turned up
  nothing usable either, so these remain the same documented "assumed near-zero, unconfirmed" gaps
  carried since Phase 2, not resolved this phase.
- **Sweets/snacks**: split into "raw sugar" (assumed ~0%, Estonia has no domestic sugar beet/cane
  refining industry — general knowledge, not independently re-sourced this session) and
  "manufactured sweets/snacks" (left entirely unscored — a chocolate or snack-food factory using
  imported raw sugar and cocoa doesn't have a coherent "self-sufficiency %" the way a raw
  agricultural commodity does, so forcing a number here would be more misleading than useful).

## Confirmed open items carried into Phase 6+

- The porridge/pasta/rice range is a real unresolved gap that a future consumption-mix data source
  could close — flag prominently in the dashboard rather than picking an arbitrary midpoint.
- The dairy milk-equivalent conversion factors should be checked against FAO's own published
  technical conversion table if this model is ever used somewhere the exact magnitude (not just
  direction) matters.
- The bread/oil "yield cancellation" argument is a reasonable simplification but an unproven one —
  worth a dedicated look in Phase 8's validation pass if refined-oil or flour trade data can be
  found separately from raw-commodity trade data.
- Fish's >200%/300% self-sufficiency remains the starkest example in this whole project of a
  headline ratio that overstates real food security — only ~15% of that resource stays domestic
  (Phase 2). Every dashboard view of self-sufficiency should carry this caveat prominently for fish.
