# TAI Tabelraamat 2025 — extracted reference tables

Source: "Eesti riiklikud toitumise, liikumise ja uneaja soovitused. Tabelraamat" (2025)
PDF: https://www.tai.ee/sites/default/files/2025-01/tabelraamat_13.1.25.pdf
Landing page: https://www.tai.ee/et/valjaanded/eesti-riiklikud-toitumise-liikumise-ja-uneaja-soovitused-tabelraamat

**Extraction method & caveat**: pulled via automated PDF-to-text extraction (WebFetch, prompt-targeted per table) because the sandboxed environment cannot download the PDF's raw bytes for direct parsing (andmed.stat.ee/tai.ee are blocked by the shell egress allowlist in both the cloud workspace and the user's local device shell — see PHASE1_NOTES.md). This is a reasonable transcription but was produced by a small summarization model reading converted PDF text, not a deterministic table parser — before it's used as the actual numeric input to the model in Phase 3, spot-check a sample of cells against the source PDF pages cited below (worth doing properly with pdfplumber/camelot once/if the PDF itself can be obtained as a file — e.g. ask the user to download it manually and drop it in data/raw/tai/, since their own machine can reach tai.ee even though this session's shells can't).

---

## Table 4 (p.16) — children/adolescents: daily energy recommendation (kcal) by age, sex, physical activity level (PAL)

PAL categories: Istuv eluviis (sedentary, PAL 1.4) / Mõõdukas kehaline aktiivsus (moderate, PAL 1.6) / Aktiivne eluviis (active, PAL 1.8)

### Girls
| Age | Sedentary | Moderate | Active |
|---|---|---|---|
| 1 | 750 | 860 | 970 |
| 2 | 990 | 1130 | 1270 |
| 3 | 1100 | 1260 | 1410 |
| 4-6 | 1170-1320 | 1340-1510 | 1510-1700 |
| 7-10 | 1400-1660 | 1590-1900 | 1790-2130 |
| 11-14 | 1660 | 1900 | 2140 |
| 15-17 | 1960 | 2240 | 2520 |

### Boys
| Age | Sedentary | Moderate | Active |
|---|---|---|---|
| 1 | 820 | 940 | 1060 |
| 2 | 1070 | 1220 | 1380 |
| 3 | 1180 | 1350 | 1520 |
| 4-6 | 1260-1420 | 1440-1630 | 1620-1830 |
| 7-10 | 1510-1760 | 1720-2020 | 1940-2270 |
| 11-14 | 1780 | 2030 | 2290 |
| 15-17 | 2370 | 2700 | 3040 |

## Table 5 (p.17) — adults/elderly: daily energy recommendation (kcal) by age, sex, PAL

### Women
| Age group | Sedentary | Moderate | Active |
|---|---|---|---|
| 18-24 | 2000 | 2250 | 2550 |
| 25-50 | 1900 | 2150 | 2450 |
| 51-70 | 1750 | 2000 | 2250 |
| >70 | 1700 | 1950 | 2200 |
| Pregnant | 2150 | 2450 | 2750 |
| Nursing (0-6mo) | 2600 | 3000 | 3350 |

### Men
| Age group | Sedentary | Moderate | Active |
|---|---|---|---|
| 18-24 | 2500 | 2800 | 3150 |
| 25-50 | 2350 | 2700 | 3050 |
| 51-70 | 2150 | 2450 | 2750 |
| >70 | 2100 | 2400 | 2700 |

**Men >70 row (confirmed via re-fetch in Phase 3): Sedentary 2100 kcal / Moderate 2400 kcal / Active 2700 kcal.** Matches the pattern from the other rows.

## Table 6 (p.18-19) — macronutrient recommendations, %E, by age group

| Age group | Protein | Fat | Carbohydrate | Fibre | Notes |
|---|---|---|---|---|---|
| 6-11 months | 7-15%E | 30-45%E | 45-60%E | no recommendation | |
| 1-2 years | 10-15%E | 30-40%E | 45-60%E | free sugars <5%E | |
| >=2 years & adults | 10-20%E | 25-40%E | 45-60%E | women >=25g, men >=35g | adults: protein 18-20%E on a lower-energy diet |
| (general notes) | | saturated fat <=10%E; cis-mono/polyunsaturated >=2/3 of total fat | prefer >=50%E; children formula age+7 g; adults ~12.5g/1000kcal | min 3%E omega-6, min 0.5%E omega-3 | |

## Table 13.1 (p.27) — food-group portions per day, by energy level, 1000-2200 kcal

kcal/portion column = the group's or item's approximate energy content per portion (from Table 16, cross-referenced).

| Food group / item | kcal/portion | 1000 | 1200 | 1400 | 1600 | 1800 | 2000 | 2200 |
|---|---|---|---|---|---|---|---|---|
| **VEGETABLES, FRUITS & BERRIES (total)** | | >=4 | >=5 | >=5 | >=6 | >=6 | >=7 | >=8 |
| Vegetables | 30 | >=2 | >=2 | >=3 | >=3 | >=4 | >=4 | >=5 |
| Legumes | 130 | 0.2 | 0.3 | 0.3 | 0.3 | 0.3 | 0.5 | 0.6 |
| Fruits | 50 | >=2 | >=2 | >=2 | >=2 | >=2 | >=2 | >=2 |
| Berries | 50 | >=0.3 | >=0.3 | >=0.3 | >=0.3 | >=0.4 | >=0.4 | >=0.4 |
| **GRAIN PRODUCTS & POTATOES (total)** | | 5-6 | 5-6 | 6-7 | 7-8 | 9-10 | 9-10 | (gap in extraction) |
| High-fibre bread/baked goods | 75 | 1-2 | 2-3 | 2-3 | 3-4 | 3-4 | 4-5 | 4-5 |
| Porridges, pasta, grain products | - | 1-2 | 2-3 | 2-3 | 2-3 | 2-3 | 3-4 | 3-4 |
| Potato, sweet potato | - | 0.5 | 0.5-1 | 1 | 1 | 1-2 | 1-2 | 1-2 |
| **DAIRY PRODUCTS (total)** | 110 | 1-2 | 1-2 | 2 | 2-3 | 2-3 | 2-3 | 2-3 |
| **NUTS, SEEDS, OILS & FATS (total)** | | 3-4 | 3-4 | 3-4 | 5-6 | 5-6 | 5-6 | 6-7 |
| Nuts | 90 | 0.5-1 | 0.5-1 | 0.5-1 | 1-2 | 1-2 | 1-2 | 2-3 |
| Seeds, cocoa | 50 | 0.2 | 0.2 | 0.2 | 0.3 | 0.3 | 0.5 | 0.5 |
| Oils/fats/spreads | - | 2-3 | 2-3 | 2-3 | 3-4 | 3-4 | 3-4 | 3-4 |
| **FISH, EGGS & MEAT (total)** | | 2 | 2-3 | 2-3 | 3 | 3-4 | 3-4 | 3-4 |
| Fish & seafood | 80 | 0.5-1 | 0.5-1.5 | 1-1.5 | 1-1.5 | 1-2 | 1-2 | 1-2 |
| Eggs | - | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Poultry | - | 0.4 | 0.5 | 0.6 | 0.7 | 0.9 | 1 | 1 |
| Red meat | - | 0.3 | 0.3 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| **SWEETS/SNACKS/DISCRETIONARY** | 40 | <=1 | <=1 | <=2 | <=2 | <=3 | <=4 | <=4 |

## Table 13.2 (p.28-29) — food-group portions per day, by energy level, 2400-3600 kcal

| Food group / item | kcal/portion | 2400 | 2600 | 2800 | 3000 | 3200 | 3400 | 3600 |
|---|---|---|---|---|---|---|---|---|
| **VEGETABLES, FRUITS & BERRIES (total)** | | >=8 | >=10 | >=11 | >=11 | >=12 | >=13 | >=14 |
| Vegetables | 30 | >=5 | >=6 | >=6 | >=7 | >=7 | >=8 | >=8 |
| Legumes | 130 | 0.6 | 0.7 | 0.7 | 0.8 | 0.8 | 0.9 | 0.9 |
| Fruits | 50 | >=2 | >=3 | >=3 | >=3 | >=3 | >=3 | >=4 |
| Berries | 50 | >=0.4 | >=0.5 | >=0.5 | >=0.6 | >=0.6 | >=0.7 | >=0.7 |
| **GRAIN PRODUCTS & POTATOES (total)** | | 11-12 | 12-13 | 12-13 | 13-14 | 14-15 | 15-16 | 16-17 |
| High-fibre bread/baked goods | 75 | 5-6 | 5-6 | 5-6 | 6-7 | 6-7 | 7-8 | 7-8 |
| Porridges, pasta, kama etc | - | 3-5 | 4-5 | 4-5 | 5-6 | 5-6 | 5-6 | 6-7 |
| Potato, sweet potato | - | 2 | 2 | 2-3 | 2-3 | 2-3 | 2-3 | 2-3 |
| **DAIRY PRODUCTS (total)** | 110 | 2-3 | 2-3 | 3-4 | 3-4 | 3-4 | 3-4 | 4-5 |
| **NUTS, SEEDS, OILS & FATS (total)** | | 7-8 | 8-9 | 8-9 | 9-10 | 10-11 | 11-12 | 11-12 |
| Nuts | 90 | 2-3 | 2-3 | 2-3 | 2-3 | 3-4 | 3-4 | 3-4 |
| Seeds, cocoa | 50 | 0.5 | 0.5 | 0.6 | 0.7 | 0.7 | 0.8 | 1 |
| Oils/butter/spreads | - | 4-5 | 5-6 | 5-6 | 6-7 | 6-7 | 7-8 | 7-8 |
| **FISH, EGGS & MEAT (total)** | | 4-5 | 4-5 | 4-5 | 4-5 | 4-5 | 4-5 | 4-5 |
| Fish & seafood | 80 | 1-2 | 1-2 | 1-2 | 1-2 | 1-2 | 1-2 | 1-2 |
| Eggs | - | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Poultry | - | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Red meat | - | <=0.6 | <=0.6 | <=0.6 | <=0.6 | <=0.6 | <=0.6 | <=0.6 |
| **SWEETS/SNACKS/DISCRETIONARY** | 40 | <=4 | <=5 | <=5 | <=5 | <=6 | <=6 | <=6 |

## Table 16 — kcal per portion, by food group (portion size definitions)

| Item | kcal/portion |
|---|---|
| Vegetables | 30 |
| Legumes | 130 |
| Fruits | 50 |
| Berries | 50 |
| Nuts | 90 |
| Seeds, cocoa | 50 |
| Fish/seafood | 80 |
| Eggs | 80 |
| Poultry | 80 |
| Red meat | 80 |
| Grain products & potatoes | 75 |
| Oils/fats/spreads | 50 |
| Dairy | 110 |
| Sweets/snacks/discretionary | 40 |

Document also notes portions should be counted in "puhaskaal" (net weight, e.g. vegetables without peel), and that household-measure gram equivalents given in the PDF are approximate.

**Resolved in Phase 3**: the full gram-weight breakdown (Tables 16.1 through 16.6, one sub-table per
pyramid food group) was retrieved by rendering the PDF through Google's Docs viewer in a real
browser (Chrome's own PDF viewer isn't reachable by browser automation, and WebFetch's PDF-to-text
conversion silently truncates this document somewhere around page 26-29 — neither gave access to
page 36+ where Table 16 lives). Every item's gram weight (or gram range) per portion, by pyramid
food group, is now in `data/raw/tai/tabelraamat_table16_portion_grams.csv` (78 rows) — this is what
lets Phase 3 convert recommended portions/day into grams/day, and eventually into tonnes/year
comparable with Statistikaamet's production data.

## What this gives the model (Section 5.1/5.2 of PLAN.md)
1. Table 4+5 → maps every age x sex x activity-level cell to a daily kcal requirement.
2. Table 13.1+13.2 → maps a daily kcal level to recommended portions per food group (and sub-item).
3. Table 16 → converts portions to kcal (and, once gram weights are confirmed, to grams) per food group/item.
Chaining 1->2->3 turns the demographic population grid directly into a national recommended-demand-by-food-group total (Section 5.1), the core of the "if everyone ate as recommended" scenario.

## Still needed from this source
- ~~Gram weights per portion for oils/fats, eggs, poultry, red meat, potato, grain items~~ — resolved, see above.
- ~~The men >70 y row in Table 5~~ — resolved, see above.
- Confirm whether a newer/updated table exists for pregnant/nursing beyond the two rows captured. (Not blocking for Phase 3 — pregnant/nursing are out of the canonical demographic grid's scope, same as infants.)
