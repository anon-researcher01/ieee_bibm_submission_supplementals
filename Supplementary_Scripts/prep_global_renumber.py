#!/usr/bin/env python3
"""
Prepare ColabFold complex PDBs for AF2-initial-guess.
Keeps 3 chains (A=binder, B=p40, C=p19) but renumbers residues GLOBALLY
and continuously (1..N) so indices are unique across the whole structure.
Non-unique per-chain numbering was causing AF2 to produce garbage.
The distance-based chain-break detector in predict.py finds the real
breaks (binder->p40, p40->p19, internal 3DUH gaps) on its own.
"""
import sys

def renumber_global(in_path, out_path):
    out_lines = []
    resnum = 0
    last_key = None
    last_chain = None
    for line in open(in_path):
        if not line.startswith(("ATOM", "HETATM")):
            continue
        chain = line[21]
        key = (chain, line[22:26], line[26])  # chain, resSeq, iCode
        if key != last_key:
            resnum += 1
            last_key = key
        # Insert TER when chain changes
        if last_chain is not None and chain != last_chain:
            out_lines.append("TER\n")
        last_chain = chain
        # Columns: 23-26 resSeq (4 chars), 27 iCode -> clear it
        new = line[:22] + f"{resnum:4d}" + " " + line[27:]
        out_lines.append(new)
    out_lines.append("TER\nEND\n")
    with open(out_path, "w") as f:
        f.writelines(out_lines)
    return resnum

if __name__ == "__main__":
    n = renumber_global(sys.argv[1], sys.argv[2])
    print(f"Wrote {sys.argv[2]} with {n} residues, globally renumbered")
