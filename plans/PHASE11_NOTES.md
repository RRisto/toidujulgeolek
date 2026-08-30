# Phase 11 notes — cross-check uncertainty bands on the self-sufficiency chart

Post-launch addition, requested by the user after Phase 10 (Scenario C) closed out. Prompted by a
general question about showing uncertainty alongside point estimates, not just a single percentage
per food group. Status: done.

## 1. Why this addition

The dashboard's self-sufficiency chart (section 02) has always shown a single point percentage per
food-group subitem. Section 8 of `docs/methodology.md` (Phase 8's FAOSTAT validation) already
computed an independent cross-check for many of these subitems, and flagged several material
divergences (vegetables, rapeseed oil, beef/poultry) — but that information lived only as prose in
the methodology doc and in `data/processed/faostat_cross_check.csv`, invisible from the dashboard
itself. This phase surfaces it directly on the chart people actually look at.

Framing choice, stated explicitly rather than left implicit: this is an *independent cross-check
range*, not a statistical confidence interval. Nothing in this project's self-sufficiency figures
comes from a random sample with a known sampling distribution, so a textbook CI doesn't apply.
What does exist is, for a subset of subitems, two independently-sourced point estimates for the
same quantity (this project's own derived/official figure, and FAOSTAT's) — the gap between them is
a genuine (if partial) signal of how uncertain the "true" figure is, which is exactly what a range
band communicates without overclaiming statistical rigor the data doesn't have.

## 2. Data model

`src/export_dashboard_data.py` gained a new section (1b) that reads
`data/processed/faostat_cross_check.csv` and collapses it into a low/high band per
`(pyramid_group, subitem)` key:

- Only rows carrying **both** a `faostat_self_sufficiency_pct` and a `project_self_sufficiency_pct`
  are used — pure FAOSTAT component rows with no comparable project figure (e.g. "Wheat and
  products" alone, or "Meat, total") are excluded, since there's nothing to compare them against.
- `FAOSTAT_ITEM_TO_SUBITEM`, a hand-maintained dict, maps each FAOSTAT item to this project's
  `(pyramid_group, subitem)` key. This can't be automatic: FAOSTAT's item taxonomy doesn't align
  1:1 with the pyramid taxonomy used here — most notably, FAOSTAT reports beef, pork, and offal as
  three separate lines, all of which roll into this project's single "Red meat" subitem. For Red
  meat, and for rapeseed (which has both a raw-seed and a refined-oil FAOSTAT line, both compared
  against the same 69.3% project figure), the resulting band pools every value from every mapped
  row — so it's wider than a strict one-to-one comparison, and is documented as such in the
  tooltip's basis text.
- For each key, `cross_check_low_pct` / `cross_check_high_pct` = min/max across all pooled values
  (FAOSTAT and project alike), and `cross_check_basis` lists the contributing FAOSTAT item(s) and
  year(s) for provenance. All three fields are `null` where no comparable FAOSTAT row exists
  (most subitems — this is a partial cross-check, not full coverage).
- 12 of the 16 food-group subitems ended up with a band; the 4 that didn't (legumes, nuts+seeds+
  cocoa, sweets & discretionary, soy oil) already had no FAOSTAT row in the source CSV at all.

## 3. Dashboard integration

`src/dashboard/app.js`'s `renderSSChart()`: for each subitem with a non-null band, draws a shaded
`.hbar-range` rectangle (spanning low% to high% of the chart's scale) plus two `.hbar-range-cap`
end-ticks, positioned behind the existing point-estimate bar (`.hbar-fill`, `z-index:2`, sits on
top at `z-index:1`) — so where the band falls entirely within the bar's own span (e.g. dairy,
139–166% band under a 166% bar) it's invisible by design, and only the portion extending *beyond*
the point estimate is visible. This deliberately mirrors how the existing `feed_adjusted_low_bound_pct`
marker already works, rather than inventing a new interaction pattern.

Also extended: the hover tooltip gained an "Independent cross-check range" row (low%–high%,
formatted as an en-dash range) directly under the existing "Feed-adjusted lower bound" row; the
table view (`renderSSTable`) gained a matching "Cross-check range" column; `src/dashboard/template.html`
gained the `.hbar-range` / `.hbar-range-cap` CSS and one new legend entry explaining the shaded band.

`docs/methodology.md` Section 8 gained one paragraph pointing from the FAOSTAT validation writeup
to this dashboard feature, so the doc and the chart cross-reference each other.

## 4. Verification

Staged the rebuilt `output/dashboard.html` into the cloud sandbox and drove it headlessly with
Playwright (this project's local machine has no Playwright install, so this step ran in the cloud
container instead — see PHASE9_NOTES.md's own verification approach for precedent). Checked:
console/page errors (only the same pre-existing Google Fonts `ERR_TUNNEL_CONNECTION_FAILED`, no new
errors); the rendered chart in both light and dark mode across all 12 banded subitems, including
edge cases (Vegetables: band and bar both end at 46%, only the bar is visible — confirmed via
computed style, not just a screenshot read, since the pixel diff first looked like a missing bar
and turned out to be a rendering-vs-perception issue, not a bug); the tooltip's rendered HTML on a
banded row (rapeseed: correctly showed "69.3%–265.2%"); the table view's new column and headers.

## 5. Deliverables

- `src/export_dashboard_data.py` — new FAOSTAT-cross-check-to-band computation (section 1b);
  `food_groups` entries gained `cross_check_low_pct`, `cross_check_high_pct`, `cross_check_basis`.
- `src/dashboard/app.js` — range band + end-cap rendering in `renderSSChart()`, tooltip row, table
  column.
- `src/dashboard/template.html` — `.hbar-range` / `.hbar-range-cap` CSS, one new legend entry.
- `docs/methodology.md` Section 8 — one new paragraph cross-referencing this feature.
- `output/dashboard_data.json`, `output/dashboard.html` — rebuilt via `export_dashboard_data.py`
  then `build_dashboard.py`.
