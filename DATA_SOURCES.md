# Data sources — Eesti toidujulgeoleku analüüs

Catalogue of concrete sources found for this project, with what each gives us, access notes, and freshness caveats. This is a living document — update it as sources are actually pulled in Phase 1.

## 1. Population & demographics

**Statistikaamet, table RV021** — "Rahvastik soo ja vanuserühma järgi, 1. jaanuar" (population by sex and age group, Jan 1).
https://andmed.stat.ee/et/stat/rahvastik__rahvastikunaitajad-ja-koosseis__rahvaarv-ja-rahvastiku-koosseis/RV021
Also RV0212 (population by sex/age with annual average) at the same path.
Gives the exact age×sex population counts needed to weight nutritional requirements up to a national total. PxWeb — exportable as CSV/JSON via the API, no manual download needed.

## 2. Nutritional & food-group requirements (recommendation side)

**Tervise Arengu Instituut (TAI) — "Eesti riiklikud toitumise, liikumise ja uneaja soovitused. Tabelraamat" (2025)**
Landing page: https://www.tai.ee/et/valjaanded/eesti-riiklikud-toitumise-liikumise-ja-uneaja-soovitused-tabelraamat
Direct PDF: https://www.tai.ee/sites/default/files/2025-01/tabelraamat_13.1.25.pdf
This is the primary reference: energy and nutrient reference values and, importantly, recommended food-group amounts, broken out by life-stage/age group and sex (infants, children, adolescents, adults, elderly, pregnant, nursing) and by physical activity level. This is the table booklet a dietitian would use — it's the closest thing to raw reference data TAI publishes. **Needs to be downloaded and parsed (PDF table extraction) in Phase 1** — the exact age/sex/activity bins it uses will define the demographic grid for the whole model, rather than us inventing our own bins.

**TAI toidupüramiid (food pyramid)** — https://www.tai.ee/et/valjaanded/toidupuramiid
Defines TAI's own food-group taxonomy (5 core groups + 1 discretionary group — see Section 3 of PLAN.md) and gives portion-based daily targets at three energy levels (~1600 / 1800–2400 / 2400–3200 kcal, i.e. roughly inactive-elderly-women / adult-women / adult-men bands). Useful as a simplified, cross-checkable version of the Tabelraamat, and as the source for the group taxonomy itself.

## 3. Actual consumption (what people currently eat)

**TAI — Eesti Rahvastiku Toitumise Uuring (RTU), 2014**, PxWeb database.
https://statistika.tai.ee/pxweb/et/Andmebaas/Andmebaas__05Uuringud__09RTU
12 tables including: average daily food-group consumption (from 24h dietary recall), weekly food consumption (recall- and frequency-based), fruit/vegetable portions, nutrient intake vs. recommendations, macronutrient split, BMI, physical activity duration vs. guidelines. Demographic breakdowns (age, sex, and likely education/region) are selectable per table.
**Key caveat: this survey is from 2014 — 12 years old at the time of this project.** No newer full national dietary survey was found in this search round; TAI's more recent "Eesti täiskasvanud rahvastiku tervisekäitumise uuring" (health behaviour survey, 2022) covers some diet-adjacent behaviour but is not a full quantified food-group consumption survey. Phase 1 should (a) confirm whether a newer RTU wave exists before building on 2014 data, and (b) if not, treat 2014 consumption patterns as the best available baseline, sanity-checked against more recent partial indicators (e.g. Statistikaamet household budget survey food expenditure shares, per-capita apparent consumption implied by the food-balance/self-sufficiency data in Section 5) and flagged clearly as a limitation in the output.

**Statistikaamet household budget survey (leibkonna eelarve uuring)** — not yet pulled; worth checking for food expenditure-by-category shares as a freshness cross-check on RTU 2014 patterns (expenditure share ≠ quantity, but trend direction is informative).

## 4. Domestic production

**Statistikaamet — Loomakasvatussaaduste tootmine** (livestock product production)
https://andmed.stat.ee/et/stat/majandus__pellumajandus__pellumajandussaaduste-tootmine__loomakasvatussaaduste-tootmine
Meat (by species), milk, eggs production volumes.

**Statistikaamet — annual "Loomakasvatus ja lihatootmine" (livestock and meat production) statistical releases** (e.g. 2019/2020 editions found; check for the latest year at publication time) — narrative + tables, useful for context and definitions alongside the PxWeb tables.
https://stat.ee/et/statistika-too/loomakasvatus-ja-lihatootmine-2020

**Statistikaamet — "Põllumajandussaaduste arvepidamine"** (agricultural output accounts) — crop production volumes (grain, potatoes, vegetables, fruit/berries).
https://www.stat.ee/et/statistika-too/pollumajandussaaduste-arvepidamine-2021 (check for latest year)

**Statistikaamet metadata pages** for methodology/definitions:
https://www.stat.ee/et/metaandmed/21203 (Loomakasvatus ja lihatootmine)

## 5. Trade (imports/exports) & animal feed

**Statistikaamet — Foreign trade (Väliskaubandus) tables**, PxWeb, under Majandus → Väliskaubandus. Needed for: food-item imports/exports (to complete the FAO-style balance: production + imports − exports − other uses = domestic supply), and separately for animal feed grain/protein imports (esp. soybean meal, which Estonia does not produce and imports almost entirely for livestock feed).
https://stat.ee/en/find-statistics/statistics-theme/economy/foreign-trade/exports-goods (English export-goods landing page; exact commodity-level PxWeb table to be located in Phase 1).

**Eesti Konjunktuuriinstituut (Estonian Institute of Economic Research)** reports on the grain/oilseed market and food sector export capacity — narrative context, possibly some feed-use volumes.
https://epkk.ee/wp-content/uploads/2019/12/Teraviljaturg-2019-III-kv.pdf (grain & oilseed market, example vintage — check for latest quarter)
https://www.ki.ee/publikatsioonid/valmis/Eesti_toidusektori_ekspordivoimekus.pdf (food sector export capacity)

**Note:** No single ready-made "% of animal feed that is imported" statistic was found in this pass. Expect to construct this in Phase 5 from (a) domestic grain production minus exports minus human/industrial use = grain available for feed, cross-checked against (b) feed import volumes (esp. protein feed/soybean meal, which is close to 100% imported for a non-soy-growing country like Estonia) and (c) standard feed-conversion-ratio (FCR) assumptions per livestock species (published zootechnical literature, not Estonia-specific) to estimate total feed demand. This is the most assumption-heavy part of the model and should be presented as a labelled estimate/sensitivity range, not a precise figure.

## 6. Self-sufficiency ratios — pre-computed, official (important shortcut + calibration anchor)

**"Toidu varustuskindluse strateegia 2023+"** (Food Supply Security Strategy 2023+), Regionaal- ja Põllumajandusministeerium (Ministry of Regional Affairs and Agriculture).
PDF: https://www.agri.ee/sites/default/files/documents/2024-05/strateegia-2023-toidu-varustuskindlus.pdf
Contains a ready-made table of Estonia's self-sufficiency rate (isevarustatuse tase) by category, presented as a 5-year average (exact reference years not stated in the excerpt pulled — confirm in Phase 1):

| Category | Self-sufficiency |
|---|---|
| Fish | 300% |
| Grain | 199% |
| Dairy | 166% |
| Beef | 95% |
| Lamb/goat meat | 90% |
| Pork | 78% |
| Potatoes | 70% |
| Total meat | 74% |
| Poultry | 57% |
| Eggs | 54% |
| Vegetables | 46% |
| Fresh fruit/berries | 8% |

This is extremely valuable: it lets us **calibrate/validate** the bottom-up production-and-trade model built in Phase 5 against an official, already-computed figure per category, rather than relying solely on a from-scratch FAO-balance build. Where our bottom-up number and this figure diverge significantly, that's a flag to investigate (different reference year, different category definition, etc.), not necessarily an error.

**"Toidujulgeoleku aastaraamat 2025"** (Food Security Yearbook 2025), same ministry.
https://www.agri.ee/toidujulgeoleku-aastaraamat-2025
Broader narrative context (four pillars: domestic production capacity, supply-chain business continuity, functioning trade, strategic reserves), some sector-specific data points (organic farming area, seed production, fishing quotas), geopolitical/climate framing. Useful for the write-up and for the "critical dependencies" narrative, less useful as a quantitative source in itself.

**Statistikaamet, 2015 article** (data year ~2014) — https://stat.ee/et/uudised/2015/09/15/eesti-isevarustatus-pohiliste-toiduainetega — older self-sufficiency figures by more granular product (e.g. wheat 192%, barley 149%, oats 162%, butter 161%, cheese/curd 143%, carrots 91%, tomatoes 29%, onions 20%). Useful for sub-category granularity (e.g. splitting "vegetables" into individual crops) and as a historical comparison point to see the trend direction, but superseded in currency by the 2023+ strategy table above.

## 7. Food waste & losses

**SEI (Stockholm Environment Institute) Tallinn — "Toidujäätmete ja toidukao teke Eesti toidutarneahelas" (2021)**, commissioned study, likely for the Ministry of Environment / Kliimaministeerium.
https://www.sei.org/wp-content/uploads/2021/05/toidujaatmete-ja-toidukao-teke-eesti-toidutarneahelas-2021.pdf
Reference year 2020. Total food waste: ~167,000 t/year (126.5 kg/capita), split by supply-chain stage:

| Stage | t/year | kg/capita | share |
|---|---|---|---|
| Households | 80,564 | 61.2 | 48% |
| Food industry | 31,622 | 24.0 | 19% |
| Primary production | 23,612 | 17.9 | 14% |
| Retail | 19,976 | 15.2 | 12% |
| Catering | 10,739 | 8.2 | 6% |

Of this, ~84,000 t/year (63.7 kg/capita, 50% of total) is classified as avoidable loss (economic value ~€164M/year). Within primary production, potatoes account for ~60% of losses. This is the best available Estonia-specific waste dataset and should anchor the waste module; it does not appear to give a full per-food-group breakdown at every stage, so some stages will need generic FAO/WRAP loss-rate assumptions by food category as a fallback, clearly labelled as such.

## 8. International cross-check sources

**FAOSTAT Food Balance Sheets (New Food Balances), Estonia** — https://www.fao.org/faostat/en/#data/FBS
Standardised production/import/export/feed/seed/waste/food-supply breakdown per commodity, computed with consistent FAO methodology across countries. Useful as an independent cross-check on both the domestic-production numbers and the derived self-sufficiency ratios, and as a fallback for any category where Estonian source data is thin. Typically lags 1–2 years behind the current year.

**Eurostat** — agricultural production and self-sufficiency-adjacent indicators (e.g. agri-environmental indicators, supply balance sheets for cereals/meat/milk) for EU cross-country comparison. To be pulled in Phase 1 if useful for context ("how does Estonia compare to other small/northern EU states").

## 9. Phase 1 acquisition status (updated 2026-08-30 — see PHASE1_NOTES.md for the full write-up)

| Source | Status | Where |
|---|---|---|
| Population by age/sex (RV021) | Acquired, validated (totals to 1,360,745) | `data/raw/statistikaamet/population_by_age_sex_2026.csv` |
| TAI Tabelraamat (energy/macronutrient/food-group-portion tables) | Acquired via PDF text extraction; flagged for a precision re-check before use as load-bearing numbers | `data/raw/tai/tabelraamat_2025_extract.md` |
| TAI RTU 2014 consumption by age/sex (RTU011) | Acquired in full (768/768 cells), 0 parse errors | `data/raw/tai/RTU011_consumption_by_age_sex_2014.csv` |
| Confirmed no newer national dietary survey exists | Confirmed directly with TAI's own page — next wave fields through May 2027 | noted in `data/raw/tai/README.md` |
| Domestic production + trade + feed + loss balance sheets (cereals, potato, veg, fruit, meat, eggs, dairy) | Acquired for 2024 via the PM20/31/33/34/42/45/47 "ressurss ja kasutamine" series — a much better source than originally scoped, already includes imports/exports/feed-use/loss per item | `data/raw/statistikaamet/PM*_2024.csv`, validated against this section's official ratios (see that folder's README.md) |
| Foreign trade at commodity level (separate from the above) | Superseded — the PM* balance tables above already carry the food-relevant import/export figures per item, so a separate pull wasn't needed except for the point below | — |
| Feed-conversion / protein-feed import share | Still open — grain-specific feed use is now known directly (PM20), but the protein-feed/soy import share has no ready-made Estonian source; will need an assumption set in Phase 3 | flagged in PHASE1_NOTES.md |
| Exact reference years behind the strategy document's "5-year average" | Confirmed NOT stated anywhere in the document (checked directly) — treat as an inference (~2018-2022, given 2023 publication), not a fact, wherever that table is cited | PHASE1_NOTES.md |
| County-level (maakond) detail | Not pulled — deferred, not needed for the national-level question this project answers | — |

Network-access note: both this session's sandboxed shells block the domains in this document outright; every pull above was done by driving an actual browser session (see PHASE1_NOTES.md) rather than shell `curl`. Anyone continuing this work from a different environment should check whether that restriction still applies before assuming shell-based pulls won't work.
