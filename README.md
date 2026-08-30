# Toidujulgeolek — Estonia food self-sufficiency model

Could Estonia feed its population a nutritionally adequate diet from domestic production, and
where are the critical dependencies? Answered by food group, under Estonia's actual current
production, and compared against four different demand scenarios: today's actual consumption,
TAI's (Tervise Arengu Instituut) recommended diet, and two editions of the EAT-Lancet Planetary
Health Diet (2019 and a 2025 revision). The model accounts for the population's actual age/sex/
activity structure, food lost to waste, and the fact that a chunk of domestic production (grain,
some fish) feeds livestock rather than people directly.

The result is a single self-contained interactive dashboard: **[`output/dashboard.html`](output/dashboard.html)**.

## Quick orientation

- **Just want the results?** Open `output/dashboard.html` in a browser. Nothing else to run.
- **Want to understand a number?** Every figure on the dashboard links back to `docs/methodology.md`
  — start there, not in the phase notes, for what a number means and how confident to be in it.
- **Want the full source catalogue?** `DATA_SOURCES.md` — every dataset used, where it came from,
  and its freshness/access caveats.
- **Want the project history?** `plans/` — the original build plan and a phase-by-phase log of
  everything done since, including every post-launch correction driven by user feedback.

## Repository layout

```
data/
  raw/            source data as pulled (Statistikaamet, TAI, FAOSTAT, SEI, agri.ee), with
                  per-source README.md provenance notes
  crosswalk/      taxonomy crosswalks between data sources and the project's own food-group model
  processed/      derived model outputs (self-sufficiency figures, scenario comparisons,
                  critical-dependency flags, consumption models) — the dashboard's actual inputs

src/
  export_dashboard_data.py   reads data/processed/*.csv, writes output/dashboard_data.json
  scenario_c_eatlancet.py    Scenario C demand crosswalk (EAT-Lancet 2019)
  scenario_c2_eatlancet2025.py, update_scenario_c2.py, patch_scenario_c2_special_cases.py,
  update_flags_c2.py         Scenario C.2 pipeline (EAT-Lancet 2025 revision)
  dashboard/                 template.html, app.js, methodology_body.html — the dashboard's
                              source pieces, assembled by build_dashboard.py

build_dashboard.py    assembles output/dashboard.html from src/dashboard/* + output/dashboard_data.json

output/
  dashboard_data.json   data export (rebuild with export_dashboard_data.py)
  dashboard.html        the final, single-file dashboard (rebuild with build_dashboard.py)

docs/
  methodology.md   the authoritative reference: every data source, method, formula, and
                    documented assumption behind every number on the dashboard, section by section

plans/
  PLAN.md               the original analysis & simulation plan (scope, taxonomy, formulas,
                         v1/v2 boundary), written before Phase 1
  PHASE1-9_NOTES.md      the initial nine-phase build: data acquisition, demographic modelling,
                         requirement/consumption models, waste and feed adjustments, scenario
                         engine, nutritional-adequacy checks
  PHASE10-14_NOTES.md    post-launch additions, each driven by direct user feedback on the live
                         dashboard: the EAT-Lancet scenario, uncertainty bands, corrected
                         assumptions (nuts, honey, pasta/durum wheat), and the 2025 EAT-Lancet
                         revision (Scenario C.2)

DATA_SOURCES.md   catalogue of every external data source with URLs, access method, and
                   freshness caveats
```

## Rebuilding the dashboard

If any `data/processed/*.csv` file or any file under `src/dashboard/` changes, regenerate the
dashboard from the project root:

```
python3 src/export_dashboard_data.py   # data/processed/*.csv -> output/dashboard_data.json
python3 build_dashboard.py             # + src/dashboard/*    -> output/dashboard.html
```

If a Scenario C.2-specific input changes, run its pipeline first, in order:

```
python3 src/scenario_c2_eatlancet2025.py
python3 src/update_scenario_c2.py
python3 src/patch_scenario_c2_special_cases.py
python3 src/update_flags_c2.py
python3 src/export_dashboard_data.py
python3 build_dashboard.py
```

Both scripts in the second pipeline are idempotent — safe to re-run after later data changes
without duplicating columns.

## Status

14 phases in: the original nine-phase build (data acquisition through nutritional-adequacy
checks and the scenario engine), plus five post-launch rounds of user-driven refinement — an
EAT-Lancet comparison scenario, cross-source uncertainty bands, corrected assumptions on nuts,
honey, and pasta/durum wheat sourcing, and a second EAT-Lancet scenario tracking the Commission's
2025 revision. See `plans/PHASE14_NOTES.md` for the most recent round and `docs/methodology.md`
for the consolidated, currently-accurate picture of every number in the dashboard.
