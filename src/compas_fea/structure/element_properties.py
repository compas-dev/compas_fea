"""
compas_fea.structure.element_properties : ElementProperties class.
Object that matches elements with their material and section.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'ElementProperties'
]


class ElementProperties(object):

    """ Initialises ElementProperties object.

    Parameters:
        material str): Name of the material to assign.
        section (str): Name of the section to assign.
        elsets (list): ELSETs the properties are assigned to.
        elements (list): Elements the properties are assigned to.
        reinforcement (dic): Reinforcement information for the element/section.

    Returns:
        None
    """

    def __init__(self, material, section, elsets=None, elements=None, reinforcement={}):
        self.material = material
        self.section = section
        self.elsets = elsets
        self.elements = elements
        self.reinforcement = reinforcement
        if (not elsets) and (not elements):
            raise NameError('Element properties require elements or element sets (ELSETs)')
