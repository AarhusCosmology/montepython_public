from planck_lite_py import PlanckLitePy
class PlanckLitePython(Likelihood):

def __init__(self, path, data, command_line):

        super(PlanckLitePython, self).__init__(path, data, command_line)
        self.need_cosmo_arguments(
            data, {'lensing': 'yes', 'output': 'tCl lCl pCl'})


        self.TT2018 = PlanckLitePy(data_directory='data', year=2018, spectra='TTTEEE', use_low_ell_bins=False)



def loglkl(self, cosmo, data):

        nuisance_parameter_names = data.get_mcmc_parameters(['nuisance'])

        # get Cl's from the cosmological code
        cl = self.get_cl(cosmo)
        ell = cl['ell']
        factor = ell*ell/(2*np.pi)

        Dltt = cl['tt']*factor
        Dlte = cl['te']*factor
        Dlee = cl['ee']*factor

        return loglkl(self.TT2018.loglike(Dltt, Dlte, Dlee, 0))