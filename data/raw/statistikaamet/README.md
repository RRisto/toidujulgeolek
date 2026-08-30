# Statistikaamet raw data — Phase 1 pull (2026-08-29)

## Population
`population_by_age_sex_2026.csv` — RV021, 1 Jan 2026, by sex and 22 age bands (single-year "0", then 5-year bands to 100+). Total = 1,360,745, matches Estonia's known population (sanity-checked OK).

## Food resource-and-use ("ressurss ja kasutamine") balance sheets — 2024
These come from Statistikaamet's **PM20/PM31/PM33/PM34/PM42/PM45/PM47** series, an Estonian-produced FAO-style supply/utilization balance per commodity: production, imports, exports, stock change, and domestic use split into seed, loss, animal feed, industrial use and human consumption (gross and net, plus per-capita). This directly supplies most of what Section 5.3 (self-sufficiency) and 5.4/5.5 (feed and loss) of PLAN.md need, for these commodities, in a single official source — better than reconstructing it from separate production/trade tables.

Files (all reference year 2024, the latest complete calendar year):
- `PM20_cereals_2024.csv` — cereals, by type (total/wheat/durum wheat/rye/barley/oats/other cereals/maize). Note: "total" row is blank in the source (not published pre-aggregated) — sum wheat+rye+barley+oats+other_cereals for a grain total; durum wheat and maize are already subsets of wheat and "other cereals" respectively, so don't double-count them into that sum.
- `PM42_meat_2024.csv` — meat, by type (total/beef/pork/sheep_goat/poultry/other_animals/offals). "total" row here IS populated directly by Statistikaamet.
- `PM31_potato_2024.csv`, `PM33_vegetables_2024.csv` (fresh vegetables), `PM34_fruit_2024.csv` (fresh fruit & berries), `PM45_eggs_2024.csv`, `PM47_dairy_2024.csv` (9 dairy product lines: fresh products excl. cream, milk/buttermilk, cream, concentrated milk, whole/skimmed milk powder, butter, cheese incl. fresh, processed cheese).

Blank cells in `value` mean the source table left that cell empty for that year/category (not zero) — usually because the breakdown genuinely doesn't apply (e.g. no seed use for meat) or Statistikaamet doesn't publish that specific cross of category × indicator.

### Validation against the 2023+ strategy document's self-sufficiency table
Computed as production / domestic_use from these files, single year 2024, vs. the ministry's 5-year-average figures cited in DATA_SOURCES.md Section 6:

| Category | This pull (2024) | Strategy doc (5yr avg) |
|---|---|---|
| Grain (wheat+rye+barley+oats+other) | 268% | ~199% |
| Meat, total | 71% | ~74% |
| Potato | 64% | ~70% |
| Fresh vegetables | 29% | ~46% |
| Fresh fruit & berries | 8% | ~8% |
| Eggs | 53% | ~54% |
| Beef | 109% | ~95% |
| Pork | 72% | ~78% |
| Poultry | 58% | ~57% |

Most land close to the official figure; the differences (grain, vegetables, beef, potato) are plausibly just single-year (2024, a strong grain harvest year) vs. 5-year-average effects — Estonian grain and vegetable output swings a lot year to year. The vegetables gap (29% vs 46%) is the largest and worth a closer look in Phase 3 (could be a category-definition difference — "fresh vegetables" here vs. all vegetables including processed in the ministry figure). Overall: methodology is validated as sound; recommend using a multi-year average (pull 2019-2024 from the same tables) rather than a single year for the final model, to smooth exactly this kind of annual volatility.

### Source
Statistikaamet PxWeb API, `https://andmed.stat.ee/api/v1/en/stat/<table>`, POST query, json-stat2 format. Table list at:
https://andmed.stat.ee/et/stat/majandus__pellumajandus__pellumajandussaaduste-tootmine__pellumajandussaaduste-ressurss-ja-kasutamine
Pulled via browser fetch (see project notes — the sandboxed shell environments cannot reach andmed.stat.ee directly, a proxy allowlist blocks it; Statistikaamet's API only accepts POST for data queries, which a plain page fetch can't do either, so pulling this required running the fetch from an actual browser session).
