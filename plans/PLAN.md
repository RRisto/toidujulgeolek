# Estonia food self-sufficiency (toidujulgeolek) — analysis & simulation plan

## 1. Research question

Could Estonia feed its population a nutritionally adequate diet from domestic production, and where are the critical dependencies? Broken down by food group, and answered under two conditions: (a) today's actual consumption patterns, and (b) if the population instead ate what Tervise Arengu Instituut (TAI) recommends — with over/under-consumption relative to TAI's guidance quantified either way.

The simulation should be realistic rather than a single national average: it accounts for the population's actual age/sex/physical-activity structure (different groups need different amounts), for food lost to waste along the supply chain, and for the fact that a chunk of domestic production (grain, some fish) doesn't feed people directly — it feeds livestock, so animal products are only as "domestic" as the feed behind them.

Final deliverable: an interactive HTML page presenting the results (see Section 9).

## 2. Scope for this version (v1)

Decisions made before starting:

- **Self-sufficiency is measured against current actual domestic production**, not a theoretical maximum. The question answered is "how self-sufficient are we today, at today's output," not "how self-sufficient could we become if we reorganised land and livestock use." A production-capacity-ceiling model (arable land, yield potential, livestock capacity headroom) is a natural v2 extension and is scoped out here — see Section 10.
- Demographic realism is in scope: population is modelled by age × sex × physical activity level, not as a single national average.
- Waste and feed-use are in scope, as described in Sections 5.5 and 5.4.
- This is a national aggregate model. It does not model seasonality, regional distribution, or supply-chain resilience under shock (that's closer to what the "Toidujulgeoleku aastaraamat" already covers qualitatively) — it answers the steady-state annual mass-balance question.

## 3. Food-group taxonomy

Two levels are needed, and the project needs an explicit crosswalk between them (built in Phase 2):

**Nutritional/recommendation level** — TAI's own toidupüramiid groups, since that's the frame the recommendations and (likely) the RTU consumption survey are expressed in:
1. Fish, eggs, meat
2. Dairy products
3. Nuts, seeds, oils, added fats
4. Vegetables, fruits, berries
5. Grain products, potatoes
6. Sweets, snacks, discretionary (not "recommended" as such — a ceiling, not a target)

**Production/self-sufficiency level** — finer than the above, because self-sufficiency varies enormously *within* each TAI group and averaging would hide the real dependencies. Confirmed from the strategy-document figures (Section 5 of DATA_SOURCES.md): fish 300% vs. poultry 57% vs. eggs 54% (all inside "fish, eggs, meat"); grain 199% vs. potatoes 70% (inside "grains, potatoes"); vegetables 46% vs. fresh fruit/berries 8% (inside "vegetables, fruits, berries"). So the production-side model should track at least: grain, potatoes, vegetables, fruit/berries, dairy, beef, pork, poultry, lamb/goat, eggs, fish, added fats/oils, sugar.

The crosswalk table (which production-level items sum to which TAI group, with what weight/share) is a Phase 2 deliverable, not assumed here.

## 4. Data sources

Full catalogue with URLs, what each gives us, and freshness caveats is in `DATA_SOURCES.md` in this folder. Summary of what feeds which part of the model:

- Population by age/sex → Statistikaamet RV021
- Recommended intake by age/sex/activity/food-group → TAI Tabelraamat (2025) + toidupüramiid
- Actual consumption by food-group and demographic → TAI RTU 2014 (flagged as stale — see limitations)
- Domestic production volumes → Statistikaamet livestock & crop production tables
- Imports/exports, feed-grain use → Statistikaamet foreign trade tables (exact table TBD in Phase 1) + industry reports
- Self-sufficiency ratios (pre-computed, official) → "Toidu varustuskindluse strateegia 2023+" — used as calibration anchor for the bottom-up model
- Food waste by supply-chain stage → SEI 2021 study
- Cross-check → FAOSTAT Food Balance Sheets, Eurostat

## 5. Methodology

### 5.1 Demographic nutritional-requirement model
Build a grid of age × sex × physical-activity-level cells matching whatever bins the TAI Tabelraamat actually uses (don't invent our own bins — read them off the source). Weight each cell by Statistikaamet's population count for that age/sex band. Physical-activity-level distribution within each age/sex band isn't directly counted by Statistikaamet, so it needs an assumption — informed by the RTU/TKU survey's physical-activity data (Section 3 in DATA_SOURCES.md) or, failing that, a documented default split (e.g. WHO/EFSA typical PAL distribution for a Northern European population), clearly labelled as an assumption. Multiply out to a national aggregate *recommended* demand per food group (tonnes/year) — this is the "if everyone ate exactly as recommended, weighted by who Estonia's population actually is" baseline.

### 5.2 Actual-consumption model & over/under-consumption
Same demographic grid, but weighted by RTU 2014's actual per-capita consumption by food group and demographic cell (to the extent the survey supports that granularity — some cells may need pooling). Produces a national aggregate *actual* demand per food group. Comparing 5.1 vs 5.2 directly answers "how much do we over/under-consume, by food group, per TAI's own standard" — and can be shown per demographic segment, not just nationally, since over-consumption of meat/sugar and under-consumption of vegetables/fish are unlikely to be evenly distributed across age groups.

### 5.3 Domestic supply / self-sufficiency model
For each production-level food item, build (or approximate, where full data isn't available) a FAO-style balance:
`Domestic supply for food = Production + Imports − Exports − Feed use − Seed use − Industrial/non-food use − Waste ± Stock change`
Self-sufficiency ratio = Production / Domestic utilization. Calibrate against the ready-made official figures in the 2023+ strategy document (Section 6 of DATA_SOURCES.md) — where a full bottom-up balance can't be built from Statistikaamet tables alone in Phase 1, use the official ratio directly and flag it as "sourced" rather than "derived."

### 5.4 Feed dependency adjustment
Animal products (meat, dairy, eggs, farmed fish) are only as domestic as their feed. Estonia is grain-surplus (199% self-sufficient) but imports essentially all protein feed (soybean meal). Using standard feed-conversion-ratio assumptions per species (published zootechnical values, not Estonia-specific — labelled as such) plus whatever feed-import volume can be sourced (Section 5 of DATA_SOURCES.md flags this as the thinnest data area), compute a *feed-adjusted* self-sufficiency figure alongside the headline one: e.g., pork production is 78% self-sufficient by output, but if a meaningful share of the feed behind it is imported protein, the resource-based dependency is higher than the headline number suggests. Present this as a labelled sensitivity/range, not a single precise number — the input data doesn't support more than that.

### 5.5 Food waste treatment
Two distinct uses of the SEI 2021 waste data:
- **Supply side**: some share of what's produced/imported never reaches a plate (production/retail/industry losses) — this means the *required* production to cover a given consumption level is higher than consumption itself, by roughly the loss rate at each stage before the household.
- **Demand side / lever**: household waste (48% of total, the largest single share) is waste of food that *did* reach the plate and wasn't eaten — this is a pure efficiency lever: cutting household waste doesn't require any more domestic production, it just means less is needed for the same nutritional outcome. Worth showing as its own scenario input (see 5.6) because it's a lever available regardless of what happens to diet composition.
Where the SEI study doesn't give food-group-level detail at a given stage, fall back to generic per-category loss-rate literature (FAO/WRAP), clearly labelled as an assumption layered on top of the Estonia-specific stage totals.

### 5.6 Scenario engine
Two core scenarios for v1, both run through the same demographic and supply machinery:
- **A — Status quo**: actual current consumption (5.2) against actual current production (5.3) → today's self-sufficiency picture, critical dependencies as they stand.
- **B — TAI-recommended diet**: recommended consumption (5.1) against *the same, unchanged* current production (5.3) → shows what self-sufficiency would look like if the population shifted to TAI's guidance with no change in what's grown. This is worth stating plainly in the output: it is **not guaranteed to improve toidujulgeolek uniformly**. Where we currently over-consume a category with strong self-sufficiency (e.g. meat, grain-based products, added sugar), moving to recommended levels eases import dependency. But TAI recommends *more* vegetables, fruit and fish than currently eaten — precisely the categories with the weakest self-sufficiency (46%, 8%, and feed-dependent respectively). So Scenario B may show *increased* pressure on the already-weakest categories even as it reduces pressure elsewhere. That tension is a headline finding worth surfacing, not a modelling error to smooth over.
An optional toggle for the household-waste-reduction lever (5.5) can be layered on top of either scenario (waste reduction doesn't require dietary change).

### 5.7 Critical-dependency flagging
Define a simple, transparent rule rather than a black-box score — e.g. flag any food group where self-sufficiency (or feed-adjusted self-sufficiency, where computed) falls below a threshold (e.g. 50%) under Scenario A, and separately note any group where Scenario B *increases* the gap. Fresh fruit/berries (8%) and vegetables (46%) are near-certain to be flagged from the sourced figures alone; poultry, eggs and pork sit in a middle band worth showing explicitly given the feed-import question in 5.4.

### 5.8 Nutritional adequacy sanity check
Beyond food-group mass balance, do a lightweight check that the recommended-diet aggregate (5.1) is calorically and macronutrient-adequate (it should be, by construction, since it's built from TAI's own reference values — this is mainly a consistency check on the modelling, not new analysis). A full micronutrient model (iron, iodine, omega-3, vitamin C etc.) is out of scope for v1's quantitative model, but the write-up should flag qualitatively that Estonia's structurally weak categories (fresh produce, fish) are also disproportionately important for vitamin C, folate, and omega-3/iodine — i.e., the self-sufficiency gap and the nutritional-adequacy risk point at the same food groups, which strengthens the "critical dependency" framing.

## 6. Architecture & tooling

- **Python (pandas)** for the calculation engine — this is a tabular ETL-and-arithmetic problem, not something that needs anything heavier.
- Suggested folder layout inside this project:
  - `data/raw/` — sourced files as downloaded (PxWeb exports, PDFs, CSVs), unmodified
  - `data/processed/` — cleaned, tidy CSVs per source
  - `data/crosswalk/` — the taxonomy mapping table from Section 3, and demographic-bin definitions from the TAI Tabelraamat
  - `src/` — ETL scripts (one per data source) + the model itself (requirement, consumption, supply, scenario, dependency-flagging modules) + a script that exports final results to JSON for the dashboard
  - `output/` — computed result tables (CSV, for inspection) and the JSON the HTML page consumes
  - `docs/` — methodology write-up, this plan, data source catalogue
- **Dashboard**: a single self-contained HTML file (inline CSS/JS, no build step) that reads the exported JSON and renders the views in Section 9. Keeping the model (Python) and the presentation (HTML/JS reading static JSON) separate means the dashboard can be regenerated any time the underlying data or assumptions are updated, without touching the page code.

## 7. Phased build plan

1. **Data acquisition** — pull every source in `DATA_SOURCES.md` into `data/raw/`; resolve the open items in its Section 9 (confirm no newer RTU wave, locate the trade-table codes, confirm strategy-doc reference years). Checkpoint: every source either acquired or explicitly marked unavailable with a fallback noted.
   - **Status: done.** See `PHASE1_NOTES.md`. Every source in `DATA_SOURCES.md` acquired or explicitly flagged (network access required a browser-automation workaround, documented there); validated via three independent cross-checks.
2. **Taxonomy & demographic grid** — build the crosswalk table (Section 3) and the age/sex/activity bins read off the Tabelraamat. Checkpoint: a single reference table both the requirement model and the consumption model will key off.
   - **Status: done.** See `PHASE2_NOTES.md`. Crosswalk: `data/crosswalk/food_group_crosswalk.csv` (+ README). Demographic grid: `data/crosswalk/demographic_grid.md` (methodology) and `data/processed/population_canonical_grid.csv` + `data/processed/pal_levels.csv` (the reference tables).
3. **Requirement model** (5.1) — population-weighted recommended demand per food group. Checkpoint: totals sanity-check against national average calorie/macronutrient figures.
   - **Status: done.** See `PHASE3_NOTES.md`. National recommended demand by food group: `data/processed/requirement_model_national.csv`. Calorie sanity check (two independent derivations within ~2%): `data/processed/SANITY_CHECK_phase3.md`.
4. **Consumption model** (5.2) — population-weighted actual demand per food group; over/under-consumption vs. requirement, nationally and by demographic segment.
   - **Status: done.** See `PHASE4_NOTES.md`. National actual demand: `data/processed/consumption_model_national.csv`. Over/under-consumption: `data/processed/over_under_consumption.csv` (national) and `over_under_consumption_by_segment.csv` (by age/sex). Headline: red meat 3.5x and sweets 3.1x over TAI's recommendation nationally; vegetables (0.28x), nuts/seeds (0.09x) and fish (0.30x) most under-consumed; children over-consume sweets far more sharply (5.7-9.2x) than adults.
5. **Supply/self-sufficiency model** (5.3) — bottom-up balance where possible, calibrated against the official strategy-document ratios. Checkpoint: computed ratios land close to the sourced official ones (Section 6 of DATA_SOURCES.md); document and explain any that don't.
   - **Status: done.** See `PHASE5_NOTES.md`. Self-sufficiency by pyramid sub-item: `data/processed/self_sufficiency_model.csv`. Most categories matched the official figures closely (eggs, poultry, fruit+berries); vegetables and dairy diverged enough that the official figure was used as headline, with the derived figure kept for transparency. Two genuine gaps reported as ranges/unknowns rather than fabricated: porridge/pasta/rice (0%-178%+, no consumption-mix data) and legumes/nuts/seeds/sweets (no production data found).
6. **Feed adjustment** (5.4) and **waste treatment** (5.5) — layered onto the supply model, presented as labelled sensitivities.
   - **Status: done.** See `PHASE6_NOTES.md`. Waste model: `data/processed/waste_model.csv` (per-pyramid-group loss rates and required-production inflators, built from SEI 2021 category-level detail plus a household+retail-proportions proxy for undocumented stages). Feed model: `data/processed/feed_dependency_model.csv` (FCR-based aggregate feed balance for animal products) and `data/processed/self_sufficiency_feed_adjusted.csv` (headline self-sufficiency re-stated as a lower bound once feed import-dependency is netted out). Headline findings: vegetables have the highest loss rate (75.5%, consistent with the RTU-vs-production mismatch flagged in Phase 1); domestic feed supply covers an estimated ~82% of aggregate livestock feed demand, with the shortfall concentrated in protein concentrates rather than forage — flagged qualitatively since no Estonian feed-ration composition data exists; feed-adjusted bounds (poultry 57.7%→40.4%, eggs 53.6%→37.5%, pork 72.0%→50.4%) are illustrative sensitivities, not measurements.
7. **Scenario engine & dependency flagging** (5.6, 5.7) — Scenario A and B computed side by side; threshold-based flags generated.
   - **Status: done.** See `PHASE7_NOTES.md`. Scenario comparison: `data/processed/scenario_comparison.csv` (Scenario A status-quo vs. Scenario B TAI-recommended demand, self-sufficiency under both, household-waste-lever effect). Critical-dependency flags: `data/processed/critical_dependency_flags.csv` (50% threshold, checked under Scenario A, Scenario B, and the Phase 6 feed-adjusted bound, plus a separate flag for items Scenario B makes worse). Headline finding: Scenario B worsens self-sufficiency in 9 of 12 numerically-comparable categories -- vegetables swings from 46% to ~13%, dairy from 166% to ~100% (corrected post-launch from an original ~61% -- see item 11 below and methodology.md Section 4.2), fish from a caveated 300% to ~89% -- because TAI recommends eating more of exactly the categories Estonia is worst at supplying domestically; red meat is the one major exception, improving from 78.1% to ~274% since it's currently over-consumed. All 12 comparable demand-change ratios independently cross-check against Phase 4's over/under-consumption figures to within rounding.
8. **Validation pass** — cross-check headline numbers against FAOSTAT/Eurostat; write up every assumption and its source in `docs/methodology.md`.
   - **Status: done.** See `PHASE8_NOTES.md`. FAOSTAT cross-check: `data/processed/faostat_cross_check.csv` (19 rows, Estonia 2022, pulled via a live browser session since FAOSTAT's API and Angular front-end both resisted direct fetch). Full write-up: `docs/methodology.md` (consolidates every data source, method, and assumption from Phases 1-8 in one document). Headline: 6 categories in strong agreement with existing figures (wheat/rye, potato, fruit, eggs, fish, pork); 4 material divergences investigated and documented rather than resolved (vegetables, beef, poultry, and -- most substantively -- rapeseed, where FAOSTAT confirms a fragility Phase 5 had already flagged: the yield-cancellation oil proxy likely understates true self-sufficiency); legumes' long-standing 'unknown - assumed low' gap was revised to a bimodal finding (large pea surplus for feed/export, ~0% for human-food pulses) and fed back into `self_sufficiency_model.csv`, `scenario_comparison.csv` and `critical_dependency_flags.csv`. A lightweight macronutrient check (5.8, using generic composition data) confirms the requirement model's aggregate %E split falls within TAI's own Table 6 targets on all three macros.
9. **Dashboard build** — export JSON, build the HTML page per Section 9, wire it to the exported data.
   - **Status: done.** See `PHASE9_NOTES.md`. Data export: `output/dashboard_data.json` (built by `src/export_dashboard_data.py`, including a new tonnage-weighted aggregate self-sufficiency figure with an explicit coverage-of-tonnage transparency metric). Dashboard source: `src/dashboard/` (template.html, app.js, methodology_body.html) + `build_dashboard.py` at project root, which assembles them with the JSON export into the single self-contained `output/dashboard.html`. Seven sections: headline scorecard, self-sufficiency by food group (Scenario A/B toggle), critical dependencies, actual-vs-recommended consumption (national + 6 demographic segments), the Scenario B delta chart, food waste by stage and group with a waste-reduction lever table, and the full methodology appendix with the Phase 8 FAOSTAT cross-check embedded. Verified by direct, wrapper-free Playwright rendering of the built HTML (all 7 sections, both scenarios, the table-view toggle, the demographic filter, the methodology expand, and dark mode) rather than through the claude.ai artifact viewer, whose cross-origin iframe blocked scroll-based verification. That pass caught and fixed three real rendering bugs: a feed-adjusted-bound marker line painting on top of percentage labels (z-index ordering), long bars in the Scenario B delta chart pushing their value labels into the row-label column (label now anchors to the bar itself, matching the working pattern already used in the self-sufficiency chart), and long "no single figure" data-gap notes overflowing the viewport instead of wrapping (pill component was `white-space: nowrap` by design for short badges; added a `.pill-wrap` modifier for these). This closes the nine-phase build.

10. **Scenario C: EAT-Lancet Planetary Health Diet (post-launch)** — a third demand scenario, requested by the user after the nine-phase build closed out, benchmarking domestic production against an international reference diet (EAT-Lancet's Planetary Health Diet) rather than a national dietary guideline. Full scope: crosswalk + demand model, self-sufficiency computation, and full dashboard integration (three-way A/B/C toggle), per the user's explicit choice among data-only / data+methodology / data+methodology+dashboard options.
   - **Status: done.** See `PHASE10_NOTES.md` and `docs/methodology.md` Section 10.1. Crosswalk: `data/crosswalk/eatlancet_crosswalk.csv` (EAT-Lancet's published 2,500 kcal/day reference gram values, population-energy-scaled to Estonia at 0.894x and mapped to this project's own pyramid taxonomy). Scenario CSVs updated in place: `scenario_comparison.csv` (+`scenario_C_demand_tonnes_per_year`, `demand_change_ratio_C_over_A`, `scenario_C_self_sufficiency_pct`) and `critical_dependency_flags.csv` (+`scenario_C_self_sufficiency_pct`, `flag_below_50pct_scenario_C`, `flag_scenario_C_worsens_dependency`), using the identical Scenario B re-scaling formula. Dashboard reworked to a three-way A/B/C toggle across the scorecard, the self-sufficiency chart/table, and a new B-vs-A / C-vs-A delta-chart toggle; re-verified with the same direct Playwright rendering approach as Phase 9 (all three scenario states, both delta views, table view, dark mode -- no new rendering bugs found). Headline: Scenario C's tonnage-weighted self-sufficiency is 156.4% (vs. 106.8% Scenario A, 76.7% Scenario B post-correction -- see item 11 below), driven mainly by EAT-Lancet recommending markedly less dairy and red meat than Estonia actually eats. The one genuinely new finding: rapeseed oil's self-sufficiency falls from 69.3% (Scenario A) to 27.0% under Scenario C, newly crossing the 50% critical-dependency threshold -- a dependency invisible under Scenario A or B, driven by EAT-Lancet's higher recommended fat intake.

11. **Post-launch correction: dairy portion-to-gram conversion** — prompted by the user quoting TAI Tabelraamat Table 16.3's full text directly and asking how the requirement model's dairy gram figure was derived. The original build (Phase 3, Task 18) used only Table 16.3's first-listed dairy line (unsweetened milk, 300g/portion) as if it represented the entire dairy category, when the table actually lists six distinct dairy sub-types (milk, cottage cheese, yogurt, cheese, cream, flavored products) at very different portion masses (55-300g).
    - **Status: done.** See `docs/methodology.md` Section 4.2 for the full investigation and before/after figures. Fix: average across all six sub-types (182.5g/portion, down from 300g), matching the same undifferentiated-tiers convention already used for fish and poultry. Recomputed in place: `data/crosswalk/portion_gram_representative.csv`, `data/processed/requirement_model_national.csv` (dairy: 805.7 → 490.1 g/day), `scenario_comparison.csv` and `critical_dependency_flags.csv` (dairy Scenario B self-sufficiency: 61.1% → 100.4%; demand-change ratio 2.72x → 1.65x), the dashboard export and rendered dashboard (Scenario B tonnage-weighted headline: 64.8% → 76.7%), and `docs/methodology.md` Sections 4.1 and 11. The total-mass-vs-EAT-Lancet finding (Section 4.1) survives in direction but shrinks materially: the recommended diet is now ~64-67% heavier than actual consumption/EAT-Lancet (was ~89%), and dairy is no longer the largest single contributor to that gap (was >50% of it, now ~29%, third behind grains+potato and vegetables+fruit+berries). No other finding in the project changed direction -- Scenario A and Scenario C figures were untouched, since neither depends on the TAI portion-to-gram conversion.

## 8. Key assumptions, limitations & known uncertainties (to state up front in the output, not bury)

- Consumption baseline is a 2014 survey; treated as the best available, cross-checked where possible against fresher partial signals, flagged explicitly as dated.
- Self-sufficiency ratios lean on an official pre-computed table (5-year average, exact years to confirm) rather than a fully independent bottom-up build for every category; used as calibration, and any material divergence from a bottom-up estimate is investigated and explained rather than silently overridden.
- Feed-conversion and feed-import-share figures are generic/assumption-based, not Estonia-specific measured data — presented as a range, not a point estimate.
- No production-capacity-ceiling modelling in v1 (see Section 10) — "self-sufficiency" here means "at today's output," not "at Estonia's potential output."
- National aggregate only — no seasonality, regional, or shock-resilience modelling.
- Micronutrient adequacy is a qualitative flag, not a quantitative model, in v1.

## 9. Planned HTML dashboard sections (for later build)

- Headline scorecard: overall diet-weighted self-sufficiency under Scenario A vs. B, and the household-waste-reduction toggle.
- Per-food-group self-sufficiency bars (production-level granularity from Section 3), with the feed-adjusted range shown alongside the headline figure where computed.
- Consumption comparison: actual vs. TAI-recommended, per food group, with a demographic-segment filter (age band / sex / activity level).
- Scenario toggle: Status quo vs. TAI-recommended diet, showing how the self-sufficiency picture shifts per group — including the categories where it gets *worse*, not just better.
- Critical-dependency callouts: the flagged groups from 5.7, with a plain-language explanation of why each is flagged (low self-sufficiency, feed dependency, or nutritional importance).
- Waste module: supply-chain stage breakdown, with the household-lever toggle's effect shown separately from dietary change.
- Methodology & sources appendix: everything in Section 8 above, plus links back to the source data, so the page doesn't overstate its own precision.

## 10. Explicitly out of scope for v1 (candidate v2 extensions)

- Theoretical maximum production-capacity modelling (arable land reallocation, yield-gap closing, livestock headroom) — would turn "are we" into "could we, if we changed what we grow."
- Seasonal/monthly resolution (annual self-sufficiency can mask a category that's 100% self-sufficient in August and near-zero in March).
- Regional (maakond-level) breakdown of surplus/deficit.
- Supply-chain shock/resilience simulation (closer to what the Toidujulgeoleku aastaraamat already covers qualitatively).
- Full micronutrient-level nutritional modelling.
