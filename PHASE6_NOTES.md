# Phase 6 notes — feed dependency adjustment & food waste treatment

Phase 6 of PLAN.md Section 7 / Sections 5.4-5.5: layer feed dependency and food waste onto the
Phase 5 supply model, presented as labelled sensitivities rather than single precise numbers (as
PLAN.md explicitly asks for both). Status: done.

## Food waste (5.5) — the stronger half of this phase

The SEI 2021 study turned out to have far more food-category detail than Phase 1 initially found —
a fresh WebFetch pass surfaced full category breakdowns for the two largest stages:

- **Households (48% of total waste, 80,564 t/year)**: vegetables 32%, prepared/cooked-food residue
  23%, fruits & berries 18%, dairy & eggs 13%, bakery 7%, meat 3%, cereals/grains 2%, fish 1%.
- **Retail (12%, 19,976 t/year)**: fruits 27%, vegetables 22%, bakery 16%, ready-to-eat 13%, meat
  11%, dairy 8%, cereals 1%, fish 2%.

Food industry, catering, and primary production (except potatoes, ~60% of that stage's losses —
already known from Phase 1) have no category breakdown in the source. This phase distributes those
remaining tonnes (51,806 t/year combined) across pyramid groups using the *same relative
proportions* observed in the household+retail category data, as an explicitly documented proxy —
not a second independent generic FAO/WRAP figure, since inventing one without being able to verify
its precision against a source would just add unfounded false confidence. This is flagged clearly
in `waste_model.csv`'s `method` column on every row.

The "prepared/cooked food" (household) and "ready-to-eat" (retail) categories are genuinely
cross-category dishes — soup, mixed meals, sandwiches — that can't be honestly attributed to one
pyramid food group. Rather than forcing them into an arbitrary split, they're kept as a separate
**21,127 t/year (12.7% of total waste) "mixed/unattributed"** line, excluded from every per-food-group
ratio.

**Output**: `data/processed/waste_model.csv` — per pyramid sub-item, waste tonnage, the resulting
*required-production inflator* (production needed = consumption × this multiplier, to also cover
everything lost before or after the plate), the household-only portion of that waste (the "free
lever" — cutting it needs no extra production, just less waste of what's already produced), and two
explicit scenario columns showing the inflator if household waste were cut 25% or 50%.

**Headline finding, and how it connects to earlier phases**: vegetables carry by far the largest
loss-adjusted gap — a 75.5% loss rate against Phase 4's RTU011-measured "eaten" consumption
(inflator 1.755), over half of it happening in the household. This is not a new anomaly — it is a
direct, now-quantified confirmation of the gap Phase 1 already flagged between RTU011's low
survey-measured vegetable intake (50 kg/year) and the much higher production-side apparent
consumption (~79 kg/year): a large share of vegetables bought or produced in Estonia are thrown
away rather than eaten, and this phase's independent SEI-based waste build lands on a strikingly
consistent story. The other end: porridge/pasta/rice/grain products has the lowest loss rate (4.9%,
inflator 1.049) of any category — bready/starchy staples waste far less than fresh produce, which
matches general food-waste literature (dry staples keep; fresh produce spoils) as well as this
Estonia-specific data.

A caveat worth stating plainly: RTU011 (Phase 4's consumption baseline) is from 2014, while the SEI
waste study is from 2020/2021 — a 6-7 year reference-year mismatch on top of the two studies using
different methodologies (dietary recall vs. waste audit). Some of the apparent loss rate could
reflect that gap rather than "true" 2024 waste behaviour. Treated as a caveat, not a reason to
discard the finding.

## Feed dependency (5.4) — the thinner half, exactly as flagged since Phase 1

This was already flagged in `DATA_SOURCES.md` Section 5 as "the thinnest data area" and "the most
assumption-heavy part of the model" — Phase 6 doesn't change that, it makes the sensitivity range
explicit rather than leaving it undone.

**Aggregate feed-tonnage balance**: using generic, widely-cited industry FCR (feed-conversion-ratio)
benchmarks — poultry 1.8, pork 2.8, beef 8.0, sheep/goat 6.0, eggs 2.2 kg feed per kg product, none
Estonia-specific — Estonia's 2024 poultry/pork/beef/sheep-goat/egg production implies **~281 kt of
total feed demand**. Known domestic feed supply (barley's disclosed feed-use, 151 kt, plus an
estimated rapeseed-meal byproduct from crushing, 80 kt) covers **~82%** of that. This 82% is a
*conservative floor*, not a precise figure — wheat/rye/oats feed-use is simply not disclosed in
Statistikaamet's 2024 pull (blank cells, not zero), so true domestic feed-grain coverage is likely
higher than 82%. Dairy cattle are deliberately excluded from this tonnage comparison since dairy
feed is predominantly grass/silage/forage, which a simple feed-grain FCR can't meaningfully
represent.

**The real point PLAN.md 5.4 asks this phase to surface**: an aggregate energy-tonnage balance
hides the *protein* dependency specifically. Estonia produces zero soybeans (PM37, confirmed
again this phase) — essentially all protein-concentrate feed is imported, regardless of how the
aggregate energy-tonnage balance looks. Pork, poultry, and eggs are concentrate-feed-heavy
monogastric systems with proportionally more imported-protein reliance than beef, sheep/goat, or
dairy, which are more grass/forage-based in typical Northern European systems. Since no Estonian
data quantifies the actual protein-feed-import share per species, this phase applies **illustrative,
clearly-labelled sensitivity bounds** rather than a computed adjustment: a -30% haircut for
poultry/eggs/pork, a -15% haircut for beef/sheep-goat/dairy — output in
`data/processed/self_sufficiency_feed_adjusted.csv`. These bounds are not derived from measured
Estonian feed-composition data; they exist to make the *qualitative point* visible and quantifiable
in the dashboard (pork's headline 72% self-sufficiency could genuinely mean closer to 50% once its
resource-based, imported-protein-feed dependency is accounted for), not to claim a specific number
is correct.

## Sanity checks

- Every category's `pct_of_total_sei_waste` across all pyramid groups plus the mixed/unattributed
  line sums to 99.5% of the SEI total (166,513 t reconstructed here vs. SEI's own rounded headline
  of ~167,000 t) — a small, expected rounding gap from the household category shares themselves
  summing to 99% (not 100%) in the source study.
- Every feed-adjusted low bound is, by construction, ≤ its headline self-sufficiency figure (no
  category "gains" self-sufficiency from the feed adjustment) — confirmed programmatically.

## Confirmed open items carried into Phase 7+

- The food-industry/catering/non-potato-primary-production waste allocation is a documented proxy
  (household+retail proportions), not independently sourced — if a future data source gives real
  category detail for those three stages, this should be revisited.
- The feed-adjusted sensitivity bounds are illustrative, not measured — Phase 8's validation pass
  should look for any Estonia-specific feed-composition or protein-import-share data that could
  tighten this range before it's presented as more than a qualitative sensitivity.
- The RTU011 (2014) vs. SEI waste study (2020/2021) reference-year mismatch applies to every loss
  rate in `waste_model.csv` and should be restated wherever these figures appear downstream.
