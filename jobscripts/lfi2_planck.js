#!/bin/bash
#SBATCH --job-name=lfi2_1200
#SBATCH --partition=q28,q40
#SBATCH --exclude=s82n[26,31-36,41]
#SBATCH --mem-per-cpu=2g
#SBATCH --ntasks=24
#SBATCH --cpus-per-task=1
#SBATCH --time=96:00:00
#SBATCH --output="/home/camtgs/MontePython/MontePythonCluster/out/lfi2_1200.out"
#SBATCH --error="/home/camtgs/MontePython/MontePythonCluster/out/lfi2_1200.err"

echo "========= Job started at `date` =========="
source ~/.bashrc
source /com/bin/modules.sh
ml load anaconda3 gcc openmpi
source activate ConnectEnvironment
export LD_LIBRARY_PATH=/lib64:/home/camtgs/connect/resources/MultiNest/lib/:$LD_LIBRARY_PATH

source /home/camtgs/connect_public/resources/planck2018/code/plc_3.0/plc-3.01/bin/clik_profile.sh
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
cd $SLURM_SUBMIT_DIR
srun -n $SLURM_NPROCS python montepython_public/montepython/MontePython.py run -p montepython_public/input/lfi2_planck.param  -o chains/lfi2_1200 -m PC --PC_nlive 1200 --PC_grade_dims 34 --PC_grade_frac 1.0
echo "========= Job finished at `date` =========="
