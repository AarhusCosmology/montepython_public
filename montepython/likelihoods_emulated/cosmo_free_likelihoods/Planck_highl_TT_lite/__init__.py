from montepython.likelihood_class import Likelihood_clik


class Planck_highl_TT_lite(Likelihood_clik):
    def get_cl(self, cosmo, l_max=-1):
        print("TEST FROM NEW GET_CL")
        return 0
    def get_unlensed_cl(self, cosmo, l_max=-1):
        print("Hello world from get_unlensed_cl()")
        return 0
