
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

    """ Initialises ElementProperties object.

    Parameters
    ----------
    name : str, int
        Key for the ElementProperties object.
    material : str
        Name of the material to assign.
    section : str
        Name of the section to assign.
    elsets : list, str
        Element sets the properties are assigned to.
    elements : list
        Elements the properties are assigned to.
    reinforcement : dic
        Reinforcement information.

    Returns
    -------
    None

    Notes
    -----
    - elements or elsets should be given, not both.

    """

    def __init__(self, name, material, section, elsets=None, elements=None, reinforcement={}):
        self.name = name
        self.material = material
        self.section = section
        self.elsets = elsets
        self.elements = elements
        self.reinforcement = reinforcement
        if (not elsets) and (not elements):
            raise NameError('Element properties require elements or element sets')
