import os, glob, json, csv, subprocess

OUTDIR = "p40_out"
IPSAE_PY = "/path/to/project/IPSAE/ipsae.py"
PAE_CUTOFF = 10
DIST_CUTOFF = 10
LEADS = ["l72", "l83", "l92", "l94", "l104"]

def parse_ipsae_txt(txt):
    vals = []
    with open(txt) as f:
        header = None
        for line in f:
            parts = line.split()
            if parts:
                header = parts
                break
        if header is None or "ipSAE" not in header:
            return 0.0
        c = header.index("ipSAE")
        for line in f:
            parts = line.split()
            if len(parts) > c:
                try:
                    vals.append(float(parts[c]))
                except Exception:
                    pass
    return max(vals) if vals else 0.0

rows = []

for lead in LEADS:
    pdbs = sorted(glob.glob(os.path.join(OUTDIR, f"{lead}_p40*rank_001*.pdb")))
    js_files = sorted(glob.glob(os.path.join(OUTDIR, f"{lead}_p40*scores_rank_001*.json")))

    if not pdbs or not js_files:
        rows.append({"lead": lead, "ipSAE_p40": "NA", "ipTM_p40": "NA"})
        continue

    pdb = pdbs[0]
    js = js_files[0]

    subprocess.run(
        ["python", IPSAE_PY, js, pdb, str(PAE_CUTOFF), str(DIST_CUTOFF)],
        check=True
    )

    ipsae_txt = f"{os.path.splitext(pdb)[0]}_{PAE_CUTOFF}_{DIST_CUTOFF}.txt"
    ipsae = parse_ipsae_txt(ipsae_txt)

    with open(js) as f:
        scores = json.load(f)

    iptm = scores.get("iptm", scores.get("ipTM", None))

    rows.append({
        "lead": lead,
        "ipSAE_p40": round(float(ipsae), 3),
        "ipTM_p40": round(float(iptm), 4) if iptm is not None else "NA"
    })

with open("p40_selectivity.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["lead", "ipSAE_p40", "ipTM_p40"])
    w.writeheader()
    w.writerows(rows)

print(open("p40_selectivity.csv").read())
