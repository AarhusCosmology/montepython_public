import numpy as np 
import os 
import argparse
from datetime import datetime 
from natsort import os_sorted

"""
How to use:
   python read_profile.py -o FOLDER -p PARAMETER
where FOLDER is the path to a directory that contains a separate folder for each run with PARAMETER being the fixed parameter, as created by profile_likelihood.py.
This script then creates a .txt file in FOLDER that contains the bestfit values from the optimizations along with the values of the fixed parameter.

Arguments required:
    -p PARAMETER
    -o FOLDER

   /Emil Brinch Holm
   ebholm@phys.au.dk
   03/06-2022
"""

parser = argparse.ArgumentParser(description='chi2 optimizer by simulated annealing in MontePython. For further argument specifications, do MontePython.py run --help.')
parser.add_argument('-p', metavar='PARAMETER', type=str, help="Parameter kept fixed in the chi2 optimizations. Format should be the same as the CLASS input.")
parser.add_argument('-o', metavar='FOLDER', type=str, help="Folder with subdirectories for each run of the chi2 optimizer.")
parser.add_argument('--only-last', dest='last', action='store_true', help="If True, will only check the last step in each run (default: False).")
parser.add_argument('--2d', dest='two', action='store_true', help="If True, will analyze run for two-dimensional profile. In this case, the parameter argument should be on the form -p PARAM1-PARAM2 (default: False).")
args = parser.parse_args()

runs = [folder[1] for folder in os.walk(args.o)][0]
runs = [args.o+'/'+sub for sub in runs]

# Parse temperature schedule from profile_config.txt
with open(args.o+"/profile_config.txt","r") as config_file:
    for line in config_file.readlines():
        if line.startswith("N_iters = "):
            N_iters = [float(f) for f in line[line.find("=")+2:].split(' ')]
        elif line.startswith("N_per_step = "):
            N_per_step = float(line[line.find("=")+2:])
        elif line.startswith("T_list = "):
            T_list = [float(T) for T in line[line.find("=")+2:].split(' ')]
        elif line.startswith("f_list = "):
            f_list = [float(f) for f in line[line.find("=")+2:].split(' ')]

param_vals   = []
bestfit_chi2 = []
bestfit_contents = []


for idx, folder in enumerate(runs):
    print(f"\nReading {folder}")

    if os.listdir(folder): # only try to read if first sim folder is not empty 
        sim_folders = [sim_folder[1] for sim_folder in os.walk(folder)][0]
        sim_folders = os_sorted(sim_folders)

        for idx_sim, sim_folder in enumerate(sim_folders): # loop over simulations
            current_best_chi2 = np.inf
            folder_path = folder+"/"+sim_folder
            write_lines = []
            idx_iter_list = []
            has_parameters = False

            if args.last:
                # Only analyze last iteration
                current_highest = 0
                current_file = "step0.txt"
                for file in os.listdir(folder_path): # loop over iterations
                    if file.startswith("step") and file.endswith(".txt"):
                        if os.path.getsize(folder_path+"/"+file) == 0:
                            continue
                        data = np.loadtxt(folder_path+"/"+file)
                        if data.shape[0] <= 0 or len(data.shape) <= 1:
                            continue

                        iter_number = int(file[file.find("step")+4:file.find(".txt")])

                        if iter_number > current_highest:
                            current_file = file 
                            current_highest = iter_number

                    elif not has_parameters and file.endswith(".paramnames"):
                        paramnames = np.genfromtxt(f"{folder_path}/{file}", dtype=str, delimiter="\t")[:, 0]

                
                iter_number = int(current_file[current_file.find("step")+4:current_file.find(".txt")])
                if current_highest > 0:
                    data = np.loadtxt(folder_path+"/"+current_file)
                else:
                    continue
                if data.shape[0] > 0 and len(data.shape) > 1:
                    idx_best_in_iter = np.argmin(data[:,1])
                    best_chi2_in_iter = data[idx_best_in_iter, 1]
                    current_best_chi2 = best_chi2_in_iter

                    idx_iter_list.append(iter_number - 1)
                    write_line = np.insert(data[idx_best_in_iter, :], 0, [np.round(T_list[iter_number - 1],4), np.round(f_list[iter_number - 1],4)])
                    write_lines.append(write_line)
            else:
                for file in os_sorted(os.listdir(folder_path)): # loop over iterations
                    if file.startswith("step") and file.endswith(".txt"):
                        if os.path.getsize(folder_path+"/"+file) == 0:
                            idx_iter = int(file[file.find("step")+4:file.find(".txt")]) - 1
                            idx_iter_list.append(idx_iter)
                            if len(write_lines) != 0:
                                write_lines.append(write_lines[idx_iter - 1])
                            continue
                        data = np.loadtxt(folder_path+"/"+file, ndmin=2)
                        
                        if data.shape[0] > 0 and len(data.shape) > 1:
                            idx_best_in_iter = np.argmin(data[:,1])
                            best_chi2_in_iter = data[idx_best_in_iter, 1]
                            
                            idx_iter = int(file[file.find("step")+4:file.find(".txt")]) - 1
                            idx_iter_list.append(idx_iter)
                            write_line = np.insert(data[idx_best_in_iter, :], 0, [np.round(T_list[idx_iter],4), np.round(f_list[idx_iter],4)])
                            write_lines.append(write_line)
                            if best_chi2_in_iter <= current_best_chi2:
                                current_best_chi2 = best_chi2_in_iter
                                continue
                    elif not has_parameters and file.endswith(".paramnames"):
                        paramnames = np.genfromtxt(f"{folder_path}/{file}", dtype=str, delimiter="\t")[:, 0]
                        has_parameters = True

            if current_best_chi2 == np.inf:
                print(f"No files found for simulation {idx_sim}; skipping.")
                continue

            # Write a summary of each simulation
            write_lines = np.stack(write_lines, axis=0)
            ordering = np.argsort(idx_iter_list)
            idx_iter_list = np.array(idx_iter_list)[ordering]
            write_lines = write_lines[ordering]
            sim_filename = f"{folder}/sim{idx_sim}.txt"
            if os.path.isfile(sim_filename):
                os.remove(sim_filename)
            with open(sim_filename,"w") as out:
                out.write(f"iter \t T \t jump_factor \t mult \t -loglkl \t ")
                out.write(f" \t ".join([str(name) for name in paramnames])+"\n")
                for idx_iter in range(len(idx_iter_list)):
                    out.write(str(idx_iter)+" \t")
                    out.write(" \t ".join([str(val) for val in write_lines[idx_iter, :]])+"\n")
            print(f"Created summary file {folder}/sim{idx_sim}.txt")


        # Read best results from each run
        current_best = np.inf
        current_contents = []
        current_best_idx = 9999
        for file in os.listdir(folder):
            if file.startswith("sim") and file.endswith(".txt"):
                if os.path.getsize(f"{folder}/{file}") == 0:
                    continue
                data = np.loadtxt(f"{folder}/{file}", skiprows=1, delimiter="\t", ndmin=2)
                idx_best = np.argmin([data[:, 4]])
                data_vec = data[idx_best, :]

                if data_vec[4] < current_best:
                    current_best = data_vec[4]
                    current_contents = data_vec[5:]
                    current_best_idx = int(file[file.find("sim")+3:file.find(".txt")])

        if current_best < np.inf:
            print(f"Found best chi^2 = {current_best} in sim {current_best_idx}.")
            bestfit_chi2.append(current_best)
            bestfit_contents.append(current_contents)

            # extract .bestfit file for each param value
            for file in os.listdir(folder):
                if file.startswith("sim") and file.find(str(current_best_idx)) != -1:
                    print(f"Analyzing {folder}/{current_best_idx}...")

                    # NB This path must be changed to your system!
                    os.system(f"python ~/Documents/phd/montepython_public/montepython/MontePython.py info {folder}/{current_best_idx} --silent --minimal --ignore-burnin")
                    os.system(f"cp {folder}/{current_best_idx}/{current_best_idx}.bestfit {folder}")

            if os.path.exists(folder+"/0/log.param"):
                with open(folder+"/0/log.param","r") as file:
                    if args.two:
                        param_inp = args.p
                        param1, param2 = param_inp.split('-')[0], param_inp.split('-')[1]
                        new_param_vals = []
                        
                        found1, found2 = False, False
                        p1, p2 = 0, 0
                        for line in file.readlines():
                            if line.find(f"data.cosmo_arguments['{param1}'] = ") != -1:
                                p1 = float(line[line.find("=")+2:])
                                found1 = True
                            elif line.find(f"data.cosmo_arguments['{param2}'] = ") != -1:
                                p2 = float(line[line.find("=")+2:])
                                found2 = True
                        if found1 and found2:
                            param_vals.append([p1, p2])
                    else:    
                        for line in file.readlines():
                            if line.find(f"data.cosmo_arguments['{args.p}'] = ") != -1:
                                param_vals.append(float(line[line.find("=")+2:]))

if args.two:
    ordering = sorted(range(len(param_vals)), key=lambda k: param_vals[k])
else:
    ordering = np.argsort(param_vals)
param_vals       = np.array(param_vals)[ordering]
bestfit_chi2     = np.array(bestfit_chi2)[ordering]
bestfit_contents = np.array(bestfit_contents)[ordering]

print(f"{args.p} \t best-fit chi^2")
with open(args.o+"/results.txt","w") as file:
    if args.two:
        file.write(f" \t ".join([param for param in args.p.split('-')]))
        file.write(f" \t -loglkl \t ")
    else:
        file.write(f"{args.p} \t -loglkl \t ")
    file.write(f" \t ".join([str(name) for name in paramnames])+"\n")
    for param, chi2, contents in zip(param_vals, bestfit_chi2, bestfit_contents):
        if args.two:
            file.write(f" \t ".join([str(p) for p in param]))
            file.write(f" \t {chi2} \t ")
            param_string_print = ' \t '.join([str(np.round(p, 6)) for p in param])
            print(f"{param_string_print} \t {chi2}")
        else:
            file.write(f"{param} \t {chi2} \t ")
            print(f"{param} \t {chi2}")
        file.write(" \t ".join([str(val) for val in contents])+"\n")
        

# Collect the ultimate best-fit point
best_param = param_vals[np.argmin(bestfit_chi2)]
os.system(f"cp {args.o}/{str(best_param)}/*.bestfit {args.o}/{args.o}.bestfit")

print(f"\nFinished postprocessing of {args.o}. Enjoy!\n")