# Phase 13 notes — pasta and the durum wheat question

Post-launch addition, prompted directly by user feedback after Phase 12: "but we produce pasta in
estonia and grow our own wheat." Status: investigated end-to-end, sourced, resolved (no numeric
change, but the assumption is now confirmed rather than merely assumed, and the reasoning behind it
is corrected).

## 1. The question

Phase 12 left the "Porridges/pasta/rice/grain products" category as a ~156.2% *upper bound*,
explicitly excluding pasta on the grounds that "pasta (durum wheat) is very likely also near 0%"
self-sufficient — carried over from this project's original Phase 1 assumption. The user pushed
back on that assumption directly, and correctly, on two factual points: Estonia does produce pasta
domestically, and Estonia does grow its own wheat. Both are true. The question this phase set out
to answer honestly was whether that meant the ~0% pasta assumption was wrong.

## 2. What was checked

- **Statistikaamet resource-and-use ("ressurss ja kasutamine") tables**: confirmed the complete
  list (PM20, 29, 31, 33, 34, 37, 42, 45, 47) has no dedicated pasta/macaroni balance table, and no
  wheat-by-variety breakdown — PM20's wheat figures are a single aggregate, not split into common
  vs. durum. There is no PM-series line to look up for "durum wheat" specifically.
- **Tartu Mill** (Estonia's main flour miller and the country's pasta producer): its own website
  states its pastas are "valminud kodumaisest viljast" (made from domestic grain) as marketing
  copy, but the actual ingredient list for its retail spaghetti gives "durum wheat flour, water" —
  no country-of-origin claim for the durum specifically. Wikipedia independently confirms Tartu
  Mill's product line includes wheat/rye flour, semolina, pasta, and feed ingredients — so the
  pasta-manufacturing claim is real and verified, not in question.
- **PIKK.ee** (Estonia's agricultural extension/knowledge portal), on winter cereal varieties grown
  in Estonia: "Eestis kasvatatakse pehme nisu sorte kuna kõva nisu vajab kasvuks kuivemat ja
  mandrilisemat kliimat" — Estonia grows soft wheat varieties because durum wheat needs a drier,
  more continental climate than Estonia has. All 17 winter wheat varieties it lists for Estonia are
  soft-wheat types; none are durum.
- **ERR/Novaator** (2024, on Estonian farmers experimenting with new crops amid changing climate
  and fertiliser costs): confirms durum wheat is being grown in Estonia, but only as a two-season
  experiment on a single farm (Põlgaste), explicitly framed by the farmer as a drought-adaptation
  trial and by an accompanying expert as contingent on "whether there's someone to sell it to
  afterward" — i.e. not an established commercial crop, and not something that would register in
  national production statistics.

## 3. Resolution

"Wheat" is not one crop for self-sufficiency purposes. Estonia is genuinely, comfortably
self-sufficient in *common/soft wheat* (Triticum aestivum) — this project's own PM20-based figures
already show 268-337% self-sufficiency for wheat overall, used for bread and animal feed. Pasta
specifically requires *durum wheat* (Triticum durum), a different species with different climate
needs, which Estonia does not grow at any commercial scale — confirmed by an agricultural extension
source explaining why (climate), and by a news source confirming the only Estonian durum-growing
activity is a small, uncertain experiment.

So: pasta *manufacturing* is genuinely domestic (Tartu Mill mills, extrudes, and packages pasta in
Estonia) — the user is right about that, and this project's original framing never should have
implied otherwise. But the *raw agricultural input* pasta depends on (durum wheat) is not grown in
Estonia at any meaningful scale, so it is imported. This is the same pattern this project already
applies implicitly elsewhere (e.g. a country can roast imported coffee or refine imported cocoa
domestically without being self-sufficient in the raw crop) and is consistent with this project's
established self-sufficiency convention throughout: production of the raw commodity relative to
domestic use, not location of final processing.

**Net result: no numeric change.** Pasta's ~0% raw-material self-sufficiency, and therefore the
~156.2% upper bound for the blended "Porridges/pasta/rice/grain products" category, both stand.
What changes is that this is now a *sourced, confirmed* finding rather than an *assumption* — and
the earlier note's claim that this was "per PM20's 0% durum production" has been corrected, since
PM20 does not track durum separately at all (there was nothing to report a 0% figure from).

## 4. What was updated

Every file touching this category's reasoning had its note/reason field extended with this
phase's sourcing and the corrected (not-PM20-based) justification — no `_pct` values changed:

- `data/crosswalk/food_group_crosswalk.csv` — `statistikaamet_source`, `self_sufficiency_2024_pct`
  text, `match_quality` (now `partially_split_phase12_pasta_confirmed_phase13`), and `notes`.
- `data/processed/self_sufficiency_model.csv` — `note`.
- `data/processed/scenario_comparison.csv` — `note`.
- `data/processed/critical_dependency_flags.csv` — `reason`.
- `docs/methodology.md` Section 8 — new "Pasta / durum wheat verification (Phase 13)" paragraph.

No changes were needed to `src/export_dashboard_data.py`, `app.js`, or `template.html` — this
category was already, and remains, a text pill rather than a numeric bar (still not a single
resolved point estimate for the whole category, since pasta's *consumption-mix weight* within the
category — as opposed to its self-sufficiency percentage — is still unknown). `output/
dashboard_data.json` and `output/dashboard.html` were rebuilt for consistency, though no numeric
field in them changes as a result of this phase.

## 5. Deliverables

- `docs/methodology.md` — Phase 13 paragraph added to Section 8.
- `data/crosswalk/food_group_crosswalk.csv`, `self_sufficiency_model.csv`,
  `scenario_comparison.csv`, `critical_dependency_flags.csv` — sourcing corrected/strengthened,
  no numeric changes.
- `output/dashboard_data.json`, `output/dashboard.html` — rebuilt (unchanged numerically).
- This file.
