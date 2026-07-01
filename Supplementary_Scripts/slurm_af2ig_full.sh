#!/bin/bash
#SBATCH --job-name=af2ig_full
#SBATCH --partition=gpu-a100
#SBATCH --array=0-3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --gres=gpu:a100:1
#SBATCH --time=18:00:00
#SBATCH --output=af2ig_full_%A_%a.out
#SBATCH --error=af2ig_full_%A_%a.err
#SBATCH -A your-slurm-account

cd /path/to/project/dl_binder_design
module load cuda/12.3.0/gcc/11.3.0/zen2
module load cudnn/8.9.7.29-12/gcc/11.3.0/zen2
source ~/miniforge3/bin/activate; conda activate af2_binder_design
export OPENBLAS_NUM_THREADS=1
export LD_LIBRARY_PATH="$CUDA_HOME/extras/CUPTI/lib64:$CUDA_HOME/targets/x86_64-linux/lib:$LD_LIBRARY_PATH"
export XLA_FLAGS="--xla_gpu_cuda_data_dir=$CUDA_HOME"
cp $CUDA_HOME/nvvm/libdevice/libdevice.10.bc ./libdevice.10.bc

C=$SLURM_ARRAY_TASK_ID
echo "=== chunk $C start $(date) ==="
python af2_initial_guess/predict.py \
    -pdbdir il23_ig_full_in/chunk_${C} \
    -outpdbdir il23_ig_full_out \
    -scorefilename il23_ig_full_scores_${C}.sc \
    -checkpoint_name il23_ig_full_${C}.point
echo "=== chunk $C done $(date) | PAE files: $(ls il23_ig_full_out/*_pae.npy 2>/dev/null | wc -l) ==="
