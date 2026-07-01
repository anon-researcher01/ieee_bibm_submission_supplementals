# Supplementary Scripts

Analysis and scoring scripts used to produce the supplementary data files for:

> Anonymous, "Computational De Novo Design of Miniprotein Candidate
> Neutralizers Targeting the IL-23 Cytokine Subunit p19," IEEE BIBM 2026.

All scripts were run on the the institutional HPC cluster
with NVIDIA A100 (40 GB) GPUs under SLURM.

---

## Script-to-data mapping

| Script | Produces | Notes |
|--------|----------|-------|
| `prep_global_renumber.py` | Preprocessed PDBs for AF2-initial-guess | Renumbers residues globally and continuously; required before `slurm_af2ig_full.sh` |
| `slurm_af2ig_full.sh` | AF2-initial-guess predictions for all 972 conventional designs | SLURM array job (4 chunks); output fed into ipSAE scoring to produce **S5** |
| `00_extract_lead_metrics.py` | `../Supplementary_S4_lead_metrics.csv` | Reads BindCraft per-design statistics CSVs; no GPU required |
| `leads_vs_p40.py build` | `p40_inputs/` FASTA files | Prepares one binder:p40 FASTA per lead for ColabFold |
| `run_p40_the institutional HPC cluster.sbatch` | ColabFold predictions in `p40_out/` | Submits 5-model/3-recycle ColabFold-Multimer jobs on the institutional HPC cluster |
| `collect_p40_robust.py` | `../Supplementary_S3_p40_selectivity.csv` | Parses ColabFold outputs, calls reference `ipsae.py`, writes S3 |

---

## Run order

### S5 — 972 conventional design scores
```bash
# 1. Renumber PDBs (run per-design or in a loop)
python prep_global_renumber.py input.pdb output.pdb

# 2. Run AF2-initial-guess as SLURM array
sbatch slurm_af2ig_full.sh

# 3. Score outputs with reference ipsae.py (Dunbrack lab) to produce S5
```

### S4 — Lead metrics
```bash
python 00_extract_lead_metrics.py \
    --p19  final_design_stats_p19.csv \
    --full final_design_stats.csv \
    --out  ../Supplementary_S4_lead_metrics.csv
```

### S3 — p40 counter-screen
```bash
# 1. Build per-lead FASTAs
python leads_vs_p40.py build

# 2. Submit ColabFold jobs
sbatch run_p40_the institutional HPC cluster.sbatch

# 3. Collect results and compute ipSAE
python collect_p40_robust.py
```

---

## Prerequisites

- ColabFold ≥ 1.5.5 (`colabfold_batch`)
- AF2-initial-guess (`dl_binder_design` repo, `af2_initial_guess/predict.py`)
- Reference `ipsae.py` (Dunbrack lab, bioRxiv 2025.02.10.637595)
- Python ≥ 3.9 with: `pandas`, `biopython`, `numpy`

---

## Confirmed output values (S3)

All five leads return ipSAE = 0.00 against p40 under full 5-model/3-recycle scoring:

| Lead | ipSAE (p40) | ipTM (p40) |
|------|-------------|------------|
| l94  | 0.00 | 0.12 |
| l104 | 0.00 | 0.12 |
| l72  | 0.00 | 0.11 |
| l92  | 0.00 | 0.12 |
| l83  | 0.00 | 0.12 |
