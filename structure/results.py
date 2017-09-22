"""compas_fea.structure.results"""

from compas_fea.fea.ansys.reading import *

__author__     = ['Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


__all__ = [
    'NodalResults'
]


class NodalResults(object):
    def __init__(self):

        """ Initialises Results object for use in finite element analysis.

        Parameters:
            nodal_stresses (dict): blah blah blah

        Returns:
            None
        """
        self.stresses = None
        self.shear = None
        self.strains = None
        self.displacements = None
        self.reactions = None
        self.modal_displcacements = None
        self.modal_frequencies = None
        self.harmonic_displacements = None
        self.harmonic_frequencies  = None
        self.path = None

    def load_results_from_files(self, software, path, stresses=False, shear=False, strains=False,
                                displacements=False, reactions=False, modal_displcacements=False,
                                modal_frequencies=False, harmonic_displacements=False):
        if software == 'ansys':
            if stresses:
                self.stresses = get_nodal_stresses_from_result_files(path)
            if shear:
                self.shear = get_shear_stresses_from_result_files(path)
            if strains:
                self.strains = get_principal_strains_from_result_files(path)
            if displacements:
                self.displacements = get_displacements_from_result_files(path)
            if reactions:
                self.reactions = get_reactions_from_result_files(path)
            if modal_displcacements:
                self.modal_displcacements, self.modal_frequencies = get_modal_data_from_result_files(path)
            if harmonic_displacements:
                self.harmonic_displacements, self.harmonic_frequencies = get_harmonic_data_from_result_files(path)


if __name__ == '__main__':
    path = '/Users/mtomas/Desktop/ansys_test/'
    res = NodalResults()
    res.load_results_from_files('ansys', path, stresses=True)
    print res.stresses
