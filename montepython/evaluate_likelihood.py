from multiprocessing import Pool
import os
import warnings
import math
import sys
import io_mp
#from montepython.likelihoods_emulated.cosmo_free_likelihoods.Planck_highl_TT_lite import Planck_highl_TT_lite
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
    input = []
    for name_lkl, likelihood in data.lkl.items():
        print(f"\nEvaluating {name_lkl}")
        loglkl = []
        for data_name in data.evaluate_data:
            # no suffixes! e.g. sample1 takes data from sample1.clell and sample1.cltt
            ell = np.genfromtxt(f"{data_name}.clell", comments='#', dtype=int)
            likelihood.evaluate_ells = ell
            cltt = np.genfromtxt(f"{data_name}.cltt", comments='#', dtype=float)[:, 1:]
            for single_spectrum in cltt:
                likelihood.evaluate_current_cls = single_spectrum
                print(np.mean(single_spectrum))

                # do MCMC in nuisance parameters

                #data.mcmc_parameters['A_planck']['current'] = data.mcmc_parameters['A_planck']['initial']
                data.mcmc_parameters['A_planck']['current'] = 1.0

                loglkl.append(likelihood.loglkl(cosmo, data))
                print(f"Computed loglkl = {loglkl[-1]}")
            
            np.savetxt(data_name+'.loglkl', loglkl, header='loglkl')

    print("\nFinished evaluating likelihoods. Enjoy!")
    return 0