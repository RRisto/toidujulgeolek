#!/usr/bin/env python3
"""
Phase 14 (post-launch): adds Scenario C.2 (2025 EAT-Lancet) columns to
critical_dependency_flags.csv, mirroring the Scenario C flag logic from Phase 10 (50% threshold
check, and a "worsens" flag for any item Scenario C.2 makes worse relative to Scenario A
regardless of threshold).
"""
import csv

def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def main():
    # pull scenario_C2 figures back out of the just-updated scenario_comparison.csv
    sc = {}
    with open("data/processed/scenario_comparison.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["pyramid_group"], row["subitem"])
            sc[key] = row["scenario_C2_self_sufficiency_pct"]

    with open("data/processed/critical_dependency_flags.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # idempotency guard: drop any previously-inserted C2 columns before reinserting, so a re-run
    # doesn't duplicate the header.
    c2_cols = ["scenario_C2_self_sufficiency_pct", "flag_below_50pct_scenario_C2",
               "flag_scenario_C2_worsens_dependency"]
    if any(c in fieldnames for c in c2_cols):
        fieldnames = [f for f in fieldnames if f not in c2_cols]
        for row in rows:
            for c in c2_cols:
                row.pop(c, None)

    idx_pct = fieldnames.index("scenario_C_self_sufficiency_pct") + 1
    idx_flag = fieldnames.index("flag_scenario_C_worsens_dependency") + 1

    new_fieldnames = (fieldnames[:idx_pct]
                       + ["scenario_C2_self_sufficiency_pct"]
                       + fieldnames[idx_pct:idx_flag]
                       + ["flag_below_50pct_scenario_C2", "flag_scenario_C2_worsens_dependency"]
                       + fieldnames[idx_flag:])

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        c2_val_raw = sc.get(key, "")
        row["scenario_C2_self_sufficiency_pct"] = c2_val_raw

        c2_val = to_float(c2_val_raw)
        if c2_val is not None:
            row["flag_below_50pct_scenario_C2"] = "Y" if c2_val < 50 else "N"
        else:
            row["flag_below_50pct_scenario_C2"] = "N/A"

        a_val = to_float(row["scenario_A_self_sufficiency_pct"])
        if a_val is not None and c2_val is not None:
            row["flag_scenario_C2_worsens_dependency"] = "Y" if c2_val < a_val else "N"
        else:
            row["flag_scenario_C2_worsens_dependency"] = "N/A"

    with open("data/processed/critical_dependency_flags.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=new_fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print("critical_dependency_flags.csv updated with Scenario C.2 columns")
    for row in rows:
        print(f"  {row['pyramid_group']} / {row['subitem']}: C2={row['scenario_C2_self_sufficiency_pct']} "
              f"below50_C2={row['flag_below_50pct_scenario_C2']} worsens_C2={row['flag_scenario_C2_worsens_dependency']}")

if __name__ == "__main__":
    main()
