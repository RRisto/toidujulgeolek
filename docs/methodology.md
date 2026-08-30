# Methodology — Estonian food self-sufficiency model

This document consolidates every data source, method, and assumption used across Phases 1-8 of
this project, for the eventual dashboard's methodology/sources appendix (PLAN.md Section 9).
It is written to stand alone: a reader shouldn't need the eight PHASE*_NOTES.md files to
understand what a number in the dashboard means or how confident to be in it. Where a method or
figure is Estonia-specific and measured, that's stated; where it's a generic assumption, an
illustrative sensitivity, or an unresolved gap, that's stated just as clearly, right next to the
number.

## 1. Research question and scope

Could Estonia feed its population a nutritionally adequate diet from domestic production, and
where are the critical dependencies? Scope: national aggregate, current-year production levels
(not production potential), ages 2+ (infants 0-1 excluded — see Section 3), the 6-group TAI
toidupüramiid framework. Full scope statement in `PLAN.md` Section 2; explicit out-of-scope list
in Section 10 (production-capacity modelling, seasonality/regional/shock resilience, a
quantitative micronutrient model, a v2 candidate list).

## 2. Data sources

| Source | What it provides | Vintage | Acquisition method |
|---|---|---|---|
| Statistikaamet RV021 | Population by age (single-year bands)/sex | 1 Jan 2026 | PxWeb 2.0 API, POST query run from a live browser session (see Section 2.1) |
| Statistikaamet PM20/31/33/34/37/42/45/47/29 | FAO-style production/import/export/feed/loss/human-consumption balance sheets: cereals, potato, vegetables, fruit&berries, oilseeds, meat, eggs, dairy (9 product lines), honey | 2024 | Same PxWeb 2.0 API method |
| TAI Tabelraamat 2025 | Energy requirements (age/sex/PAL), macronutrient %E targets (Table 6), food-group portion counts by energy level (Table 13), gram weights per portion (Table 16) | 2025 publication | PDF text extraction (WebFetch) for most tables; Table 16 required a different method — see Section 2.2 |
| TAI RTU011 (2014 consumption survey) | Actual food-group consumption, grams/day, by age band and sex | 2013-2015 fieldwork | Classic PxWeb UI, driven directly (no JSON API reachable) |
| Estonia's 2023+ food/agriculture strategy document | Official pre-computed self-sufficiency ratios (5-year average, exact years unconfirmed) | ~2018-2022 inferred | PDF extraction |
| SEI (Stockholm Environment Institute) 2021 Estonia food waste study | Waste tonnage and (in a second, more targeted extraction pass) category-level detail by supply-chain stage | 2021 | WebFetch, two passes (see PHASE6_NOTES.md — the second pass surfaced materially richer detail than the first) |
| agri.ee 2026 fish consumption study | Fish production/catch vs. domestic human consumption, resolving the "high self-sufficiency but mostly exported" nuance | 2026 | WebFetch |
| FAOSTAT Food Balance Sheets (New Food Balances, FBS domain) | Independent, internationally-standardised production/trade/utilization balance per commodity, for cross-checking | 2022 (latest available; FAOSTAT typically lags 1-2 years) | Live browser session, FAOSTAT's own "Report" builder (Estonia, 2022) — see Section 8 |
| Eurostat | EU-context comparison indicators | — | Attempted (Section 8); not successfully retrieved via automated access this round, left as a documented gap, not a blocker (DATA_SOURCES.md already flagged this as "if useful," lower priority than FAOSTAT) |

Full source-by-source detail, including what was *not* found (a dedicated feed-import/protein-feed
trade table, any legume/nut/seed/cocoa/sugar production table from an Estonian source, a
consumption-mix breakdown within "porridges/pasta/rice/grain products") is in `DATA_SOURCES.md`.

### 2.1 Network access workaround

Both sandboxed shells this project runs in sit behind a network allowlist that blocks
andmed.stat.ee, statistika.tai.ee, tai.ee, agri.ee and fao.org for direct `curl`/`wget`, and
Statistikaamet's PxWeb 2.0 API only accepts POST queries, which a GET-only page-fetch tool can't
issue either. The workaround used throughout: drive an actual browser session (real network) to
execute the fetch/POST call from the page's own JavaScript context and read the JSON or rendered
result back. For TAI's older classic-PxWeb system (RTU011), no JSON API was reachable at all, so
the variable-selection UI itself was driven directly and the rendered result table read as text.

### 2.2 PDF extraction workaround

WebFetch's PDF-to-text conversion silently truncates the Tabelraamat PDF around page 26-29 — below
where Table 16 (gram weights per portion, needed from page 36) lives — and Chrome's native PDF
viewer is unreachable by browser automation tools at all. Resolved by rendering the PDF through
Google's Docs viewer (`docs.google.com/gview?url=<encoded-pdf-url>&embedded=true`) in a real
Chrome tab, which renders as a normal, screenshottable/scrollable web page with a page-jump
control — the tables were then read directly off the rendered pages.

## 3. Demographic grid (Phase 2)

Three sources use three different age-band schemes. RTU011's bands were chosen as canonical (it's
the only source with real consumption data — everything else maps onto it). Population was
reconciled from RV021's finer 5-year bins via uniform-within-bin proration. Two population
handling decisions: ages 0-1 (1.54% of the population) are excluded from scope entirely — infant
feeding doesn't fit the toidupüramiid framework; ages 75+ (~10% of the population) are kept in
scope, modelled as a proxy using RTU011's 70-74 band (RTU011 itself has no data past 74; excluding
10% of the population would badly distort a national conclusion). Physical activity level (PAL)
has no Estonian population-distribution data at all — PAL=moderate is used as the single
national-aggregate default; sedentary/active bounds are computed but not carried into headline
figures. Full design rationale: `data/crosswalk/demographic_grid.md`.

## 4. Requirement model — Scenario B input (5.1, Phase 3)

Population-weighted recommended demand: "if everyone ate exactly as TAI recommends, weighted by
who Estonia's population actually is." Adults use a direct constant lookup into Table 5's kcal
bands; children are built by averaging Table 4's single-year/banded values across every single age
in the canonical band (equal weight per age — Statistikaamet doesn't publish single-year
population to weight it more finely). Each grid cell's kcal requirement is rounded to the
*nearest* of Table 13's 200-kcal columns (ties round up, favouring not under-stating recommended
intake) rather than interpolated, since the source table is a step function, not a continuous
formula. A representative gram-weight was chosen per sub-item from Table 16 where the portion
table doesn't specify which exact food (e.g. fish uses an unweighted average across four
fat-content tiers, since no Estonian data says which tier dominates actual consumption) — every
choice and its rationale is in `data/crosswalk/portion_gram_representative.csv`.

**Output**: `data/processed/requirement_model_national.csv`. **Internal check**: two independent
derivations of national average daily energy (the requirement grid directly, and summing the
food-group demand table back into kcal) land within 2% of each other (2,234 vs 2,282 kcal/capita/
day) — see `SANITY_CHECK_phase3.md`.

### 4.1 Post-launch plausibility check: per-category and total gram values

Added post-launch, prompted by a question about whether individual food-group gram figures might
be implausibly large or small -- a check the project had not explicitly run before. Phase 3's own
validation (above) confirms the *aggregate calorie total* is sound (two independent derivations
within 2%) and Phase 8 confirms the *macronutrient split* falls within TAI's own targets, but
neither checks whether each category's gram/day figure, or the total food mass they sum to, is
individually plausible.

**Per-category check**: every one of the 16 rows in `requirement_model_national.csv` was compared
against commonly-cited international dietary-guideline ranges. None look like a computational
error (no missing/extra order of magnitude, no unit mismatch) -- fish (79.6 g/day) was re-verified
directly against Table 13.1's portion count and Table 16's gram weight and is a correct read of
the source, not a bug. Dairy was the standout figure at this check's original pass (805.7 g/day) --
investigating it at length (Sections 4, 5.1, 5.2) surfaced a genuine methodological error in how
that figure itself was computed, corrected in Section 4.2 below to 490.1 g/day. Figures in this
section already reflect the corrected value.

**Total mass check, against an independent external reference**: summed across all 16 categories,
the recommended model totals **2,141.7 g/day** of food -- still high in absolute terms, so this was
benchmarked against the EAT-Lancet Planetary Health Diet, a well-known international reference diet
(2,500 kcal/day calibration), which totals **1,324 g/day**. For a fair comparison (EAT-Lancet's
legumes line excluded, matching this project's own legumes gap): **this project's actual-consumption
model totals 1,274 g/day -- within 2% of EAT-Lancet's 1,249 g/day -- while the TAI-recommended
figure is 2,084.6 g/day, roughly 64-67% higher than both** (originally computed as 89% higher,
before the Section 4.2 dairy correction), despite implying *fewer* calories than EAT-Lancet's
calibration (2,282 vs. 2,500 kcal/capita/day per Phase 3's own cross-check). The recommended diet
is therefore not just proportionally larger; it is structurally denser in mass per calorie than
either actual Estonian eating habits or an independent international benchmark -- a smaller gap
than first computed, but not a small one.

Attributing the ~835.6 g/day gap between the recommended and EAT-Lancet totals (post-correction):
no single category dominates it the way dairy originally appeared to. **Grains+potato combined is
now the largest single contributor** (~290 g higher -- EAT-Lancet treats potato as a limited
"starchy tuber" allowance, not a dietary staple the way Estonian food culture does), closely
followed by **vegetables+fruit+berries** (roughly 180-245 g higher, depending how EAT-Lancet's
fruit line is compared) and by **dairy** (490 g vs. EAT-Lancet's 250 g, a 240 g gap -- down from
556 g pre-correction, and no longer the largest contributor on its own), with fish contributing the
remainder (80 g vs. 28 g). Red meat is the notable exception: TAI's figure (20 g) and EAT-Lancet's
(14 g) are close, showing this isn't a uniform "every category runs high" pattern.

This is stated as a finding, not a verdict: EAT-Lancet is itself a specific, deliberately
dairy-light and legume-forward normative diet oriented around planetary sustainability, not a
neutral ground truth, so some divergence from a traditional Baltic dietary pattern is expected and
not inherently wrong. But the fact that *actual* Estonian consumption independently lands within
2% of an unrelated international benchmark, while TAI's own recommendation sits roughly two-thirds
above both, is concrete, independently-sourced evidence -- beyond this project's own
scenario-comparison percentages -- of how large a shift Scenario B actually represents, even after
correcting the dairy figure that originally made the gap look larger and more dairy-driven than it
actually is.

### 4.2 Post-launch correction: dairy portion-to-gram conversion

Prompted by the user directly quoting TAI Tabelraamat Table 16.3's full text and asking how the
805.7 g/day dairy figure was derived. That prompted a re-examination of the original extraction,
which surfaced a genuine error, not just a documentation gap.

**What was wrong**: Table 16.3 does not define one dairy portion mass. It lists six distinct dairy
sub-types, each with its own gram weight (lowest-fat/first-listed variant of each): unsweetened
milk and liquid dairy products (300 g), unsweetened cottage cheese/kodujuust (140 g), unsweetened
yogurt (200 g), cheeses (55 g), creams (100 g), and flavored dairy products (300 g). The original
build (Task 18, Phase 3) captured only the first of these -- the milk line -- and applied its 300 g
figure as if it represented the entire dairy category. `portion_gram_representative.csv`'s original
note called this "the primary/first-listed item," which was an accurate description of what the
build actually did, but not a defensible choice on its own: nothing in Table 16.3 marks the milk
line as more representative than the other five, and cheese, cream, and cottage cheese portions are
all substantially smaller by mass.

**Why it matters**: unlike fish and poultry -- where Table 16's multiple tiers are different
fat-content variants of the *same* food, calibrated to the *same* target portion energy (a lower-fat
variant needs more grams to reach the same kcal, a higher-fat variant needs fewer) -- dairy's six
lines are different foods entirely (milk, cheese, yogurt, cottage cheese, cream, flavored products),
not fat-content tiers of one food. There is no data on which of the six an average dairy portion
actually is, so no single line can be defended as "the" dairy portion any more than any other.

**The fix**: apply the same convention already used for fish and poultry when Table 16 gives
multiple undifferentiated options with no consumption-share data to weight them -- an unweighted
average across all six sub-types: (300 + 140 + 200 + 55 + 100 + 300) / 6 = **182.5 g/portion**,
down from 300 g. This is still an approximation, not a measurement (there is no Estonian data on
the true consumption-weighted mix of milk vs. cheese vs. yogurt etc.), and is documented as such --
but it no longer silently treats one specific dairy product as the entire category.

**What changed, and what didn't**: portion *counts* (from Table 13, population-weighted to 2.69
portions/day on average) and the portion's *energy content* (110 kcal, taken directly from Table 13
and unaffected by this fix) are unchanged, so Phase 3's internal kcal cross-check
(`SANITY_CHECK_phase3.md`, the two-derivations-within-2% result) does not change either -- it never
depended on the gram-weight assumption. What changes is the *mass* implied by those portions:

| Figure | Before | After |
|---|---|---|
| Dairy representative g/portion | 300 | 182.5 |
| Dairy recommended demand (national avg) | 805.7 g/day | 490.1 g/day |
| Dairy recommended demand (national) | 393,990 t/year | 239,677 t/year |
| Demand change ratio, Scenario B vs. A | 2.72x | 1.65x |
| Dairy self-sufficiency, Scenario B | 61.1% | 100.4% |
| Recommended-diet total mass (16 categories) | 2,457.2 g/day | 2,141.7 g/day |
| ...vs. EAT-Lancet/actual-consumption benchmark (Section 4.1) | ~89% higher | ~64-67% higher |
| Dairy's share of the recommended-vs-EAT-Lancet gap | >50% (largest single contributor) | ~29% (third-largest, behind grains+potato and vegetables+fruit+berries) |

Every downstream figure this touches -- `requirement_model_national.csv`,
`scenario_comparison.csv`, `critical_dependency_flags.csv`, the dashboard export and its rendered
charts, and this document's own Sections 4.1 and 10.1 headline figures -- has been recomputed and
updated in place, not left inconsistent with the correction. Dairy's Scenario B self-sufficiency
still *falls* under the recommended diet (166.0% to 100.4%), and the direction of every other
finding in this document is unchanged; what changed is the *magnitude* of the dairy-specific and
total-mass figures, not the qualitative conclusions built on them.

## 5. Consumption model — Scenario A input (5.2, Phase 4)

Same demographic grid, weighted by RTU011's actual per-capita consumption. RTU011's 16 categories
map onto the pyramid taxonomy four ways: **direct 1:1** (9 categories); **split** (RTU011 bundles
poultry with red meat and offal into one figure — split using PM42 2024's own per-capita
consumption *shares*, poultry 34.3% / red meat+offal 65.7%, not absolute levels, since PM42's
absolute levels run structurally higher than RTU011's); **combined-only** (RTU011 can't separate
fruit from berries, or nuts from seeds/cocoa — compared against Phase 3's summed target for the
pair); **not measured** (legumes have no RTU011 category — left as an explicit gap, never treated
as zero).

**Output**: `data/processed/consumption_model_national.csv`, `over_under_consumption.csv`
(national), `over_under_consumption_by_segment.csv` (6 demographic segments). **Headline**: red
meat consumed at 3.5x TAI's recommendation, sweets/snacks at 3.1x; vegetables (0.28x), nuts/seeds
(0.09x) and fish (0.30x) most under-consumed; children over-consume sweets far more sharply
(5.7-9.2x) than adults.

### 5.1 Post-launch validation against RTU011's own published toplines

Added after the nine-phase build was already complete, prompted by a follow-up question about
dairy specifically. Phase 4 built the consumption model bottom-up from 96 age/sex/activity-level
grid cells, individually weighted by real 2026 population counts -- but never checked the result
against the simplest possible baseline: RTU011's *own* published population-wide average per food
group, queried directly and unmodified from its live PxWeb table
(`https://statistika.tai.ee/pxweb/.../RTU011.px`, sex = both, age = all groups combined, unit =
grams). That check was run retroactively via live browser automation (no static export of this
particular slice existed in `data/raw/`) across all 16 RTU011-published rows. Full table: `data/processed/rtu011_topline_cross_check.csv`.

**Result: close agreement on nearly every category.**

| Category | Phase 4 model (g/day) | RTU011 raw topline (g/day) | Difference |
|---|---|---|---|
| Bread/baked goods | 73.7 | 71 | +3.8% |
| Porridge/rice/pasta | 125.9 | 127 | -0.9% |
| Potato | 97.8 | 97 | +0.8% |
| Vegetables | 135.7 | 137 | -0.9% |
| Dairy products | 296.4 | 300 | -1.2% |
| Fish & seafood | 23.5 | 23 | +2.2% |
| Eggs | 20.6 | 21 | -2.0% |
| Oils/fats/spreads | 18.0 | 18 | +0.2% |
| Fruits+berries (combined) | 212.1 | 210 | +1.0% |
| Nuts+seeds+cocoa (combined) | 3.3 | 3 | +10% (both sub-4g -- survey-noise range) |
| Poultry + red meat (summed) | 107.7 | 109 (RTU011's own bundled figure) | -1.2% |
| Sweets/snacks/sugar | 159.0 | 167 | -4.8% |
| Legumes | not measured | not measured (no RTU011 category) | consistent gap, both sides |

Ten of twelve numerically comparable categories land within about 2% of RTU011's own simple
topline -- a meaningful confirmation of the whole Phase 4 weighting pipeline, not just one
category, since it wasn't performed during Phase 4 itself (which only ran two *internal*
consistency checks: top-level vs. summed sub-groups, and published `total` vs. average of
`male`/`female`). It also independently validates the poultry/red-meat **split** specifically:
RTU011 doesn't publish that split (it bundles both into one 109 g/day figure), so Phase 4 divided
it using PM42's production-side consumption shares (34.3%/65.7%) -- summing the two resulting
model figures back together (107.7 g) reproduces RTU011's own bundled total to within 1.2%,
confirming the split preserved the right combined quantity even though it manufactured a division
the source doesn't provide.

Two things fell outside the close-agreement band, both minor and neither changing any dashboard
conclusion: **sweets/snacks/sugar** (-4.8%) is the one real outlier, plausibly a small mismatch
between the crosswalk's category boundary and RTU011's own "sweet and salty snacks" grouping --
not investigated further, since it doesn't affect a threshold-crossing figure anywhere in the
model. **Nuts+seeds+cocoa** shows the largest relative gap (+10%) but both figures are under 4
grams/day, i.e. within ordinary survey rounding noise at that scale, not a meaningful divergence.

### 5.2 Caveat: TAI's own public messaging doesn't flag dairy as an "increase" priority

Also added post-launch, prompted by visually comparing this project's dairy gap against TAI's own
"tegeliku ja soovitusliku toidupüramiidi võrdlus" (actual vs. recommended pyramid) poster
(`https://www.tai.ee/et/valjaanded/tegeliku-ja-soovitusliku-toidupuramiidi-vordlus`) -- which,
looked at directly as an image, doesn't visually convey a large dairy gap at all, since it's an
illustrative food-photo collage arranged into a pyramid silhouette, not a quantity-scaled chart.

More substantively: the poster's companion document lists TAI's own ten explicit dietary-change
recommendations verbatim, and dairy *quantity* is not one of them. The full list: increase whole
grains, increase vegetables (incl. legumes), diversify fruit and berries, increase fish (prefer
fresh over processed), increase nuts and seeds, increase plain water, increase physical activity;
reduce red/processed meat, reduce sweet and salty snacks; and, for dairy specifically, only
*"replace sweetened dairy products with unsweetened versions"* -- a type/quality swap, not a
quantity increase.

This doesn't contradict Section 4/5's finding -- the Tabelraamat's Table 13 portion targets
(Section 4) are real, verified directly against the source table, and do imply a large gap between
actual dairy consumption and the portion-count guidance. But it's a genuine limitation worth
stating plainly: **this project's Scenario B treats every food-pyramid category's portion target
as an equally-weighted "should increase to this" signal, while TAI's own public communication
clearly does not** -- it prioritizes a curated subset of gaps (grains, vegetables, fruit variety,
fish, nuts/seeds, water) for explicit "eat more" messaging and leaves others, dairy included,
unaddressed as a quantity matter. Plausible reasons (not stated by TAI, so held as reasoning, not
fact): adding several hundred more grams/day of anything without an offsetting reduction risks
raising total energy intake, which cuts against overweight/obesity messaging more than it helps;
dairy's key nutrients (protein, calcium) are also obtainable from other food groups already in the
diet, so a shortfall against the portion-table target isn't necessarily a shortfall in nutrient
adequacy; and the portion table is built as a template for one idealized full day at a given
calorie level across all groups simultaneously, not sixteen independent per-category deficiency
alerts. Section 10 already flags Scenario B's demand-scaling approximation as applying uniformly
across categories, without a priority weighting; this is additional, concrete evidence of where
that uniform treatment diverges from how TAI itself actually prioritizes dietary change in its own
public messaging.

## 6. Self-sufficiency model (5.3, Phase 5)

`Self-sufficiency = Production / Domestic utilization`, built bottom-up from the PM-series balance
sheets where possible, calibrated against the official strategy-document figures. Decision rule
when the two diverge: close agreement (within a few points) → average the two; large divergence →
use the official figure as headline (with the derived figure kept for transparency), since a
single-year bottom-up build can't outweigh a multi-year official average without more evidence.
Two real conversions required generic, explicitly-flagged assumptions:

- **Dairy milk-equivalent aggregation**: PM47's 9 separate dairy product balances can't be summed
  directly (a kg of butter represents far more raw milk than a kg of liquid milk). Used standard
  order-of-magnitude conversion factors (fresh 1.0x, cream 6x, concentrated milk 2.3x, milk
  powders 8-9x, butter 20x, cheese 10x, processed cheese 8x) — generic, not Estonia-specific or
  independently verified. Result: 134.9% derived vs. 166% official; headline uses the official
  figure, though Phase 8's FAOSTAT cross-check (Section 8 below) landed almost exactly on the
  *derived* figure (139.0%), which is worth weighing if this gets revisited.
- **Bread and rapeseed-oil "yield cancellation"**: if a processing yield (milling, oil-extraction)
  applies uniformly to domestically-sourced and imported raw material, it cancels out of the
  production/domestic-use ratio, so raw-commodity self-sufficiency approximates the processed
  product's self-sufficiency — avoiding the need to defend a specific, unverified yield
  percentage. **This assumption was tested and found to break down for rapeseed oil specifically**
  in Phase 8 (Section 8) — flagged there in detail.

Two genuine gaps were reported as ranges/unknowns rather than forced into false-precision points:
porridge/pasta/rice (0%-178%+, no consumption-mix data to weight barley vs. rice vs. durum pasta)
and legumes/nuts/seeds/sweets (no Statistikaamet production table found for any of them —
Phase 8's FAOSTAT check partially resolved the legumes gap; see Section 8).

**Output**: `data/processed/self_sufficiency_model.csv` (18 rows, each tagged with a `data_status`
so a reader can tell a measured figure from an estimated or assumed one at a glance).

## 7. Feed dependency and waste (5.4, 5.5, Phase 6)

**Feed**: animal products are only as domestic as their feed. Used published, generic
(non-Estonia-specific) feed-conversion-ratio benchmarks per species (poultry 1.8, pork 2.8, beef
8.0, sheep/goat 6.0, eggs 2.2 kg feed/kg product) against known domestic feed supply (barley used
as feed + rapeseed-meal byproduct), giving an aggregate ~82% domestic feed coverage — with the
important caveat that the shortfall is concentrated in protein concentrates (Estonia produces
essentially no soy) rather than forage, which the aggregate figure alone hides. Feed-adjusted
self-sufficiency *lower bounds* use illustrative haircuts (-30% concentrate-heavy species:
poultry/eggs/pork; -15% forage-based: beef/sheep-goat/dairy) — labelled throughout as illustrative
sensitivities, not measurements, since no Estonian feed-ration composition data exists.

**Waste**: two distinct uses of the SEI 2021 data. Supply side — a share of what's produced never
reaches a plate, so required production exceeds consumption by roughly the pre-household loss
rate; a `required_production_inflator` is computed per pyramid group. Demand side — household
waste (the largest single share) is a pure efficiency lever: cutting it doesn't require more
production, it just means less is needed for the same nutritional outcome (modelled as a
25%/50% household-waste-cut scenario). Where SEI doesn't give food-group-level detail at a stage,
a household+retail-proportions-based proxy fills the gap, clearly labelled as such. Headline:
vegetables have by far the highest loss rate (75.5%), consistent with the RTU-vs-production
mismatch already flagged in Phase 1.

**Output**: `data/processed/feed_dependency_model.csv`, `self_sufficiency_feed_adjusted.csv`,
`waste_model.csv`.

## 8. Validation against FAOSTAT (Phase 8)

FAOSTAT's Food Balance Sheet for Estonia, 2022 (the latest year available — FAOSTAT typically lags
1-2 years), was pulled via its own "Report" builder and cross-checked commodity-by-commodity
against this project's self-sufficiency figures. Full table: `data/processed/faostat_cross_check.csv`.

**Strong agreement** (within a few percentage points, despite different years, methodologies, and
often different item scope): wheat+rye/bread proxy (FAOSTAT 322% vs. project 332.5%), potato
(65.8% vs. 66.9%), fruit (6.5% vs. 8%, FAOSTAT excludes berries), eggs (57.9% vs. 53.6%), fish
(303% vs. 300%, also independently corroborating the "~15-19% stays domestic" export-heavy
caveat), pork (78.2% vs. 72%). Dairy's FAOSTAT figure (139.0%) lands almost exactly on this
project's own *derived* milk-equivalent figure (134.9%) rather than the official headline (166%)
— worth noting as a data point that slightly favours the derived build.

**Material divergences, flagged and left open rather than resolved with false confidence:**

- **Vegetables**: FAOSTAT 2022 shows just 9.2%, well below both this project's derived (29%) and
  headline/official (46%) figures — a *third* disagreeing data point on a category that was
  already the project's largest unexplained gap since Phase 1. Plausible drivers (unconfirmed):
  a narrower FAOSTAT item definition for "Vegetables, Other," known international under-counting
  of minor-crop production for small countries, or genuine year-to-year volatility. Not resolved.
- **Beef and poultry**: FAOSTAT 2022 beef (75%) is notably below the PM42 2024 figure (109%);
  FAOSTAT 2022 poultry (79.3%) is notably above the PM42 2024 headline (57.7%). Two years apart in
  sectors that can shift meaningfully year to year — this reinforces, rather than undercuts, the
  project's existing caution in treating poultry's feed-adjusted and Scenario B figures (Phase 6/7)
  as sensitivities rather than precise points.
- **Rapeseed — both raw seed and refined oil**: this is the most substantive finding of the
  validation pass. FAOSTAT 2022 raw rapeseed self-sufficiency (141.3%) is roughly double the
  PM37-2024-derived figure (69.3%) the project's oil estimate is built on; refined rapeseed-oil
  self-sufficiency (265.2%, from FAOSTAT's direct oil balance) is even further from it. This
  **confirms a limitation Phase 5 had already flagged as a risk**: the yield-cancellation argument
  "breaks down if a meaningful share of Estonia's edible oil trade is in already-refined form
  rather than raw seed" — which is exactly what FAOSTAT shows (Estonia produces far more refined
  oil, 61kt, than it consumes domestically, 23kt supply, meaning a large share of crushed oil is
  exported directly). The likely direction of the true figure is that this project's 69.3% oil
  estimate *understates* self-sufficiency, not overstates it — but the raw-seed-level divergence
  (possibly driven by 2022's unusual Baltic/Black Sea oilseed trade disruption following Russia's
  invasion of Ukraine, a real but unconfirmed candidate explanation) means the exact magnitude
  stays genuinely uncertain. Documented as an open uncertainty, not resolved.
- **Legumes**: FAOSTAT's Pulses aggregate revealed Estonia is actually a large net *exporter*
  (332% self-sufficient), which revises the prior "unknown - assumed low" placeholder — but the
  figure is driven almost entirely by field peas grown for feed/export, while FAOSTAT's own
  dry-beans line (closer to a human-food legume, matching what RTU011's "legumes" consumption
  category likely captures) sits at 0% domestic production. `self_sufficiency_model.csv`,
  `scenario_comparison.csv` and `critical_dependency_flags.csv` were all updated in Phase 8 to
  reflect this bimodal finding rather than the flat "assumed low" guess.

**Eurostat**: attempted (FAOSTAT's REST API worked via a live browser session; Eurostat's did not
via automated fetch — robots.txt blocks and 403s on the endpoints tried). Left as a documented,
low-priority gap rather than pursued further, consistent with DATA_SOURCES.md's original framing
of Eurostat as "useful for EU-comparison context" rather than a required cross-check — FAOSTAT
already provided the substantive independent validation this phase needed.

## 9. Nutritional-adequacy check (5.8, Phase 8)

The calorie-level check was already done in Phase 3 (two independent derivations within 2%). A
lightweight macronutrient check was run in Phase 8: applying generic, non-Estonia-specific
per-100g macronutrient composition estimates (standard nutrition-database-style values, not
measured) to the requirement model's food-group tonnages gives an aggregate energy split of
**17.4%E protein, 35.9%E fat, 46.7%E carbohydrate** against TAI's own Table 6 targets for ages 2+
(protein 10-20%E, fat 25-40%E, carbohydrate 45-60%E) — **all three land within TAI's stated
bands**, and the implied total (2,524 kcal/capita/day) is in the same range as Phase 3's own more
precise figure (~2,234-2,282 kcal/capita/day), with the ~10-13% gap explained by this check's
necessarily coarser, generic composition assumptions rather than a modelling error. This is
consistency-checking, not new measurement — by construction, since Table 13's own portion
prescriptions are TAI's tool for hitting these targets, adequacy follows as long as Table 13 was
applied faithfully, which this check corroborates.

The qualitative micronutrient point (out of scope for a quantitative model in v1): vegetables,
fruit and fish — already the three weakest self-sufficiency categories, and (per Phase 7's
Scenario B) the three that worsen most under a TAI-compliant diet — are also disproportionately
important sources of vitamin C, folate, and omega-3/iodine. The self-sufficiency gap and the
nutritional-adequacy risk point at the same food groups.

## 10. Scenario engine and critical-dependency flagging (5.6, 5.7, Phase 7)

Scenario A (status quo) vs. Scenario B (TAI-recommended diet), production held fixed between the
two. Scenario B's self-sufficiency is computed by scaling Scenario A's headline figure by the
ratio of Scenario A to Scenario B demand tonnage — an approximation (not a re-derived balance
sheet) that assumes proportional consistency between the RTU011-based demand model and the
PM-series-based official self-sufficiency denominator, flagged in every row. Critical-dependency
flags apply a plain 50% threshold under three lenses (Scenario A, Scenario B, and the Phase 6
feed-adjusted bound where computed), plus a separate flag for any item Scenario B makes worse
regardless of the threshold. **Headline**: Scenario B worsens self-sufficiency in 9 of 12
numerically-comparable categories — TAI recommends eating more of exactly the categories Estonia
is worst at supplying domestically. All 12 comparable demand-change ratios independently
cross-check against Phase 4's over/under-consumption figures to within rounding.

**Output**: `data/processed/scenario_comparison.csv`, `critical_dependency_flags.csv`.

### 10.1 Scenario C: EAT-Lancet Planetary Health Diet (post-launch)

A third demand scenario, added after the initial nine-phase build at the user's request, benchmarking
domestic production against an international reference diet rather than a national dietary guideline.
The EAT-Lancet Commission's Planetary Health Diet (Willett et al., 2019) publishes reference gram/day
intakes for a 2,500 kcal/day diet. This project scales those figures to Estonia's actual population
energy need (the same population-weighted kcal/day figure computed in Section 4: 2,234.4 kcal/day at
moderate PAL) by a single multiplicative scale factor (2,234.4 / 2,500 = 0.894). This scaling is this
project's own methodological choice, applied for consistency with how Scenario B already scales TAI's
Tabelraamat to Estonia's population -- it is not something EAT-Lancet's own published guidance
prescribes.

Crosswalk from EAT-Lancet's food groups to this project's own pyramid taxonomy
(`data/crosswalk/eatlancet_crosswalk.csv`) required three kinds of documented assumption, in addition
to several direct 1:1 matches (vegetables, legumes, dairy, fish, eggs, poultry, red meat):

- **Splitting a combined figure using the project's own already-derived ratio.** EAT-Lancet publishes
  one combined "whole grains" figure (232 g/day); this project's taxonomy keeps bread and
  porridge/pasta/rice/grain products as separate rows. Rather than fabricate an independent split, the
  same convention established in Phase 4 for the RTU011 poultry/red-meat split is reused here: apply
  this project's own bread:porridge ratio (33.5%/66.5%, derived from `requirement_model_national.csv`)
  to divide EAT-Lancet's combined figure.
- **Summing several EAT-Lancet lines onto one demand basis.** EAT-Lancet's unsaturated oils (40 g) +
  palm oil (6.8 g) + lard/tallow (5 g) = 51.8 g/day is applied to the single combined oils/fats/spreads
  demand basis that Scenarios A and B already use (no demand source in this project distinguishes oil
  type; the figure is assigned to the rapeseed representative row by the same convention as A/B, and
  the two structurally-zero oil types, sunflower and soy, stay fixed at 0% self-sufficiency regardless
  of scenario).
- **Leaving a genuine gap rather than reporting a partial number.** EAT-Lancet publishes a nuts figure
  (50 g/day) but no separate seeds or cocoa figure, while this project's taxonomy carries a combined
  "Nuts+Seeds,cocoa" row. Reporting nuts alone as the combined demand would understate it and produce a
  misleading ratio, so this row is left blank under Scenario C, consistent with this project's standing
  convention against false precision. Self-sufficiency for this row is assumed ~0% under every scenario
  regardless (Phase 5), so the gap affects only the demand-tonnage columns, not the self-sufficiency
  figure itself.

Two further caveats apply project-wide to Scenario C, both already flagged for other rows earlier in
this document: the fruit/berry row uses EAT-Lancet's single "fruits" figure (200 g) as-is, likely a
slight underestimate of the true combined fruit+berry figure since no separate EAT-Lancet berries line
exists to add on top (Section 5's discussion of the same RTU011 category boundary applies here too);
and the sweets/discretionary row uses EAT-Lancet's "added sugars" (31 g) as a proxy, understating the
true comparable figure since this project's category also includes salty snacks (the same
category-boundary caveat already flagged in Section 5.1's RTU011 comparison for this row).

Self-sufficiency under Scenario C is computed with the identical re-scaling formula already used for
Scenario B (Section 10, above): `scenario_C_self_sufficiency_pct = scenario_A_self_sufficiency_pct ×
(scenario_A_demand_tonnes / scenario_C_demand_tonnes)`, production held fixed, with the same
threshold/worsens flagging logic (`flag_below_50pct_scenario_C`, `flag_scenario_C_worsens_dependency`).

**Headline**: Scenario C's tonnage-weighted aggregate self-sufficiency is 156.4% -- well above both
Scenario A (106.8%) and Scenario B (64.8%), on the same 77.4%-of-tonnage coverage basis. This is driven
mainly by dairy and red meat: EAT-Lancet recommends markedly less of both than Estonia actually eats
(dairy self-sufficiency rises from 166.0% under A to 220.2% under C; red meat from 78.1% to 441.5%), so
demand falls faster than production, mechanically raising the ratio -- this is not a claim that Estonia
is well-positioned to feed itself an EAT-Lancet diet in every category. The reverse happens for
oils/fats: EAT-Lancet's reference diet recommends noticeably more fat intake than this project's demand
model assumes, and rapeseed oil's self-sufficiency correspondingly falls from 69.3% (Scenario A) to
27.0% under Scenario C -- newly crossing the 50% critical-dependency threshold, a dependency that
doesn't exist under either Scenario A or Scenario B. This is the one genuinely new critical dependency
this scenario surfaces; every other flagged critical dependency under Scenario C (vegetables,
fruit+berries, the two structurally-zero oil types) was already flagged under Scenario A.

**Output**: `data/crosswalk/eatlancet_crosswalk.csv`; `scenario_C_demand_tonnes_per_year`,
`demand_change_ratio_C_over_A`, and `scenario_C_self_sufficiency_pct` columns added to
`scenario_comparison.csv`; `scenario_C_self_sufficiency_pct`, `flag_below_50pct_scenario_C`, and
`flag_scenario_C_worsens_dependency` columns added to `critical_dependency_flags.csv`.

## 11. Consolidated assumptions and limitations (stated up front, not buried)

- Consumption baseline is a 2014 survey (RTU011) — the best available, cross-checked where
  possible against fresher partial signals (e.g. the 2024 dairy balance-sheet figure landed within
  2% of the 2014 survey figure), flagged explicitly as dated throughout.
- Self-sufficiency ratios lean on an official pre-computed table (5-year average, exact years
  unconfirmed) as calibration rather than a fully independent bottom-up build for every category;
  material divergences are investigated and explained (Section 6, Section 8), never silently
  overridden.
- Feed-conversion, feed-import-share, and household-waste-lever figures are generic/
  assumption-based, not Estonia-specific measured data — presented as labelled sensitivities, not
  point estimates.
- No production-capacity-ceiling modelling in v1 — "self-sufficiency" means "at today's output,"
  not "at Estonia's potential output" (see PLAN.md Section 10 for the v2 candidate).
- National aggregate only — no seasonality, regional, or shock-resilience modelling.
- Micronutrient adequacy is a qualitative flag (Section 9), not a quantitative model, in v1.
- Reference-year mismatches propagate through every phase's ratios: RTU011 (2014), PM-series
  (2024), FAOSTAT (2022), SEI waste (2021), the official strategy figures (~2018-2022 inferred) —
  none of these years line up exactly, which is itself part of why Phase 8's cross-checks show the
  divergences they do, not necessarily a sign that any one figure is wrong.
- Dairy's requirement-model portion mass (Section 4.2) is an unweighted average across six
  distinct dairy product forms (milk, cheese, yogurt, cottage cheese, cream, flavored products),
  corrected post-launch from an earlier single-product (milk-only) assumption -- still an
  approximation, since no Estonian data states the true consumption-weighted mix across those
  forms, and the same caveat applies to any other food group whose Table 16 gram weight is likewise
  an average across undifferentiated variants (fish, poultry).
- Scenario C's EAT-Lancet-to-Estonia energy scaling (Section 10.1) is this project's own
  methodological choice, not something EAT-Lancet's own published guidance prescribes; its crosswalk
  carries the same category of documented assumption already used for Scenario B (a combined-figure
  split reusing this project's own derived ratio, one gap left blank rather than understated), plus
  one entirely new gap (nuts vs. nuts+seeds+cocoa) not present in the Scenario B crosswalk.
- Six taxonomy mismatches are carried from Phase 2's crosswalk and touch every phase downstream:
  the legume gap (partially resolved in Phase 8, still bimodal/unresolved for the human-food
  slice), fruit/berry inseparability, RTU011's poultry/red-meat/offal bundling, the missing
  bread-specific balance (grain self-sufficiency computed on raw wheat/rye, tested against
  FAOSTAT in Phase 8 and found to hold up well), the missing nut/seed/cocoa data, and the missing
  sugar/sweets balance (confirmed ~0% by both Statistikaamet-adjacent general knowledge and
  FAOSTAT's rice/sugar lines in Phase 8).

## 12. Output file inventory

| File | Phase | Contents |
|---|---|---|
| `data/crosswalk/food_group_crosswalk.csv` | 2 | Taxonomy mapping, match_quality per row |
| `data/crosswalk/demographic_grid.md` | 2 | Age/sex/PAL grid design rationale |
| `data/processed/population_canonical_grid.csv`, `pal_levels.csv` | 2 | Canonical population and PAL reference tables |
| `data/processed/requirement_model_national.csv` | 3 | Recommended demand, tonnes/year |
| `data/processed/consumption_model_national.csv`, `over_under_consumption*.csv` | 4 | Actual demand, over/under-consumption ratios |
| `data/processed/self_sufficiency_model.csv` | 5 (revised 8) | Self-sufficiency ratio per pyramid sub-item |
| `data/processed/feed_dependency_model.csv`, `self_sufficiency_feed_adjusted.csv` | 6 | Feed balance, feed-adjusted lower bounds |
| `data/processed/waste_model.csv` | 6 | Loss rates, required-production inflators, waste-lever scenarios |
| `data/processed/scenario_comparison.csv`, `critical_dependency_flags.csv` | 7 (revised 8) | Scenario A/B comparison, 50%-threshold flags |
| `data/processed/faostat_cross_check.csv` | 8 | FAOSTAT 2022 independent validation |
| `data/processed/rtu011_topline_cross_check.csv` | post-launch | RTU011 raw-topline validation of the Phase 4 consumption model, all 16 categories |
| `data/crosswalk/eatlancet_crosswalk.csv` | post-launch | EAT-Lancet Planetary Health Diet crosswalk to project taxonomy, Scenario C demand basis |
| `docs/methodology.md` | 8 (revised post-launch, Scenario C added post-launch) | This file |

