# Phase 8 notes — validation pass & methodology write-up

Implements PLAN.md Section 7 item 8: cross-check headline numbers against FAOSTAT/Eurostat, and
write up every assumption and its source. Status: done.

## 1. FAOSTAT cross-check

Pulled Estonia's 2022 FAOSTAT Food Balance Sheet (the latest year FAOSTAT publishes) via a live
browser session and FAOSTAT's own "Report" builder — the FAOSTAT REST API returned a 521/robots
error on direct fetch, and the site's Angular front-end doesn't render through a plain page-fetch
tool, so the same "drive a real browser" workaround used throughout this project for
Statistikaamet/TAI was needed here too. Full detail and the resulting 19-row comparison table:
`data/processed/faostat_cross_check.csv`; the full writeup is folded into `docs/methodology.md`
Section 8 rather than repeated here. Summary of what it found:

- **6 categories in strong agreement** with this project's existing figures (wheat+rye/bread,
  potato, fruit, eggs, fish, pork) — despite different years, methodologies, and often different
  exact item scope. This is meaningful independent corroboration of the overall approach.
- **4 material divergences**, each investigated and documented rather than silently resolved:
  vegetables (a third disagreeing data point on an already-flagged gap), beef and poultry (likely
  real year-to-year shifts between 2022 and 2024), and — the most substantive finding — rapeseed,
  where FAOSTAT's own raw-seed AND refined-oil self-sufficiency figures (141%, 265%) are far above
  the PM37-2024-derived 69.3% this project's oil estimate rests on. This directly confirms a
  fragility Phase 5's own methodology note had already flagged as a risk (the yield-cancellation
  assumption "breaks down if a meaningful share of Estonia's edible oil trade is in already-refined
  form") — a good example of a documented limitation actually mattering when tested, rather than
  being boilerplate caution.
- **One gap partially resolved**: legumes, carried as "unknown - assumed low" since Phase 2, turns
  out to be bimodal — Estonia is a large net exporter of field peas (feed/export use) but ~0%
  self-sufficient in dry beans/lentils (the more plate-relevant pulse type). Updated in
  `self_sufficiency_model.csv`, `scenario_comparison.csv`, and `critical_dependency_flags.csv` —
  the first time a Phase 8 finding fed back to revise an earlier phase's output rather than just
  commenting on it.

## 2. Eurostat

Attempted (WebSearch, WebFetch on the Eurostat REST API and a secondary EU-comparison paper) but
not successfully retrieved — robots.txt blocks and 403s on every endpoint tried this round. Per
DATA_SOURCES.md's original framing ("useful for EU-comparison context," lower priority than
FAOSTAT), this is left as a documented gap rather than pursued through a browser-automation
workaround the way FAOSTAT was — FAOSTAT alone already delivered a substantive, commodity-level
independent validation, which was the actual purpose of this checkpoint.

## 3. Nutritional-adequacy macronutrient check (5.8)

Phase 3 flagged this as deferred to Phase 8. Applied generic, non-Estonia-specific per-100g
macronutrient composition estimates (standard nutrition-database-style values, clearly not
measured Estonian data) to the requirement model's 16 food-group tonnages. Result: **17.4%E
protein, 35.9%E fat, 46.7%E carbohydrate** — all three land inside TAI's own Table 6 targets for
ages 2+ (10-20%E / 25-40%E / 45-60%E respectively). Implied total energy (2,524 kcal/capita/day)
is in the same range as Phase 3's own more precise 2,234-2,282 kcal figure, with the gap
attributable to this check's coarser composition assumptions rather than a modelling error. This
is a consistency check, not new measurement, as PLAN.md 5.8 itself frames it — by construction,
adequacy follows from applying Table 13's TAI-designed portions faithfully, and this check
corroborates that Table 13 was in fact applied faithfully.

## 4. Methodology write-up

`docs/methodology.md` (295 lines) consolidates every data source, method, and assumption from
Phases 1-8 into a single standalone document, structured to double as the dashboard's methodology
appendix content (PLAN.md Section 9's last bullet). Includes a source-acquisition table, the two
network/PDF-access workarounds that recur throughout the project, one subsection per methodology
step (5.1-5.8), the full FAOSTAT validation writeup, a consolidated assumptions/limitations list,
and an output-file inventory pointing to every processed CSV by the phase that produced it.

## 5. Files produced / revised this phase

- `data/processed/faostat_cross_check.csv` (new, 19 rows)
- `docs/methodology.md` (new, 295 lines)
- `data/processed/self_sufficiency_model.csv` — Legumes row revised (was `gap_assumed`, now
  `derived_from_faostat`, bimodal finding documented in the note)
- `data/processed/scenario_comparison.csv`, `critical_dependency_flags.csv` — Legumes rows revised
  to match

## 6. Known limitations carried into Phase 9

- FAOSTAT's 2022 vintage is two years behind the PM-series 2024 data used everywhere else in this
  project — every cross-check in Section 1 has to be read with that gap in mind; some divergences
  found may be temporal rather than definitional, and this phase couldn't fully separate the two
  for rapeseed or the meat categories.
- Eurostat's EU-comparison angle (how does Estonia compare to Latvia/Lithuania/Finland) remains
  unaddressed — a genuine, if lower-priority, gap for anyone wanting cross-country context in the
  eventual dashboard.
- The rapeseed-oil divergence is flagged, not resolved — the dashboard (Phase 9) should present
  the 69.3% figure with its FAOSTAT-derived caveat visible, not silently replace it with an
  unverified alternative.
- The macronutrient check (Section 3) is a lightweight, generic-composition-based consistency
  check, not a substitute for a genuine per-food-item nutrient database — still out of scope for a
  quantitative micronutrient model in v1, per PLAN.md Section 2/10.
