import numpy as np 
import os 
from datetime import datetime 

"""
How to use:
   python profile_likelihood.py
The code will then generate and sbatch slurm jobscripts based on the input on the first lines below the documentation here.
After finishing, one can use the read_profile.py script to extract the bestfit chi^2 values for each model.

You may need to adjust according to your particular cluster.

Remember to fill in the input below!

   /Emil Brinch Holm
   ebholm@phys.au.dk
   03/06-2022
"""

# --- Set meta-data --- #
jobname = 'prof_dcdm_Gamma'
base_jobscript = f'{jobname}_base.sh' # must be in jobscripts directory
base_paramfile = f'{jobname}_base.param' # must be in montepython_public/input directory
output_folder  = f'chains/{jobname}'

param = 'log10_Gamma_dcdm_Gyr'
param_vals = np.round(np.linspace(3.5, 6.0, 15), 2)


# Amount of attempted jumps per temperature step
N_per_step = 1000
N_iters = 8

# --- Set cooling schedule --- #
N_steps = 8
T_max = 0.005
T_min = 1e-4
jump_factors = np.logspace(-0.0, -1.5, N_steps)

dec_const = np.log(T_max/T_min)/N_steps
T_list = T_max*np.exp(-dec_const*np.arange(0, N_steps))

##################
# 
#  Automatic from here
#
##################

# Can add check in paramfile that the chosen parameter is not set as a cosmological parameter, but as a fixed argument

# Store configuration file with the inputs
if not os.path.isdir(output_folder):
    os.system(f'mkdir {output_folder}')
else:
    raise ValueError("Output folder already exists! Remove it before running again.")
with open(output_folder + "/profile_config.txt","w") as config_file:
    config_file.write(f"N_iters = {N_iters}\n")
    config_file.write(f"N_per_step = {N_per_step}\n")
    config_file.write(f"T_list = {' '.join([str(T) for T in T_list])}\n")
    config_file.write(f"f_list = {' '.join([str(f) for f in jump_factors])}\n")

os.system(f"rm -r jobscripts/{jobname}")
os.system(f"mkdir jobscripts/{jobname}")

os.system(f"rm -r montepython_public/input/{jobname}")
os.system(f"mkdir montepython_public/input/{jobname}")

for idx_param, param_val in enumerate(param_vals):
    single_output_folder = f"{output_folder}/{param_val}"
    os.system(f"mkdir {single_output_folder}")
    for idx_sim in range(N_iters):
        jobscript_filename = f"jobscripts/{jobname}/{base_jobscript[:-3]}_{param_val}_{idx_sim}.sh"
        os.system(f"cp jobscripts/{base_jobscript} {jobscript_filename}")
        os.system(f'sed -i "s@JOBNAME@{jobname}@g" {jobscript_filename}')
        os.system(f'sed -i "s@TEMPNAME@{param_val}@g" {jobscript_filename}')
        os.system(f'sed -i "s@PARALLEL_SIM_NAME@{idx_sim}@g" {jobscript_filename}')
        os.system(f'sed -i "s@OUTFOLDERNAME@{single_output_folder}@g" {jobscript_filename}')

        param_filename = f"montepython_public/input/{jobname}/{base_paramfile[:-6]}_{param_val}.param"
        os.system(f"cp montepython_public/input/{base_paramfile} {param_filename}")
        os.system(f'sed -i "s@TEMPNAME@{param_val}@g" {param_filename}')

        os.system(f"sbatch {jobscript_filename}")
