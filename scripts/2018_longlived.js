#!/bin/bash
#SBATCH --job-name=18_longlived
#SBATCH --partition=q24,q28,q36,q48
#SBATCH --mem=80G
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=6
#SBATCH --time=300:00:00
output_dir='/path/to/montepython_public/chains/18_longlived'
MPARGS=" -p /path/to/montepython_public/input/2018_longlived.param"
MPARGS+=" -o $output_dir"
MPARGS+=" -c /path/to/montepython_public/covmat/base2018TTTEEE.covmat"
MPARGS+=" -N 5000000000"
MPARGS+=" --conf default.conf"
MPARGS+=" -j fast -f 2.1 --silent"
MPARGS+=" --update 5000"
echo "========= Job started  at `date` =========="
rm -rf $output_dir
# load correct python
ml load anaconda3/5.0.1
source activate MontePythonEnvironment
# source click_profile.sh
source planck2018/code/plc_3.0/plc-3.01/bin/clik_profile.sh
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
cd $SLURM_SUBMIT_DIR
mpirun -n $SLURM_NPROCS python montepython/MontePython.py run $MPARGS
echo "========= Job finished at `date` =========="
