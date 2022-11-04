#!/bin/bash
#SBATCH --job-name=JOBNAME_TEMPNAME_PARALLEL_SIM_NAME
#SBATCH --partition=XXX
#SBATCH --nodes=X
#SBATCH --ntasks=X
#SBATCH --ntasks-per-node=X
#SBATCH --cpus-per-task=X
#SBATCH --time=XXXX:XXXX:XXXX
#SBATCH --output="/path/to/stdoutput/JOBNAME_TEMPNAME_PARALLEL_SIM_NAME.out"
#SBATCH --error="/path/to/stdoutput/JOBNAME_TEMPNAME_PARALLEL_SIM_NAME.err"
MPARGS=" -p /path/to/parameterfiles/JOBNAME/JOBNAME_base_TEMPNAME.param"
MPARGS+=" -o /path/to/output/OUTFOLDERNAME"
MPARGS+=" -c /path/to/covmat/dcdm.covmat"
MPARGS+=" -b /path/to/bestfit.bestfit"
MPARGS+=" --conf /path/to/config/default.conf"
MPARGS+=" -i PARALLEL_SIM_NAME"
echo "========= Job started at `date` =========="

# activate Python environment

# source clik_profile.sh

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
cd $SLURM_SUBMIT_DIR
echo $SLURM_NPROCS
python /path/to/profile_single.py $MPARGS
echo "========= Job finished at `date` =========="


