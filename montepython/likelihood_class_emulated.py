from likelihood_class import Likelihood
import tensorflow as tf 
import numpy as np 
from time import time 

###################################
# Emulated likelihoods (currently only works for clik-type likeihoods)
# by E.B.Holm
# see arXiv:XXXX.XXXX
###################################

class Likelihood_emulated(Likelihood):

    def __init__(self, path, data, command_line):

        Likelihood.__init__(self, path, data, command_line)

        self.need_cosmo_arguments(
            data, {'lensing': 'yes', 'output': 'tCl lCl pCl'})

        self.model = tf.keras.models.load_model(f"{self.folder}/model")

    def loglkl(self, cosmo, data):
        cls = self.get_computed_cls(cosmo)
        nuisance = []
        for elem in data.get_mcmc_parameters(['varying', 'nuisance']): # be careful about the ordering, I think this works
            nuisance.append(data.mcmc_parameters[elem]['current']*data.mcmc_parameters[elem]['scale'])
        
        inp = np.concatenate([cls[spectrum_type][2:-2] for spectrum_type in self.spectrum_types])
        inp = np.concatenate([inp, nuisance])
        inp = tf.reshape(tf.constant(inp, dtype=tf.float32), [1, inp.shape[0]])

        #begin = time()
        loglkl = self.model(inp)[0][0].numpy()
        #end = time()
        #print(f"Evaluation of network took {end - begin:.6}s")
        return -loglkl
