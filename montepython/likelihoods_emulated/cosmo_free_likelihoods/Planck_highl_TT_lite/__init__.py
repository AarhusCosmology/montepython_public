from montepython.likelihood_class import Likelihood_clik


class Planck_highl_TT_lite_evaluate(Likelihood_clik):
    def __init__(self, path, data, command_line):
        print("INITIALIZING EVAL LIKELIHOOD CLASS!")
        self.evaluate_current_cls = 0
        Likelihood_clik.__init__(self, path, data, command_line)
        print("FINISHED INITIALIZING EVAL LIKELIHOOD CLASS!")


    def get_cl(self, cosmo, l_max=-1):
        print("RUNNING get_cl()!")
        return self.evaluate_current_cls

    def get_unlensed_cl(self, cosmo, l_max=-1):
        print("RUNNING get_unlensed_cl()!")
        return self.evaluate_current_cls
