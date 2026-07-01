#!/usr/bin/env python3
"""
leads_vs_p40.py  --  Priority 1: score the 5 leads against p40 ALONE with ipSAE.

Two modes:
  build    -> writes one ColabFold FASTA per lead: binder : p40   (binder+p40 complex)
  collect  -> runs ipSAE on each ColabFold prediction and writes p40_selectivity.csv

Run order on the institutional HPC cluster:
  python leads_vs_p40.py build          # make FASTAs
  colabfold_batch  p40_inputs/  p40_out/   (done by the sbatch, see run_p40_the institutional HPC cluster.sbatch)
  python leads_vs_p40.py collect        # ipSAE + table

Expected (if selective): every lead's p40 ipSAE sits far below 0.60, near the
conventional p40 best of 0.147, while its p19 ipSAE (Table I) stays 0.76-0.80.
"""
import argparse, glob, json, os, subprocess
import pandas as pd
from Bio.PDB import PDBParser, PPBuilder

# ---- CONFIG ---------------------------------------------------------------
P19_CSV  = "final_design_stats_p19.csv"
FULL_CSV = "final_design_stats.csv"
SEQ_COL  = "Sequence"          # confirmed column name in your BindCraft CSVs

# p40 sequence. EASIEST: paste UniProt IL12B (P29460) mature chain here.
# Or leave blank and set PDB_3DUH to extract chain A (the exact p40 you targeted).
P40_SEQ   = "IWELKKDVYVVELDWYPDAPGEMVVLTCDTPEEDGITWTLDQSSEVLGSGKTLTIQVKEFGDAGQYTCHKGGEVLSHSLLLLHKKEDGIWSTDILKDQKEPKNKTFLRCEAKNYSGRFTCWWLTTISTDLTFSVKSSRGSSDPQGVTCGAATLSAERVRGDNKEYEYSVECQEDSACPAAEESLPIEVMVDAVHKLKYENYTSSFFIRDIIKPDPPKNLQLKPLKNSRQVEVSWEYPDTWSTPHSYFSLTFCVQVQGKSKREKKDRVFTDKTSATVICRKNASISVRAQDRYYSSSWSEWASVPCS"
PDB_3DUH  = "3duh.pdb"
P40_CHAIN = "A"

IPSAE_PY    = "/path/to/project/IPSAE/ipsae.py"        # path to reference ipsae.py (or your own script)
PAE_CUTOFF  = 10
DIST_CUTOFF = 10

LEADS = {
    "il23_l94_s482991_mpnn8":  "l94",
    "il23_l104_s309115_mpnn6": "l104",
    "il23_l72_s467308_mpnn8":  "l72",
    "il23_l92_s675453_mpnn18": "l92",
    "il23_l83_s957191_mpnn2":  "l83",
}
INDIR  = "p40_inputs"
OUTDIR = "p40_out"
# ---------------------------------------------------------------------------


def chain_seq(pdb, chain):
    s = PDBParser(QUIET=True).get_structure("x", pdb)
    ppb = PPBuilder()
    return "".join(str(p.get_sequence()) for p in ppb.build_peptides(s[0][chain]))


def lead_sequences():
    df = pd.concat([pd.read_csv(P19_CSV), pd.read_csv(FULL_CSV)], ignore_index=True)
    df = df[df["Design"].isin(LEADS)].set_index("Design")
    return {LEADS[d]: df.loc[d, SEQ_COL] for d in LEADS}


def build():
    os.makedirs(INDIR, exist_ok=True)
    p40 = P40_SEQ.strip() or chain_seq(PDB_3DUH, P40_CHAIN)
    if not p40:
        raise SystemExit("No p40 sequence: set P40_SEQ or provide 3duh.pdb.")
    for short, bseq in lead_sequences().items():
        with open(os.path.join(INDIR, f"{short}_p40.fasta"), "w") as fh:
            fh.write(f">{short}_p40\n{bseq}:{p40}\n")   # ':' joins chains for a complex
    print(f"wrote {len(LEADS)} FASTAs to {INDIR}/  (binder : p40)")


def ipsae_max(pdb, pae_json):
    subprocess.run(["python", IPSAE_PY, pae_json, pdb,
                    str(PAE_CUTOFF), str(DIST_CUTOFF)], check=True)
    txt = f"{os.path.splitext(pdb)[0]}_{PAE_CUTOFF}_{DIST_CUTOFF}.txt"
    vals = []
    with open(txt) as fh:
        hdr = None
        for line in fh:
            parts = line.split()
            if parts:
                hdr = parts
                break
        if hdr is None:
            return 0.0
        c = hdr.index("ipSAE") if "ipSAE" in hdr else None
        for line in fh:
            parts = line.split()
            if c is not None and len(parts) > c:
                try:
                    vals.append(float(parts[c]))
                except ValueError:
                    pass
    return max(vals) if vals else 0.0


def collect():
    rows = []
    for short in LEADS.values():
        pdb  = sorted(glob.glob(os.path.join(OUTDIR, f"{short}_p40*rank_001*.pdb")))
        js   = sorted(glob.glob(os.path.join(OUTDIR, f"{short}_p40*scores_rank_001*.json")))
        if not pdb or not js:
            print(f"  missing output for {short}"); rows.append(dict(lead=short, ipSAE_p40=None, ipTM_p40=None)); continue
        with open(js[0]) as fh: sc = json.load(fh)
        rows.append(dict(lead=short,
                         ipSAE_p40=round(ipsae_max(pdb[0], js[0]), 3),
                         ipTM_p40=sc.get("iptm")))
    out = pd.DataFrame(rows)
    out.to_csv("p40_selectivity.csv", index=False)
    print(out.to_string(index=False))
    print("\nSend p40_selectivity.csv back. Selective if every ipSAE_p40 << 0.60.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "collect"])
    a = ap.parse_args()
    build() if a.mode == "build" else collect()
