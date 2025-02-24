#!/bin/bash -l
#SBATCH --job-name=ralphasconnect
#SBATCH --partition=q48,q40,q36,q28
#SBATCH --nodes=1
#SBATCH --ntasks=6
#SBATCH --ntasks-per-node=6
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
#SBATCH --output="/home/camtgs/MontePython/MontePythonCluster/out/ralphas_connect.out"
#SBATCH --error="/home/camtgs/MontePython/MontePythonCluster/out/ralphas_connect.err"
MPARGS=" -p montepython_public/input/ralphas_connect1.param"
MPARGS+=" -o chains/ralphas_connect4"
MPARGS+=" -c montepython_public/covmat/base2018TTTEEE_lensing.covmat"
MPARGS+=" -N 9876543210"
MPARGS+=" --silent"
echo "========= Job started at `date` =========="
source activate ConnectEnvironment
#source planck2018/code/plc_3.0/plc-3.01/bin/clik_profile.sh
source /home/camtgs/connect_public/resources/planck2018/code/plc_3.0/plc-3.01/bin/clik_profile.sh
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
cd $SLURM_SUBMIT_DIR
mpirun -n $SLURM_NPROCS python montepython_public/montepython/MontePython.py run $MPARGS
echo "========= Job finished at `date` =========="
