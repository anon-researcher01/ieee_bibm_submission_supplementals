# ieee_bibm_submission_supplementals: Supplementary Data

Supplementary materials for:

> Anonymous, "Computational De Novo Design of Miniprotein Candidate
> Neutralizers Targeting the IL-23 Cytokine Subunit p19," IEEE BIBM 2026.

---

## Data files

| File | Description | Backs |
|------|-------------|-------|
| `Supplementary_S1_sequences.fasta` | All 50 BindCraft Accepted binder sequences; five leads marked `LEAD*` | §IV-C, Table II |
| `Supplementary_S2_seed_table.csv` | 42 p19-only designs mapped to 23 distinct backbone seeds, with per-seed sequence count and best ipSAE | §IV-C ("23 independent design seeds") |
| `Supplementary_S3_p40_selectivity.csv` | Full 5-model/3-recycle p40 counter-screen results for the five leads | Table III |
| `Supplementary_S4_lead_metrics.csv` | Complete Table II mirror: all columns including ipSAE, minPAE, RMSD, hotspots, %helix, ΔG, dSASA, SC, HB, contacts | Table II |
| `Supplementary_S5_conventional_972_scores.tsv` | AF2-initial-guess ipSAE scores for all 972 conventional designs; backs the 0/972 central negative result | §IV-B, Fig. 3 |
| `Supplementary_S6_colabfold_artifact.tsv` | Paired single-sequence ColabFold vs AF2-initial-guess pLDDT for 50 matched designs; backs the 56-point artifact claim | §IV-A, Fig. 2 |
| `Supplementary_S7_top50_p19_p40_scores.tsv` | Top-50 curated conventional designs rescored against both p19 and p40 | §IV-B ("best p19 0.235, best p40 0.147") |

## Scripts

See `Supplementary_Scripts/README.md` for run order, prerequisites, and
the mapping from each script to the data file it produced.

## Reproducing key numbers

| Claim | File | Check |
|-------|------|-------|
| 0/972 ≥ 0.60 ipSAE (conventional) | S5 | count rows with ipSAE_p19 ≥ 0.60 |
| Best conventional ipSAE 0.297 | S5 | max(ipSAE_p19) |
| 42/50 ≥ 0.60 (BindCraft) | S1 | count headers with ipSAE ≥ 0.60 |
| 23 independent seeds | S2 | count rows |
| ColabFold under-rates by ~56 pts | S6 | mean(plddt_delta) |
| All five leads ipSAE_p40 = 0.00 | S3 | read directly |

Raw AF2 prediction files and BindCraft trajectory outputs are available
from the authors on request.
