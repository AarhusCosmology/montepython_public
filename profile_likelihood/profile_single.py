from multiprocessing.sharedctypes import Value
import numpy as np 
import os 
import sys
import argparse
from datetime import datetime 

"""
Subroutine used to run simulated annealing optimization for a single model.
Called by profile_likelihood.py
Based on bestfit_optimizer.py

   /Emil Brinch Holm
   ebholm@phys.au.dk
   03/06-2022
"""

parser = argparse.ArgumentParser(description='chi2 optimizer by simulated annealing in MontePython. For further argument specifications, do MontePython.py run --help.')
parser.add_argument('-p', metavar='PARAM', type=str, help="Input parameter file.")
parser.add_argument('-o', metavar='FOLDER', type=str, help="Output folder.")
parser.add_argument('-c', metavar='COV', type=str, help="Input covariance matrix.")
parser.add_argument('-b', metavar='BF', type=str, help=".bestfit file to start from.")
parser.add_argument('-i', metavar='ITER', type=int, help="Iteration index.")
parser.add_argument('-j', metavar='JUMP', type=str, help="Jumping strategy.")
parser.add_argument('--conf', dest='conf', type=str, help="MontePython configuration file.")
args = parser.parse_args()

# Parse temperature schedule from profile_config.txt
if not os.path.isdir(args.o):
    os.system(f"mkdir {args.o}")
with open(args.o+"/../profile_config.txt","r") as config_file:
    for line in config_file.readlines():
        if line.startswith("N_iters = "):
            N_iters = int(line[line.find("=")+2:])
        elif line.startswith("N_per_step = "):
            N_per_step = int(line[line.find("=")+2:])
        elif line.startswith("T_list = "):
            T_list = [float(T) for T in line[line.find("=")+2:].split(' ')]
        elif line.startswith("f_list = "):
            f_list = [float(f) for f in line[line.find("=")+2:].split(' ')]

for hyperparam_name in ['N_iters', 'N_per_step', 'T_list', 'f_list']:
    if hyperparam_name not in locals():
        raise ValueError(f"Input parameter {hyperparam_name} not read from config file!")

# Stores filenames of bestfits
now = datetime.now()
date_today = now.strftime(f"%Y-%m-%d")
year_today = now.strftime(f"%Y")
chain_basename = now.strftime(f"%Y-%m-%d_{N_per_step}__")

iter = args.i
path_iter = f"{args.o}/{iter}"
os.system(f"mkdir {path_iter}")

MPARGS = f" -p {args.p} -o {path_iter} -N {N_per_step} --silent --update 0"
if args.j is not None:
    MPARGS+=f" -j {args.j}"
else:
    MPARGS+=" -j global" # global stepping is default
if args.conf is not None:
    MPARGS+=f" --conf {args.conf}"
if args.c is not None:
    os.system(f"cp {args.c} {path_iter}/start.covmat")
    MPARGS+=f" -c {args.c}"
if args.b is not None:
    os.system(f"cp {args.b} {path_iter}/start.bestfit")
    bestfit_file = f"{path_iter}/start.bestfit"

for idx_iter, T in enumerate(T_list):
    ITER_ARGS = f" --lklfactor {1/T} -f {f_list[idx_iter]}"
    if idx_iter == 0:
        if args.b is not None:
            ITER_ARGS += f" --chain-number {1} -b {bestfit_file}"
        else:
            ITER_ARGS += f" --chain-number {1}"
    else:
        prior_chain_name = f"{path_iter}/{date_today}_{idx_iter*N_per_step}__1.txt"
  
        os.system(f"cp {prior_chain_name} {path_iter}/temp{idx_iter}.txt")
        ITER_ARGS += f" -r {prior_chain_name}"
    
    os.system('python montepython_public/montepython/MontePython.py run'+MPARGS+ITER_ARGS)

    current_name = f"{path_iter}/{date_today}_{(idx_iter + 1)*N_per_step}__1.txt"
        
    # Test to rename chain files that spawn with later dates than date_today
    for file in os.listdir(f"{path_iter}"):
        if f"{path_iter}/{file}" != current_name:
            if file.startswith(year_today) and file.endswith(f"{(idx_iter + 1)*N_per_step}__1.txt"):
                os.system(f"mv {path_iter}/{file} {current_name}")
                os.system(f"mv {path_iter}/{file[:-6]}.paramnames {current_name[:-6]}.paramnames")

    # Save chain contents
    if idx_iter > 0:
        os.system(f"cp {current_name} {path_iter}/step{idx_iter}_full.txt")
        os.system(f"grep -Fxvf {path_iter}/temp{idx_iter}.txt {path_iter}/step{idx_iter}_full.txt > {path_iter}/step{idx_iter}.txt")
        os.system(f"rm {path_iter}/step{idx_iter}_full.txt")
        os.system(f"rm {path_iter}/temp{idx_iter}.txt")
        os.system(f"rm {path_iter}/{date_today}_{(idx_iter + 1)*N_per_step}_.paramnames")
    else:
        os.system(f"cp {current_name} {path_iter}/step{idx_iter}.txt")

# 26/10/2022: I don't think this is needed anymore, with the standard MP installation
#for idx_iter, T in enumerate(T_list[:-1]): # leave the last text file so MP can analyze the folder
#    name = f"{path_iter}/{date_today}_{(idx_iter + 1)*N_per_step}__1.txt"
#    os.system(f"rm {name}")
