from multiprocessing import Pool
import os
import warnings
import math
import sys
import io_mp
from montepython.likelihoods_emulated.cosmo_free_likelihoods.Planck_highl_TT_lite import Planck_highl_TT_lite
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
    for data_name in data.evaluate_data:
        input.append(np.genfromtxt(data_name, comments='#', dtype=float))

    for name_lkl in data.lkl.keys():
        for data_name, data_vector in zip(data.evaluate_data, input):
            print(f"Evaluating inputs in: {data_name}")
            loglkl = []
            for data_point in data_vector:

                if name_lkl == 'sh0es':
                    import likelihoods_emulated.cosmo_free_likelihoods.sh0es as sh0es
                    like = sh0es.sh0es(data.path, data, command_line)
                    loglkl.append(like.loglkl(data_point))

                elif name_lkl == 'Planck_highl_TT_lite':
                    import likelihoods_emulated.cosmo_free_likelihoods.Planck_highl_TT_lite as Planck
                    nuisance_parameter_names = ['A_planck']

                    initialize_nuisance_parameters(data, nuisance_parameter_names) # in the future, put this outside the loop
                    set_nuisance_parameters(data, nuisance_parameter_names, data_point)
                    # remember to also update the "varying" parameters!

                    folder = os.path.abspath(os.path.join(data.path['MontePython'], "likelihoods", "%s" % name_lkl))
                    like = Planck.Planck_highl_TT_lite(f"{folder}/{name_lkl}.data", data, command_line)
                    loglkl.append(like.loglkl(cosmo, data, command_line))

                elif name_lkl == 'Planck_highl_TTTEEE':
                    print("Planck2018 TTTEEE not yet implemented!")


            np.savetxt(data_name.split('.')[0]+'.out', loglkl, header='loglkl')
    print("\nFinished evaluating likelihoods. Enjoy!")
    return 0

def initialize_nuisance_parameters(data, nuisance_parameter_names):
    for parameter in nuisance_parameter_names:
        data.mcmc_parameters[parameter] = Parameter([100.028,   90,  110,  0.25,  0.01,'nuisance'], parameter)
        data.mcmc_parameters[parameter]['scale'] = 1.0

def set_nuisance_parameters(data, nuisance_parameter_names, data_point):
    N_nuisance = len(nuisance_parameter_names)
    for idx, parameter in enumerate(nuisance_parameter_names):
        # data.mcmc_parameters[nuisance]['current'] = data_point[-N_nuisance + idx]
        data.mcmc_parameters[parameter]['current'] = 100.0
