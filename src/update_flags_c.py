#!/usr/bin/env python3
"""
Phase 10 (post-launch): adds Scenario C (EAT-Lancet) columns to critical_dependency_flags.csv,
mirroring the Scenario B flag logic from Phase 7 (50% threshold check, and a "worsens" flag for
any item Scenario C makes worse relative to Scenario A regardless of threshold).
"""
import csv

def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def main():
    # pull scenario_C figures back out of the just-updated scenario_comparison.csv
    sc = {}
    with open("data/processed/scenario_comparison.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["pyramid_group"], row["subitem"])
            sc[key] = row["scenario_C_self_sufficiency_pct"]

    with open("data/processed/critical_dependency_flags.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    idx = fieldnames.index("scenario_B_self_sufficiency_pct") + 1
    new_fieldnames = (fieldnames[:idx]
                       + ["scenario_C_self_sufficiency_pct"]
                       + fieldnames[idx:idx+1]  # feed_adjusted_low_bound_pct stays next
                       + ["flag_below_50pct_scenario_C", "flag_scenario_C_worsens_dependency"]
                       + fieldnames[idx+1:])
    # de-duplicate: the above double-includes feed_adjusted col if present; rebuild cleanly instead
    base = fieldnames[:idx]  # up to and incl. scenario_B_self_sufficiency_pct
    rest = fieldnames[idx:]  # feed_adjusted_low_bound_pct, flags..., reason
    new_fieldnames = base + ["scenario_C_self_sufficiency_pct"] + rest[:1] + \
                      ["flag_below_50pct_scenario_C", "flag_scenario_C_worsens_dependency"] + rest[1:]

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        c_val_raw = sc.get(key, "")
        row["scenario_C_self_sufficiency_pct"] = c_val_raw

        c_val = to_float(c_val_raw)
        if c_val is not None:
            row["flag_below_50pct_scenario_C"] = "Y" if c_val < 50 else "N"
        else:
            row["flag_below_50pct_scenario_C"] = "N/A"

        a_val = to_float(row["scenario_A_self_sufficiency_pct"])
        if a_val is not None and c_val is not None:
            row["flag_scenario_C_worsens_dependency"] = "Y" if c_val < a_val else "N"
        else:
            row["flag_scenario_C_worsens_dependency"] = "N/A"

    with open("data/processed/critical_dependency_flags.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=new_fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print("critical_dependency_flags.csv updated with Scenario C columns")
    for row in rows:
        print(f"  {row['pyramid_group']} / {row['subitem']}: C={row['scenario_C_self_sufficiency_pct']} "
              f"below50_C={row['flag_below_50pct_scenario_C']} worsens_C={row['flag_scenario_C_worsens_dependency']}")

if __name__ == "__main__":
    main()
