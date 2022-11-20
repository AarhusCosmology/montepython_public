from multiprocessing import Pool
import os
import warnings
import math
import sys
import io_mp
import sampler
from data import Data, Parameter
import numpy as np 
import types 

"""
    This module evaluates likelihood functions from pre-computed data (e.g. from a cosmo module).
    It is used like:
        python montepython/MontePython.py run -m EV -o chains/OUTPUT_CHAIN -p input/test_evaluate.param

    Remember to make sure that there is no log.param when switching around your parameter files!

    /Emil Brinch Holm
    Aarhus University & RWTH Aachen
    ebholm@phys.au.dk
    09/09 2022
"""

def run(cosmo, data, command_line):
    # cosmo input is taken for convenience but never actually used!
    for name_lkl, likelihood in data.lkl.items(): # Currently only works with one likelihood at a time 
        print(f"\nEvaluating {name_lkl}")
        loglkl = []
        nuisance_vectors = []
        for data_name in data.evaluate_data:
            # no suffixes! e.g. sample1 takes data from sample1.clell and sample1.cltt
            ell = np.genfromtxt(f"{data_name}.clell", comments='#', dtype=int)
            likelihood.evaluate_ells = ell
            cltt = np.genfromtxt(f"{data_name}.cltt", comments='#', dtype=float)[:, 1:]
            for idx_spectrum, single_spectrum in enumerate(cltt):
                likelihood.evaluate_current_cls = single_spectrum

                nuisance_params = {}
                nuisance_param_names = data.get_mcmc_parameters(['nuisance'])
                if data.evaluate_nuisance_strategy == 'lhc':
                    print("\nCreating Latin hypercube in nuisance params")
                    print(f"Spectrum mean: {np.mean(single_spectrum)}")
                    if data.evaluate_nuisance_samples > 0:
                        samples = GetNuisanceLHC(data)
                        nuisance_params = {nuisance_param_names[idx_param]: samples[:, idx_param] for idx_param in range(len(nuisance_param_names))}
                    else:
                        raise KeyError(f"data.evaluate_nuisance_samples must be set in parameter file.")
                elif data.evaluate_nuisance_strategy == 'test':
                    print(f"Fixing all nuisance parameters to 1.0 for syntax testing purposes")
                    for param_name in nuisance_param_names:
                        nuisance_params[param_name] = [1.0]
                else:
                    raise NotImplementedError(f"Nuisance parameter sampling strategy {data.evaluate_nuisance_strategy} not recognized.")

                for idx_nuisance_sample in range(len(nuisance_params[nuisance_param_names[0]])):
                    for key, val in nuisance_params.items():
                        data.mcmc_parameters[key]['current'] = val[idx_nuisance_sample]
                    loglkl.append(likelihood.loglkl(cosmo, data))
                    print(f"Computed loglkl = {loglkl[-1]}")
                
                if data.evaluate_nuisance_strategy != 'test':
                    np.savetxt(data_name+'.nuisance', samples, header=' \t '.join(nuisance_param_names))
            np.savetxt(data_name+'.loglkl', loglkl, header='loglkl')

    print("\nFinished evaluating likelihoods. Enjoy!")
    return 0

def GetNuisanceLHC(data):
    nuisance_param_names = data.get_mcmc_parameters(['nuisance'])
    # get nuisance parameter bounds to scale the LHC
    from scipy.stats.qmc import LatinHypercube
    N_samples = data.evaluate_nuisance_samples
    LHC = LatinHypercube(d=len(nuisance_param_names))
    samples = LHC.random(n=data.evaluate_nuisance_samples)
    for idx_param, param_name in enumerate(nuisance_param_names):
        # Scale hypercube according to bounds in param file
        lower_bound, upper_bound = data.parameters[param_name][1], data.parameters[param_name][2]
        samples[:, idx_param] = samples[:, idx_param]*(upper_bound - lower_bound) + lower_bound
    return samples