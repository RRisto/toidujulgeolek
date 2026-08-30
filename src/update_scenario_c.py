#!/usr/bin/env python3
"""
Phase 10 (post-launch): joins the Scenario C (EAT-Lancet) demand crosswalk onto
scenario_comparison.csv and critical_dependency_flags.csv, computing Scenario C
self-sufficiency the same way Scenario B was computed (Phase 7):

    scenario_C_pct = scenario_A_pct * (scenario_A_demand_tonnes / scenario_C_demand_tonnes)

Only applied where scenario_A_pct is a resolved single number and scenario_A_demand_tonnes
exists -- rows with a range/bimodal/gap baseline (porridge, legumes, nuts+seeds, sweets/sugar)
keep the same qualitative treatment Scenario B already uses, per the project's standing rule
against forcing false precision onto an unresolved figure.
"""
import csv

POPULATION = 1339785.0

def load_crosswalk():
    cw = {}
    with open("data/crosswalk/eatlancet_crosswalk.csv", encoding="utf-8") as f:
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

    new_fieldnames = fieldnames[:4] + ["scenario_C_demand_tonnes_per_year",
                                        "demand_change_ratio_C_over_A",
                                        "scenario_C_self_sufficiency_pct"] + fieldnames[4:]
    # insert scenario_C columns right after scenario_B_self_sufficiency_pct block for readability:
    # actual desired order: ... demand_change_ratio_B_over_A, scenario_A_self_sufficiency_pct,
    # scenario_B_self_sufficiency_pct, scenario_C_demand_tonnes_per_year,
    # demand_change_ratio_C_over_A, scenario_C_self_sufficiency_pct, waste levers..., data_status, note
    idx_after_B_pct = fieldnames.index("scenario_B_self_sufficiency_pct") + 1
    new_fieldnames = (fieldnames[:idx_after_B_pct]
                       + ["scenario_C_demand_tonnes_per_year", "demand_change_ratio_C_over_A",
                          "scenario_C_self_sufficiency_pct"]
                       + fieldnames[idx_after_B_pct:])

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        entry = cw.get(key)
        c_g = entry["g_per_day"] if entry else None
        c_tonnes = tonnes(c_g)
        a_tonnes = to_float(row["scenario_A_demand_tonnes_per_year"])
        a_pct = to_float(row["scenario_A_self_sufficiency_pct"])

        row["scenario_C_demand_tonnes_per_year"] = c_tonnes if c_tonnes is not None else ""

        if c_tonnes and a_tonnes:
            ratio = round(c_tonnes / a_tonnes, 4)
            row["demand_change_ratio_C_over_A"] = ratio
        else:
            row["demand_change_ratio_C_over_A"] = ""

        if a_pct is not None and c_tonnes and a_tonnes:
            c_pct = round(a_pct * (a_tonnes / c_tonnes), 1)
            row["scenario_C_self_sufficiency_pct"] = c_pct
        elif row["scenario_A_self_sufficiency_pct"] in (
                "~0% assumed",
                "~0% (raw sugar) / not scoreable (manufactured)"):
            # structural near-zero rows: stays ~0% regardless of demand scaling, same logic as B
            row["scenario_C_self_sufficiency_pct"] = row["scenario_A_self_sufficiency_pct"]
        elif "bimodal" in str(row["scenario_A_self_sufficiency_pct"]):
            row["scenario_C_self_sufficiency_pct"] = row["scenario_A_self_sufficiency_pct"]
        elif "wide, unresolved" in str(row["scenario_A_self_sufficiency_pct"]):
            row["scenario_C_self_sufficiency_pct"] = (
                "proportionally different from the Scenario A range (see demand_change_ratio_C_over_A) "
                "-- not stated as a number since the Scenario A range itself has no resolved point estimate")
        elif row["pyramid_group"] == "Nuts, seeds, oils & fats" and row["subitem"] == "Oils/fats/spreads (sunflower, 0%)":
            row["scenario_C_self_sufficiency_pct"] = "0.0"
        elif row["pyramid_group"] == "Nuts, seeds, oils & fats" and row["subitem"] == "Oils/fats/spreads (soy, 0%)":
            row["scenario_C_self_sufficiency_pct"] = "0.0"
        else:
            row["scenario_C_self_sufficiency_pct"] = ""

    with open("data/processed/scenario_comparison.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=new_fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print("scenario_comparison.csv updated with Scenario C columns")
    for row in rows:
        print(f"  {row['pyramid_group']} / {row['subitem']}: A={row['scenario_A_self_sufficiency_pct']} "
              f"B={row['scenario_B_self_sufficiency_pct']} C={row['scenario_C_self_sufficiency_pct']} "
              f"(C demand={row['scenario_C_demand_tonnes_per_year']}t, ratio={row['demand_change_ratio_C_over_A']})")

if __name__ == "__main__":
    main()
