# Toidujulgeolek — Estonia food self-sufficiency model

Could Estonia feed its population a nutritionally adequate diet from domestic production, and
where are the critical dependencies? Answered by food group, under Estonia's actual current
production, and compared against four different demand scenarios: today's actual consumption,
TAI's (Tervise Arengu Instituut) recommended diet, and two editions of the EAT-Lancet Planetary
Health Diet (2019 and a 2025 revision). The model accounts for the population's actual age/sex/
activity structure, food lost to waste, and the fact that a chunk of domestic production (grain,
some fish) feeds livestock rather than people directly.

EAT-Lancet source grams and model-comparison grams are deliberately separate: dry/uncooked source
weights are converted through source calories to TAI's edible/ready-to-eat representative mass
basis before C/C2 demand is compared with A/B. See methodology Section 10.3.

The EAT-Lancet 2025 conversion has a separate sensitivity analysis. It tests 91 documented
TAI-based conversion variants one at a time and reports the resulting range for each of the 14
food-group rows. This is a deterministic sensitivity range, not a Monte Carlo simulation,
confidence interval, or probability distribution. See methodology Section 10.4.

The main result is a self-contained interactive dashboard: **[`output/dashboard.html`](output/dashboard.html)**.

## Quick orientation

- **Just want the results?** Open `output/dashboard.html` in a browser. Nothing else to run.
- **Want to understand a number?** Every figure on the dashboard links back to `docs/methodology.md`
  — start there, not in the phase notes, for what a number means and how confident to be in it.
- **Want the full source catalogue?** `DATA_SOURCES.md` — every dataset used, where it came from,
  and its freshness/access caveats.
- **Want to inspect the EAT-Lancet 2025 conversion sensitivity?** Open
  [`output/eatlancet2025_sensitivity_et.html`](output/eatlancet2025_sensitivity_et.html) for the
  compact graph or read
  [`docs/eatlancet2025_conversion_sensitivity_et.md`](docs/eatlancet2025_conversion_sensitivity_et.md)
  for the findings and interpretation limits.
- **Want the project history?** `plans/` — the original build plan and a phase-by-phase log of
  everything done since, including every post-launch correction driven by user feedback.

## Repository layout

```
data/
  raw/            source data as pulled (Statistikaamet, TAI, FAOSTAT, SEI, agri.ee), with
                  per-source README.md provenance notes
  crosswalk/      taxonomy crosswalks between data sources and the project's own food-group model
                  (including eatlancet2025_sensitivity_candidates.csv)
  processed/      derived model outputs (self-sufficiency figures, scenario comparisons,
                  critical-dependency flags, consumption models) — the dashboard's actual inputs
                  plus the standalone eatlancet2025_conversion_sensitivity.csv

src/
  export_dashboard_data.py   reads data/processed/*.csv, writes output/dashboard_data.json
  scenario_c_eatlancet.py    Scenario C demand crosswalk (EAT-Lancet 2019)
  scenario_c2_eatlancet2025.py, update_scenario_c2.py, patch_scenario_c2_special_cases.py,
  update_flags_c2.py         Scenario C.2 pipeline (EAT-Lancet 2025 revision)
  eatlancet2025_sensitivity.py
                              validates TAI conversion variants and writes the standalone
                              EAT-Lancet 2025 sensitivity CSV and findings report
  dashboard/                 template.html, app.js, methodology_body.html — the dashboard's
                              source pieces, assembled by build_dashboard.py

build_dashboard.py    assembles output/dashboard.html from src/dashboard/* + output/dashboard_data.json

output/
  dashboard_data.json   data export (rebuild with export_dashboard_data.py)
  dashboard.html        the final, single-file dashboard (rebuild with build_dashboard.py)
  eatlancet2025_sensitivity_et.html
                        standalone compact conversion-sensitivity graph (not part of the dashboard)

docs/
  methodology.md   the authoritative reference: every data source, method, formula, and
                    documented assumption behind every number on the dashboard, section by section
  eatlancet2025_conversion_sensitivity_et.md
                    generated Estonian sensitivity findings and interpretation limits

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

### Editing Estonian UI text

Edit `src/dashboard/strings_et_v2.json` for `output/dashboard_et_v2.html`.
The older layout uses `src/dashboard/strings_et.json` for `output/dashboard_et.html`.
Both catalogues now include chart and table labels, tooltips, demographic labels,
units, accessibility text, data names and notes, and the full methodology text.

- Existing sections contain page and JavaScript labels.
- `methodology` contains the text fragments in the methodology section; preserve HTML entities and surrounding spaces.
- `data_text` contains deduplicated data labels and notes. Edit each entry's `text`; keep its `source` and key unchanged. Repeated occurrences update together.
- Keep placeholders such as `{coverage}` and `{scenario_c_pct}` intact.

Rebuild from the project root after editing:

```
python build_dashboard_et_v2.py
python src/dashboard/build_dashboard_et.py
python src/dashboard/check_translations.py
```

The builders read these translations directly; you do not need to edit the data
export or HTML to change their wording. New untranslated data text causes a build
error so it can be added to the catalogue.

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

### Rebuilding the EAT-Lancet 2025 sensitivity outputs

The sensitivity analysis is standalone and does not rewrite Scenario C.2 or dashboard artifacts:

```
python -m src.eatlancet2025_sensitivity
python -m build_treemap.build_sensitivity_chart
```

The first command validates the 91-row candidate catalogue and writes the 14-row CSV plus the
Estonian findings report. The second command renders the compact HTML graph from that CSV.

## Status

The original nine-phase build has been followed by multiple user-driven refinements: EAT-Lancet
2019 and 2025 scenarios, cross-source uncertainty bands, corrections to food-form assumptions,
waste and feed companion measures, secondary-effects analysis, multilingual dashboard builds,
and the standalone EAT-Lancet 2025 conversion sensitivity analysis. See `plans/` for the build
history and `docs/methodology.md` for the consolidated, currently accurate methods.
