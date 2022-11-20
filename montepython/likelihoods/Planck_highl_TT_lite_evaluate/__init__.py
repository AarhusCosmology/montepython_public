from montepython.likelihood_class import Likelihood_clik
import numpy as np 
from scipy.interpolate import interp1d

class Planck_highl_TT_lite_evaluate(Likelihood_clik):
    def __init__(self, path, data, command_line):
        self.evaluate_current_cls = 0
        self.evaluate_ells = 0
        Likelihood_clik.__init__(self, path, data, command_line)


    def get_cl(self, cosmo, l_max=-1):
#        print("\nRUNNING get_cl()!")
        full_grid = range(self.clik.get_lmax()[0] + 1)
        #print(self.evaluate_current_cls)
        interped_cls = interp1d(self.evaluate_ells, self.evaluate_current_cls, fill_value="extrapolate", kind="cubic")(full_grid)
        return {'tt': interped_cls}

    def get_unlensed_cl(self, cosmo, l_max=-1):
        print("\nRUNNING get_unlensed_cl()!")
        return {'tt': self.evaluate_current_cls}
