#!/usr/bin/env python3
"""
rosetta_conventional.py
Computes AlphaFold-independent interface geometry for the top-ranked conventional
(RFdiffusion/ProteinMPNN) designs, providing a check on the pipeline contrast
that uses no AlphaFold-derived quantity.

Ranks designs by ipSAE from full_screen_ipsae.tsv, selects the highest-ranked
designs with retained AlphaFold-initial-guess structures, and records buried
interface area (dSASA), shape complementarity, and interface hydrogen bonds with
the Rosetta InterfaceAnalyzerMover.

Chain A = designed binder; chain B = target (p40+p19 merged).

Rosetta dG is deliberately not reported: AlphaFold outputs are not
energy-minimized, so an unrelaxed dG reflects structural strain rather than
binding and is not comparable to BindCraft's post-relaxation values.

Outputs: Supplementary_S8_conventional_rosetta_geometry.csv

Usage:
    python rosetta_conventional.py --topn 20 \
        --tsv full_screen_ipsae.tsv --pdbdir il23_ig_full_out \
        --out Supplementary_S8_conventional_rosetta_geometry.csv
"""
import os, sys, csv, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--tsv",     default="full_screen_ipsae.tsv")
ap.add_argument("--pdbdir",  default="il23_ig_full_out")
ap.add_argument("--pattern", default="il23_option_c_{id}_af2pred.pdb")
ap.add_argument("--topn",    type=int, default=20)
ap.add_argument("--out",     default="Supplementary_S8_conventional_rosetta_geometry.csv")
a = ap.parse_args()

rows = []
with open(a.tsv) as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        try:
            rows.append((r["design"].strip(), float(r["ipSAE_p19"]),
                         int(float(r["binder_len"]))))
        except (KeyError, ValueError):
            continue
rows.sort(key=lambda x: -x[1])

sel, missing = [], 0
for did, ipsae, blen in rows:
    p = os.path.join(a.pdbdir, a.pattern.format(id=did))
    if os.path.exists(p):
        sel.append((did, ipsae, blen, p))
        if len(sel) >= a.topn:
            break
    else:
        missing += 1

print(f"Ranked {len(rows)} designs; selected top {len(sel)} with retained "
      f"structures ({missing} higher-ranked designs had no structure on disk).")
if not sel:
    sys.exit("no structures matched")
print(f"ipSAE range of selected set: {sel[-1][1]:.3f}-{sel[0][1]:.3f}")

import pyrosetta
from pyrosetta import pose_from_pdb
from pyrosetta.rosetta.protocols.analysis import InterfaceAnalyzerMover

pyrosetta.init("-mute all -ignore_unrecognized_res "
               "-ignore_zero_occupancy false -detect_disulf false")

FIELDS = ["design", "ipSAE_p19", "binder_len", "dSASA_int",
          "shape_complementarity", "hbonds_int", "delta_unsatHbonds"]
out = []
for i, (did, ipsae, blen, path) in enumerate(sel, 1):
    try:
        pose = pose_from_pdb(path)
        ia = InterfaceAnalyzerMover("A_B")
        ia.set_pack_separated(True)
        ia.set_compute_interface_sc(True)
        ia.set_calc_dSASA(True)
        ia.apply(pose)
        d = ia.get_all_data()
        rec = dict(design=did, ipSAE_p19=ipsae, binder_len=blen,
                   dSASA_int=round(ia.get_interface_delta_sasa(), 1),
                   shape_complementarity=round(d.sc_value, 3),
                   hbonds_int=d.interface_hbonds,
                   delta_unsatHbonds=round(ia.get_interface_delta_hbond_unsat(), 1))
        out.append(rec)
        print(f"[{i}/{len(sel)}] {did}: dSASA={rec['dSASA_int']} "
              f"SC={rec['shape_complementarity']} HB={rec['hbonds_int']}")
    except Exception as exc:
        print(f"[{i}/{len(sel)}] {did}: FAILED ({type(exc).__name__}: {exc})")

with open(a.out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader(); w.writerows(out)
print(f"Wrote {len(out)} rows to {a.out}")
