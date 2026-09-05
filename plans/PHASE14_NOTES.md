# Phase 14 notes — Scenario C.2, the 2025 EAT-Lancet revision

> **Superseded in part by Phase 21.** The 2025 sugar value below was misread: **30 g/day** is the
> added/free-sugar target; 6 g/day is palm/coconut oil. C2 now uses energy-based TAI
> edible-equivalent mass, includes the known 50 g nuts value, and excludes Honey as a duplicate of
> aggregate sweets. The corrected C2 total is 1,666.9 g/person/day and the weighted headline is
> 129.4%. Historical 6 g/Honey figures below are retained only as a record of the superseded build.

Post-launch addition, prompted by the user asking "what is EAT-Lancet diet?" after Scenario C came
up in conversation, then explicitly asking to "build a Scenario C.2 using the 2025 targets" once
research turned up that the EAT-Lancet Commission published a revised Planetary Health Diet in
2025 with materially different food-group targets, not just updated framing. Status: done, full
scenario built end-to-end (new demand crosswalk, scenario_comparison.csv + critical_dependency_
flags.csv columns, dashboard chart/table/delta-view integration, methodology write-up).

## 1. What's actually different in the 2025 diet

Read from the EAT-Lancet Commission's 2025 Summary Report (Figure 01), against a lower reference
calorie level (2,500 -> ~2,400 kcal/day):

| Food group | 2019 (g/day) | 2025 (g/day) | Change |
|---|---|---|---|
| Whole grains | 232 | 210 | down |
| Vegetables | 300 | 300 | unchanged |
| Fruits | 200 | 200 | unchanged |
| Legumes | 75 | 75 | unchanged |
| Nuts | 50 | 50 | unchanged |
| Dairy | 250 | 250 | unchanged |
| Starchy tubers | 50 | 50 | unchanged |
| Eggs | 13 | 15 | up |
| Fish | 28 | 30 | up |
| Poultry | 29 | 30 | up |
| Red meat | 14 | 15 | up |
| Added/free sugar | 31 | 6 | down sharply |
| Oils/fats (combined) | 51.8 | 51 | ~unchanged |

Sourcing caveat carried over from Scenario C's own numbers: read from the Commission's public
summary PDF via two independent fetches that agreed with each other, not independently
cross-checked against the full peer-reviewed Lancet paper (paywalled). If this project's Scenario
C.2 figures are ever cited externally, re-verify against the primary journal article first.

## 2. Build

Mirrors Scenario C's construction exactly (`src/scenario_c_eatlancet.py` -> now paired with
`src/scenario_c2_eatlancet2025.py`), including the same documented assumptions: the bread:porridge
split reuses this project's own RTU011-derived ratio (EAT-Lancet still doesn't distinguish them
even in 2025); the combined oils/fats/spreads demand basis sums unsaturated oils + palm/coconut
oil + lard/tallow/butter the same way; the Nuts+Seeds,cocoa row is left blank rather than
understated, since 2025 still gives no separate seeds/cocoa figure.

Pipeline (run in order):
1. `src/scenario_c2_eatlancet2025.py` -> writes `data/crosswalk/eatlancet2025_crosswalk.csv`.
2. `src/update_scenario_c2.py` -> adds `scenario_C2_demand_tonnes_per_year`,
   `demand_change_ratio_C2_over_A`, `scenario_C2_self_sufficiency_pct` to
   `scenario_comparison.csv`. Made idempotent (drops and reinserts its own columns) so it's safe
   to re-run after later data changes.
3. `src/patch_scenario_c2_special_cases.py` -> fixes the two rows the generic branch logic in
   step 2 can't handle: Nuts+Seeds,cocoa (confirmed structural 0%, same as every other scenario)
   and Honey (no EAT-Lancet gram target exists for honey specifically, so its demand is
   extrapolated using the Sweets (total) category's own demand-change ratio, the same convention
   Phase 12 established for Scenario B/C).
4. `src/update_flags_c2.py` -> adds `scenario_C2_self_sufficiency_pct`,
   `flag_below_50pct_scenario_C2`, `flag_scenario_C2_worsens_dependency` to
   `critical_dependency_flags.csv`. Also made idempotent.
5. `python3 src/export_dashboard_data.py && python3 build_dashboard.py`.

Verified the full chain is reproducible: re-running steps 2-5 from the already-correct file state
reproduces identical output (same headline figures, same per-row values, no duplicate columns).

## 3. Dashboard changes

- Scorecard (section 01): new "Scenario C.2 — EAT-Lancet 2025 diet" tile.
- Self-sufficiency chart (section 02): fourth scenario-toggle button; chart, tooltip, and table
  all extended to read/display `scenario_C2_pct` / `scenario_C2_pct_display`.
- Diet-shift delta chart (section 05): third comparison-toggle button ("Scenario C.2 vs. A").
- Section descriptions (02, 03, 05) updated to mention both EAT-Lancet editions rather than one.
- Verified via headless Playwright against a staged copy: all four scenario buttons and all three
  delta buttons render without JS errors, correct row counts (17 food groups, 14 delta rows), and
  the table view's new "Scenario C.2" column populates correctly.

## 4. Headline result and the Honey outlier

Scenario C.2's tonnage-weighted headline is 156.8%, almost identical to Scenario C's 157.0% —
coincidental rather than meaningful, since the two editions' biggest divergence (added sugar) sits
entirely outside this weighted average (the sweets/sugar row has no resolved self-sufficiency
percentage to weight, and Honey isn't tonnage-significant enough to move it). Within individual
resolved categories, animal-protein self-sufficiency figures move down slightly across the board
(red meat 441.5% -> 395.6%, fish 281.8% -> 252.5%, eggs 95.0% -> 79.0%, poultry 82.3% -> 76.4%)
because 2025's targets for all four are higher than 2019's, raising demand against fixed
production. Rapeseed oil remains a critical dependency either way (27.0% -> 26.3%).

The one figure that looks alarming out of context is Honey, which jumps to roughly **2,795%**
under Scenario C.2 (up from 562.8% under C). This is a real consequence of the model's own stated
assumption (Honey's demand scales proportionally with total sweets demand), not a data error or a
claim about honey production changing: the 2025 diet's added-sugar target is about five times
smaller than 2019's, shrinking the denominator, not growing the numerator. Flagged with matching
caveats in the CSV notes, the dashboard's scorecard tile note, scenario-hint text, and delta-hint
text, so anyone encountering this figure gets the explanation alongside it rather than a bare
number that reads as implausible.

One visual side effect worth flagging directly rather than silently fixing: the self-sufficiency
chart's horizontal axis scales to the largest value in the current scenario. Under Scenario C.2,
Honey's ~2,795% dominates that scale so heavily that every other bar compresses to a thin sliver —
a more severe version of a compression effect Scenario C already has (from its own outlier, Honey
at 562.8%), just roughly five times worse. This wasn't introduced by new code — the same axis-
scaling logic applies uniformly across all four scenarios — but it does mean Scenario C.2's chart
is harder to read at a glance than the others. Left as-is rather than adding scenario-specific
axis-capping logic unilaterally, since that's a chart-design decision affecting the whole project's
established rendering convention, not a Scenario-C.2-specific bug; worth a follow-up if it becomes
a recurring complaint.

## 5. Deliverables

- `src/scenario_c2_eatlancet2025.py`, `src/update_scenario_c2.py`,
  `src/patch_scenario_c2_special_cases.py`, `src/update_flags_c2.py` — new pipeline scripts.
- `data/crosswalk/eatlancet2025_crosswalk.csv` — new demand crosswalk.
- `data/processed/scenario_comparison.csv`, `critical_dependency_flags.csv` — new Scenario C.2
  columns; notes extended on Porridges, Nuts, Sweets (total), and Honey rows.
- `src/export_dashboard_data.py` — Scenario C.2 fields added to `food_groups` and `headline`.
- `src/dashboard/app.js`, `template.html` — fourth scenario-toggle button, third delta-toggle
  button, extended table column, updated section descriptions and hint text.
- `docs/methodology.md` — new Section 10.2.
- `output/dashboard_data.json`, `output/dashboard.html` — rebuilt and verified.
- This file.
