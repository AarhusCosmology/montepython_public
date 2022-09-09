from multiprocessing import Pool
import os
import warnings
import math
import sys
import io_mp
from montepython.likelihoods_emulated.cosmo_free_likelihoods.Planck_highl_TT_lite import Planck_highl_TT_lite
import sampler
from data import Data
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

def run(data, command_line):
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
                elif name_lkl == 'Planck_highl_TT_lite':
                    import likelihoods_emulated.cosmo_free_likelihoods.Planck_highl_TT_lite as Planck
                    like = Planck.Planck_highl_TT_lite(data.path, data, command_line)


                elif name_lkl == 'Planck_highl_TTTEEE':
                    print("Planck2018 TTTEEE not yet implemented!")

                loglkl.append(like.loglkl(data_point))

            np.savetxt(data_name.split('.')[0]+'.out', loglkl, header='loglkl')


    """
    h = data_point
    def overwrite_h(self):
        return h
    #cosmo.h() = lambda x: h  # <-- Override the function like this!
    cosmo.h = types.MethodType(overwrite_h, cosmo)
    print(cosmo.h())
    print(likelihood.loglkl(cosmo, data))
    """


    # To find out: How to set cosmo data!
    # Problem: The likelihood functions don't take direct inputs, instead they query the cosmo module for them.
    # To get this to work, I should therefore modify the cosmo module. This could maybe be done for things like attributes,
    # but the problem is that many of the likelihoods query cosmo.compute() etc. directly, which cannot be done unless some
    # serious hacking is done to the cosmo module. Even then, it would be impossible to do an automatic one-serves-all general
    # emulation that works on all likelihoods. We probably need to hardcode some of that!
    print("\nFinished evaluating likelihoods. Enjoy!")
    return 0

