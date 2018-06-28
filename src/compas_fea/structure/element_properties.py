
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'ElementProperties'
]


class ElementProperties(object):

    """ Initialises an ElementProperties object.

    Parameters
    ----------
    name : str
        Key name for the ElementProperties object.
    material : str
        Name of the Material object to assign.
    section : str
        Name of the Section object to assign.
    elsets : list
        Element set names assignment.
    elements : list
        Element keys assignment.
    reinforcement : dict
        Reinforcement layer data.

    Returns
    -------
    None

    Notes
    -----
    - Either ``elements`` or ``elsets`` should be given, not both.

    """

    def __init__(self, name, material=None, section=None, elsets=None, elements=None, reinforcement={}):

        self.name          = name
        self.material      = material
        self.section       = section
        self.elsets        = elsets
        self.elements      = elements
        self.reinforcement = reinforcement

        if (not elsets) and (not elements):
            raise NameError('***** ElementProperties objects require elements or element sets *****')

    def __str__(self):

        print('compas_fea ElementProperties object')
        print('-----------------------------------')
        for attr in ['name', 'material', 'section', 'elsets', 'elements', 'reinforcement']:
            print('{0:<13} : {1}'.format(attr, getattr(self, attr)))

        return ''
