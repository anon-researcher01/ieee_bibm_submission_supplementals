#!/bin/bash
#SBATCH --job-name=p40_full
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=p40_full_%j.log
#SBATCH --error=p40_full_%j.err

cd /path/to/project

echo "===== JOB START ====="
date
hostname
pwd

echo "===== GPU CHECK BEFORE ENV ====="
nvidia-smi || true

echo "===== MODULE CHECK ====="
source /etc/profile 2>/dev/null || true
source /etc/profile.d/modules.sh 2>/dev/null || true
module list 2>&1 || true

echo "===== TRY LOAD CUDA/CUDNN WITHOUT PURGE ====="
module load cuda 2>&1 || true
module load cudnn 2>&1 || true
module load cuda/11.8 2>&1 || true
module load cudnn/8.9.7 2>&1 || true
module load cuda/12.1 2>&1 || true
module load cudnn/8.9.2 2>&1 || true
module list 2>&1 || true

echo "===== CONDA ENV ====="
source /path/to/project/miniforge3/etc/profile.d/conda.sh
conda activate SE3nv

export XDG_CACHE_HOME=/path/to/project/.cache
export COLABFOLD_DATA=/path/to/project/colabfold_data
mkdir -p "$XDG_CACHE_HOME" "$COLABFOLD_DATA"

echo "CONDA=$CONDA_DEFAULT_ENV"
which python
which colabfold_batch

echo "===== GPU CHECK AFTER ENV ====="
nvidia-smi || true

echo "===== PYTHON CHECK ====="
python - <<'PYTEST'
import pandas
import colabfold
print("pandas OK")
print("colabfold OK")
PYTEST

echo "===== CLEAN OLD PARTIAL OUTPUT ====="
rm -rf p40_inputs p40_out p40_selectivity.csv

echo "===== BUILD FASTAS ====="
python leads_vs_p40.py build

echo "===== RUN COLABFOLD FAST SINGLE-SEQUENCE ====="
colabfold_batch \
  --data /path/to/project/colabfold_data \
  --msa-mode single_sequence \
  --num-models 5 \
  --num-recycle 3 \
  p40_inputs/ p40_out/

echo "===== COLLECT IPSAE ====="
python leads_vs_p40.py collect

echo "===== DONE ====="
cat p40_selectivity.csv
