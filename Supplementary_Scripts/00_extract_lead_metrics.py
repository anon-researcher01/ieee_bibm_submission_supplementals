"""
00_extract_lead_metrics.py
Extracts per-lead BindCraft Rosetta metrics for the five characterized leads
from the BindCraft per-design statistics CSVs (no GPU or re-prediction required).

Outputs: Supplementary_S4_lead_metrics.csv

Usage:
    python 00_extract_lead_metrics.py \
        --p19  final_design_stats_p19.csv \
        --full final_design_stats.csv \
        --out  Supplementary_S4_lead_metrics.csv
"""

import argparse
import pandas as pd

LEADS = [
    "il23_l94_s482991_mpnn8",
    "il23_l104_s309115_mpnn6",
    "il23_l72_s467308_mpnn8",
    "il23_l92_s675453_mpnn18",
    "il23_l83_s957191_mpnn2",
]

# p19-only leads drawn from p19 stats; full-heterodimer leads from full stats
LEAD_REGIME = {
    "il23_l94_s482991_mpnn8":   "p19",
    "il23_l104_s309115_mpnn6":  "p19",
    "il23_l72_s467308_mpnn8":   "p19",
    "il23_l92_s675453_mpnn18":  "full",
    "il23_l83_s957191_mpnn2":   "full",
}

COLUMNS = [
    "Average_Hotspot_RMSD",
    "Average_i_pTM",
    "Average_pTM",
    "Average_i_pAE",
    "Average_Binder_pLDDT",
    "Average_dG",
    "Average_dSASA",
    "Average_ShapeComplementarity",
    "Average_n_InterfaceHbonds",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p19",  default="final_design_stats_p19.csv")
    ap.add_argument("--full", default="final_design_stats.csv")
    ap.add_argument("--out",  default="Supplementary_S4_lead_metrics.csv")
    args = ap.parse_args()

    df_p19  = pd.read_csv(args.p19,  index_col="Design")
    df_full = pd.read_csv(args.full, index_col="Design")

    rows = []
    for lead in LEADS:
        src = df_p19 if LEAD_REGIME[lead] == "p19" else df_full
        if lead not in src.index:
            raise ValueError(f"Lead '{lead}' not found in {args.p19 if LEAD_REGIME[lead]=='p19' else args.full}")
        missing = [c for c in COLUMNS if c not in src.columns]
        if missing:
            print(f"WARNING: columns not found in source CSV: {missing}")
        row = {"Design": lead}
        for col in COLUMNS:
            row[col] = src.loc[lead, col] if col in src.columns else None
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"Wrote {len(out)} rows to {args.out}")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
