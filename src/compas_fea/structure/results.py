"""compas_fea.structure.results"""

from __future__ import print_function
from __future__ import absolute_import

__author__     = ['Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


__all__ = [
    'StepResults'
]


class StepResults(object):
    def __init__(self):
        """ Initialises results object.

        Parameters:
            u (dict): displacements dictionaty
            f (dict): frequencies dictionaty
            s (dict): stresses dictionaty
            ...

        Returns:
            None
        """
        self.u = {'nodal': {}, 'element': {}}
        self.f = {'nodal': {}, 'element': {}}
        self.s = {'nodal': {}, 'element': {}}


if __name__ == '__main__':
    pass
