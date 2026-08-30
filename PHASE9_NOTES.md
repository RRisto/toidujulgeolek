# Phase 9 notes — dashboard build

Implements PLAN.md Section 7 item 9: export the consolidated data, build the single self-contained
HTML dashboard per Section 9, wire it to the exported data. Status: done. This is the final phase
of the nine-phase build plan.

## 1. Data export

`src/export_dashboard_data.py` reads every processed CSV from Phases 3-8
(`requirement_model_national.csv`, `consumption_model_national.csv`,
`over_under_consumption_by_segment.csv`, `self_sufficiency_model.csv`, `waste_model.csv`,
`scenario_comparison.csv`, `critical_dependency_flags.csv`, `faostat_cross_check.csv`) and produces
one JSON file, `output/dashboard_data.json`, that the dashboard reads verbatim — no computation
happens client-side beyond formatting and sorting.

The one genuinely new computation added at this stage is a **tonnage-weighted aggregate
self-sufficiency figure** for the scorecard. Every prior phase deliberately avoided collapsing 16
very different per-category self-sufficiency ratios into one number, on the grounds that doing so
would overclaim precision. A dashboard needs a headline, though, so Phase 9 adds one — transparently:

- Weighted by Scenario A demand tonnage per category (`weighted_headline()` in the export script).
- Reports its own `coverage_pct_of_tonnage` (77.4%) alongside the number, and explicitly lists
  which categories are included, excluded (no resolved single figure — porridge/pasta/rice range,
  legumes bimodal, nuts+seeds ~0% assumed, sweets not scoreable), and which have no tonnage weight
  at all, rather than silently averaging over gaps.
- Result: **106.8%** for Scenario A (weighted heavily by dairy and grain, both strongly
  self-sufficient and large by mass) vs. **64.8%** for Scenario B — a 42-point swing from a single
  change in assumption about what people eat, production held fixed. Hand-verified by summing
  weighted per-category contributions independently of the Python computation. **[Post-launch
  correction, see docs/methodology.md Section 4.2]**: the Scenario B figure above reflects a since-
  corrected dairy portion-mass error; the corrected Scenario B weighted headline is **76.7%** (a
  30-point swing from Scenario A, not 42), left as originally written here for the historical
  record of what Phase 9 computed at the time — the corrected figure is authoritative in
  `dashboard_data.json` and the rendered dashboard.
- The two waste-lever scorecard tiles (108.9% / 111.1%) use the same weighting basis applied to
  the Scenario A waste-adjusted self-sufficiency figures from Phase 6.

## 2. Dashboard build

Skills used: `dataviz` (chart form selection, the validated status/categorical palette, mark specs,
tooltip and accessibility conventions) and `artifact-design` (three-state light/dark theming,
AI-cliché avoidance, product-style naming, Google Fonts as the only external CDN dependency).

Architecture follows PLAN.md Section 6: the model (Python, Phases 1-8) and the presentation stay
decoupled. `src/dashboard/template.html` (page skeleton, full CSS token system, structure),
`src/dashboard/app.js` (all rendering logic — 7 section renderers reading `DATA` from the embedded
JSON), and `src/dashboard/methodology_body.html` (static prose + the data-sources table) are three
separate, human-editable source files. `build_dashboard.py` at the project root assembles them with
`output/dashboard_data.json` into the single self-contained `output/dashboard.html` — no build
step beyond running that script, and no external runtime dependency besides one Google Fonts
stylesheet (IBM Plex Sans/Mono), which degrades gracefully to system fonts if unreachable.

Seven sections, matching PLAN.md Section 9:

1. **Scorecard** — the four headline tiles described above.
2. **Self-sufficiency by food group** — horizontal bar chart, Scenario A/B toggle, status-coloured
   (good/warning/critical), with a feed-adjusted-lower-bound tick mark where Phase 6 computed one,
   and a table view twin for the same data.
3. **Critical dependencies** — card grid, one per flagged category from
   `critical_dependency_flags.csv`, distinguishing genuine sub-50% dependencies from unresolved
   data gaps.
4. **Actual vs. recommended consumption** — dumbbell chart, national by default, filterable to any
   of the 6 demographic segments Phase 4 computed (age band × sex).
5. **Scenario delta** — diverging bar chart of the percentage-point swing from Scenario A to B per
   category, sorted by magnitude.
6. **Food waste** — stacked bar (household vs. other supply-chain stages) by food group, plus the
   waste-reduction-lever table (required-production multiplier at today's waste / -25% / -50%).
7. **Methodology** — collapsed by default, full write-up (what the model is, data sources, how the
   numbers are built, the Phase 8 FAOSTAT validation with its comparison table embedded, and
   assumptions/limitations stated plainly), reusing the prose from `docs/methodology.md`.

## 3. Verification

The published Claude Artifact renders inside a cross-origin iframe with a fixed, non-auto-resizing
height. Scroll-based visual verification through that wrapper (mouse wheel, Page Down, nav-link
clicks, all via browser automation) produced no visible scroll movement across many attempts, and
one screenshot attempt failed outright with a 30-second CDP timeout. Rather than keep debugging a
tooling/wrapper question that had nothing to do with the actual page, verification switched to
driving the built `output/dashboard.html` file directly with Playwright (Chromium, headless,
`file://`) — bypassing the artifact viewer entirely. This is a strictly cleaner signal: it tests the
actual deliverable in isolation, with no iframe, no cross-origin sandboxing, and no dependency on
claude.ai's own infrastructure being healthy.

That direct pass checked: console/page errors, total rendered page height, a full-page screenshot
plus one at each of the 7 section anchors, the Scenario A/B toggle, the self-sufficiency table-view
toggle, the demographic segment filter, the methodology `<details>` expand, and dark mode via
`prefers-color-scheme` emulation — 13 screenshots in total, manually inspected.

**Found and fixed three real rendering bugs**, none of which were data or logic errors —
all confined to `src/dashboard/template.html` (CSS) and `src/dashboard/app.js`:

1. **Feed-adjusted-bound marker painting over percentage labels.** The `.hbar-marker` tick (a 2px
   vertical line) and the `.hbar-fill` bar's value label had no explicit stacking order, so the
   marker — appended later in the DOM — painted on top of the label text whenever the two
   coincided (visible as e.g. "53.6%" rendering with the "3" struck through). Fixed with explicit
   `z-index` (`.hbar-fill` above `.hbar-marker`), so the marker is hidden wherever the opaque bar
   covers it and still visible as a tick where it extends beyond the bar.
2. **Scenario-delta chart value labels colliding with row labels.** The diverging bar chart
   positioned its value label with `right: calc(100% - X%)` relative to the *track*, not the bar.
   For the largest bars (e.g. fish & seafood, -211.4 pt) this pushed the label's anchor point past
   the track's own left edge and into the row-label column, overlapping category text. Fixed by
   anchoring the label to the bar element itself (`fill.appendChild(tip)`) — the same pattern
   already working correctly in the self-sufficiency chart — with wide bars getting the label
   inside in white and narrow bars keeping it outside in ink color.
3. **Long data-gap notes overflowing the viewport.** The `.pill` component is `white-space: nowrap`
   by design, correct for its usual short badges ("Critical", "Data gap") but wrong for the
   sentence-length "no single figure — ..." notes reused from the self-sufficiency chart, which ran
   off the right edge of the page uncut in both light and dark mode. Added a `.pill-wrap` modifier
   (`white-space: normal`, left-aligned, `flex: 1 1 auto`) applied to those specific badges.

After the fix, the same Playwright pass was re-run in full: `document.body.scrollHeight` unchanged
(6271px, no layout blow-up from the fix), console errors unchanged (one expected
`ERR_TUNNEL_CONNECTION_FAILED` from the Google Fonts request, which the sandbox's network egress
doesn't reach — not a page bug, and the CSS already falls back to system fonts), and all three
fixed regions re-screenshotted clean. The published artifact was then republished from the fixed
file.

## 4. Deliverables

- `output/dashboard_data.json` — data export.
- `src/export_dashboard_data.py` — the export script (includes the new weighted-headline
  computation).
- `src/dashboard/template.html`, `src/dashboard/app.js`, `src/dashboard/methodology_body.html` —
  dashboard source, kept separate from the assembled page so it can be regenerated without
  touching the model.
- `build_dashboard.py` — assembles the above into the final page. Run `python3 build_dashboard.py`
  from the project root any time the data or dashboard source changes.
- `output/dashboard.html` — the final, self-contained, verified dashboard.
- Published as a Claude Artifact (private, shareable from its own page).

## 5. Project status

All nine phases of PLAN.md Section 7 are now complete. See PLAN.md's own per-item status notes for
the full chain from data acquisition through this dashboard.
