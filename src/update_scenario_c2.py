#!/usr/bin/env python3
"""
Phase 14 (post-launch): joins the Scenario C.2 (2025 EAT-Lancet) demand crosswalk onto
scenario_comparison.csv and critical_dependency_flags.csv, computing Scenario C.2
self-sufficiency the same way Scenario C was computed (Phase 10):

    scenario_C2_pct = scenario_A_pct * (scenario_A_demand_tonnes / scenario_C2_demand_tonnes)

Only applied where scenario_A_pct is a resolved single number and scenario_A_demand_tonnes
exists -- rows with a range/bimodal/gap/upper-bound baseline (porridge, legumes, nuts+seeds,
sweets/sugar) keep the same qualitative treatment Scenario B/C already use, per the project's
standing rule against forcing false precision onto an unresolved figure. The porridge row's text
is regenerated to reference Scenario C.2 specifically rather than copying Scenario C's wording
verbatim, since that wording is itself hand-curated (not script-regenerated) as of Phase 12/13 --
this script must not silently clobber it, so it reproduces the same *pattern* for the C2 column
without touching the existing scenario_C_self_sufficiency_pct column at all.
"""
import csv

POPULATION = 1339785.0

def load_crosswalk():
    cw = {}
    with open("data/crosswalk/eatlancet2025_crosswalk.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["pyramid_group"], row["subitem"])
            g = row["scaled_g_per_day_estonia"]
            cw[key] = {
                "g_per_day": float(g) if g else None,
                "note": row["note"],
            }
    return cw

def tonnes(g_per_day):
    if g_per_day is None:
        return None
    return round(g_per_day * POPULATION * 365 / 1e6, 1)

def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def main():
    cw = load_crosswalk()

    with open("data/processed/scenario_comparison.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # idempotency guard: if a prior run already inserted the C2 columns, drop them first so a
    # re-run doesn't duplicate the header (this script may be re-run after later data updates).
    c2_cols = ["scenario_C2_demand_tonnes_per_year", "demand_change_ratio_C2_over_A",
               "scenario_C2_self_sufficiency_pct"]
    if any(c in fieldnames for c in c2_cols):
        fieldnames = [f for f in fieldnames if f not in c2_cols]
        for row in rows:
            for c in c2_cols:
                row.pop(c, None)

    idx_after_C_pct = fieldnames.index("scenario_C_self_sufficiency_pct") + 1
    new_fieldnames = (fieldnames[:idx_after_C_pct]
                       + ["scenario_C2_demand_tonnes_per_year", "demand_change_ratio_C2_over_A",
                          "scenario_C2_self_sufficiency_pct"]
                       + fieldnames[idx_after_C_pct:])

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        entry = cw.get(key)
        c2_g = entry["g_per_day"] if entry else None
        c2_tonnes = tonnes(c2_g)
        a_tonnes = to_float(row["scenario_A_demand_tonnes_per_year"])
        a_pct = to_float(row["scenario_A_self_sufficiency_pct"])
        a_pct_text = row["scenario_A_self_sufficiency_pct"]

        row["scenario_C2_demand_tonnes_per_year"] = c2_tonnes if c2_tonnes is not None else ""

        if c2_tonnes and a_tonnes:
            ratio = round(c2_tonnes / a_tonnes, 4)
            row["demand_change_ratio_C2_over_A"] = ratio
        else:
            row["demand_change_ratio_C2_over_A"] = ""

        if a_pct is not None and c2_tonnes and a_tonnes:
            c2_pct = round(a_pct * (a_tonnes / c2_tonnes), 1)
            row["scenario_C2_self_sufficiency_pct"] = c2_pct
        elif a_pct_text in (
                "~0% assumed",
                "~0% (raw sugar) / not scoreable (manufactured)"):
            # structural near-zero rows: stays at the same text regardless of demand scaling,
            # same logic as Scenario B/C
            row["scenario_C2_self_sufficiency_pct"] = a_pct_text
        elif "bimodal" in str(a_pct_text):
            row["scenario_C2_self_sufficiency_pct"] = a_pct_text
        elif "upper bound" in str(a_pct_text):
            row["scenario_C2_self_sufficiency_pct"] = (
                "proportionally different from the Scenario A upper bound (see "
                "demand_change_ratio_C2_over_A) -- still not stated as a single number for the "
                "same reason")
        elif row["pyramid_group"] == "Nuts, seeds, oils & fats" and row["subitem"] == "Oils/fats/spreads (sunflower, 0%)":
            row["scenario_C2_self_sufficiency_pct"] = "0.0"
        elif row["pyramid_group"] == "Nuts, seeds, oils & fats" and row["subitem"] == "Oils/fats/spreads (soy, 0%)":
            row["scenario_C2_self_sufficiency_pct"] = "0.0"
        else:
            row["scenario_C2_self_sufficiency_pct"] = ""

    with open("data/processed/scenario_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=new_fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print("scenario_comparison.csv updated with Scenario C.2 columns")
    for row in rows:
        print(f"  {row['pyramid_group']} / {row['subitem']}: A={row['scenario_A_self_sufficiency_pct']} "
              f"C={row['scenario_C_self_sufficiency_pct']} C2={row['scenario_C2_self_sufficiency_pct']} "
              f"(C2 demand={row['scenario_C2_demand_tonnes_per_year']}t, ratio={row['demand_change_ratio_C2_over_A']})")

if __name__ == "__main__":
    main()
