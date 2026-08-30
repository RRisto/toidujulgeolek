# Phase 10 notes — Scenario C: the EAT-Lancet Planetary Health Diet

Post-launch addition, requested by the user after the original nine-phase build closed out (see
PHASE9_NOTES.md). Implements PLAN.md Section 7 item 10: build a third demand scenario benchmarked
against the EAT-Lancet Planetary Health Diet, mirroring how Scenario B (TAI-recommended diet) was
built, with full dashboard integration. Status: done.

## 1. Why this scenario

Scenario B already tests domestic production against Estonia's own dietary guidance (TAI). During
an earlier Q&A pass, validating Scenario B's dairy demand figure against TAI's own consumption
data and food-pyramid poster raised a broader question: are TAI's recommended gram values
themselves plausible? A per-category plausibility check (added to `docs/methodology.md` Section
4.1) found TAI's recommended diet is ~89% more massive by weight than either actual Estonian
consumption or an independent international benchmark — with dairy alone driving more than half
that gap. EAT-Lancet's Planetary Health Diet is that independent benchmark: a well-known,
externally-sourced reference diet, not derived from this project's own data at any point, so
running it as its own scenario tests domestic production against a genuinely independent yardstick
rather than a second variation on the same national guidance.

## 2. Data model

`src/scenario_c_eatlancet.py` builds the crosswalk (`data/crosswalk/eatlancet_crosswalk.csv`):
EAT-Lancet's published reference gram/day values at 2,500 kcal, scaled to Estonia's actual
population-weighted energy need (2,234.4 kcal/day at moderate PAL, the same figure Section 4
already computed) — a single multiplicative factor of 0.894, applied as this project's own
methodological choice for consistency with how Scenario B already scales to Estonia's population,
not something EAT-Lancet's own documentation prescribes.

Mapping EAT-Lancet's food groups onto this project's finer pyramid taxonomy required three
documented assumptions, none of them new in kind: reusing this project's own already-derived
bread:porridge ratio to split EAT-Lancet's one combined "whole grains" figure (the same convention
Phase 4 used for the RTU011 poultry/red-meat split); summing three EAT-Lancet oil/fat lines onto
the single combined oils/fats/spreads demand basis Scenarios A and B already use; and leaving the
nuts+seeds+cocoa row as a genuine gap rather than reporting EAT-Lancet's nuts-only figure as if it
covered the whole combined category. Full detail in `docs/methodology.md` Section 10.1.

`src/update_scenario_c.py` and `src/update_flags_c.py` then compute Scenario C self-sufficiency
using the identical re-scaling formula already established for Scenario B —
`scenario_C_self_sufficiency_pct = scenario_A_self_sufficiency_pct × (scenario_A_demand_tonnes /
scenario_C_demand_tonnes)`, production held fixed — and append it to `scenario_comparison.csv` and
`critical_dependency_flags.csv` in place, alongside the same threshold/worsens flags Scenario B
already carries.

**Headline finding**: Scenario C's tonnage-weighted aggregate self-sufficiency is 156.4% — above
both Scenario A (106.8%) and Scenario B (64.8%) — mechanically driven by EAT-Lancet recommending
markedly less dairy and red meat than Estonia actually eats (dairy 166.0%→220.2%, red meat
78.1%→441.5%). The reverse happens for oils/fats: EAT-Lancet's higher recommended fat intake pushes
rapeseed oil's self-sufficiency from 69.3% (Scenario A) down to 27.0% — newly crossing the 50%
critical-dependency threshold, a dependency that doesn't exist under Scenario A or B at all. This is
the one genuinely new critical dependency Scenario C surfaces; every other flagged item under
Scenario C was already flagged under Scenario A.

## 3. Dashboard integration

Reworked `src/dashboard/template.html` and `src/dashboard/app.js` (worked from local copies of the
same two source files) to a three-way A/B/C toggle:

- **Scorecard**: added a fifth tile for Scenario C's weighted headline figure.
- **Self-sufficiency by food group**: the existing Scenario A/B toggle gained a third "Scenario C —
  EAT-Lancet diet" button; the scenario-key lookup was refactored from a ternary to a small map
  (`SCEN_KEYS`) so the chart, tooltip, and table-view twin all support three states without
  duplicated logic. The table view gained a Scenario C column.
- **Scenario delta chart (section 05)**: this previously showed only the A→B delta. Rather than
  cram a third series onto one diverging bar chart, it gained its own toggle ("Scenario B vs. A" /
  "Scenario C vs. A") so each comparison stays legible on its own — the same interaction pattern as
  the scenario toggle in section 02, refactored the same way (`currentDelta` state, a `DELTA_LABEL`
  map, tooltip and hint text keyed off the selection).
- **Critical dependencies (section 03)** was deliberately left unchanged in scope: it reports
  today's actual dependencies (Scenario A) plus robustness flags, not hypothetical diet-shift
  ones — that framing already excluded some Scenario-B-only crossings (e.g. potato, eggs) before
  this phase, so extending it piecemeal to Scenario C alone would have been an inconsistent, not a
  complete, fix. Its section description was updated with one clarifying sentence pointing to
  section 05, where the new rapeseed-oil finding is fully visible instead (as the largest bar on
  the chart when "Scenario C vs. A" is selected, plus a data-status note in the table).
- `src/export_dashboard_data.py` was extended to read the three new `scenario_C_*` columns,
  compute a Scenario C tonnage-weighted headline (via the existing generic `weighted_headline()`
  helper — no new aggregation logic needed), and add `scenario_C_pct`, `scenario_C_pct_display`,
  `demand_C_tonnes`, `demand_change_ratio_C`, and the two new Scenario C flags to every
  `food_groups` entry in `output/dashboard_data.json`.

## 4. Verification

Re-ran the same direct, wrapper-free Playwright approach used in Phase 9 (`test_render.py`,
extended with three new interaction steps: clicking the Scenario C button, clicking the delta
chart's "Scenario C vs. A" button, and screenshotting both) against the rebuilt
`output/dashboard.html`. Checked: console/page errors (none new — the same expected Google Fonts
`ERR_TUNNEL_CONNECTION_FAILED` from Phase 9, unrelated to this change), all three scenario states
of the self-sufficiency chart, both delta-chart comparisons, the table view with its new Scenario C
column, and dark mode. No new rendering bugs found — the existing z-index, label-anchoring, and
`pill-wrap` fixes from Phase 9 held up unchanged under the added content.

## 5. Deliverables

- `data/crosswalk/eatlancet_crosswalk.csv` — EAT-Lancet crosswalk and Scenario C demand basis.
- `src/scenario_c_eatlancet.py`, `src/update_scenario_c.py`, `src/update_flags_c.py` — build
  scripts (Scenario C demand model, self-sufficiency computation, flag computation).
- `data/processed/scenario_comparison.csv`, `critical_dependency_flags.csv` — updated in place
  with Scenario C columns.
- `docs/methodology.md` Section 10.1 — full write-up of the scaling methodology, crosswalk
  assumptions, and headline findings; Section 11 gained one new assumptions bullet; Section 12's
  output-file inventory gained the new crosswalk file.
- `src/export_dashboard_data.py`, `output/dashboard_data.json` — extended data export.
- `src/dashboard/template.html`, `src/dashboard/app.js`, `output/dashboard.html` — three-way
  scenario toggle across the scorecard, self-sufficiency chart/table, and a new delta-chart toggle.
- Republished as the same Claude Artifact (private, shareable from its own page).
