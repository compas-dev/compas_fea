"""
compas_fea.structure.element : Element class.
Library of 1D, 2D and 3D element classes for FE analysis.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'Element',
    'BeamElement',
    'SpringElement',
    'TrussElement',
    'StrutElement',
    'TieElement',
    'ShellElement',
    'MembraneElement',
    'SolidElement',
    'PentahedronElement',
    'TetrahedronElement',
    'HexahedronElement'
]


# ==============================================================================
# General
# ==============================================================================

class Element(object):

    """ Initialises base Element object.

    Parameters:
        axes (list): The local element axes.
        nodes (list): Nodes the element connects to.
        number (int): Number of the element.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None
    """

    def __init__(self, axes={}, nodes=None, number=None, acoustic=None, thermal=None):
        self.axes = axes
        self.nodes = nodes
        self.number = number
        self.acoustic = acoustic
        self.thermal = thermal


# ==============================================================================
# 1D elements
# ==============================================================================

class BeamElement(Element):

    """ A 1D element that takes axial, shear, bending and torsion.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        Element.__init__(self)
        self.__name__ = 'BeamElement'


class SpringElement(Element):

    """ A 1D spring element.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        Element.__init__(self)
        self.__name__ = 'SpringElement'


class TrussElement(BeamElement):

    """ A 1D element that takes axial loads.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        BeamElement.__init__(self)
        self.__name__ = 'TrussElement'


class StrutElement(TrussElement):

    """ A truss element that takes axial compressive loads.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        TrussElement.__init__(self)
        self.__name__ = 'StrutElement'


class TieElement(TrussElement):

    """ A truss element that takes axial tensile loads.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        TrussElement.__init__(self)
        self.__name__ = 'TieElement'


# ==============================================================================
# 2D elements
# ==============================================================================

class ShellElement(Element):

    """ A 2D element that takes axial, shear, bending and torsion.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        Element.__init__(self)
        self.__name__ = 'ShellElement'


class MembraneElement(ShellElement):

    """ A shell element that takes only axial loads.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        ShellElement.__init__(self)
        self.__name__ = 'MembraneElement'


# ==============================================================================
# 3D elements
# ==============================================================================

class SolidElement(Element):

    """ A 3D element that takes axial, shear, bending and torsion.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        Element.__init__(self)
        self.__name__ = 'SolidElement'


class PentahedronElement(SolidElement):

    """ A Solid element with 5 faces (extruded triangle).

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        SolidElement.__init__(self)
        self.__name__ = 'PentahedronElement'


class TetrahedronElement(SolidElement):

    """ A Solid element with 4 faces.

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        SolidElement.__init__(self)
        self.__name__ = 'TetrahedronElement'


class HexahedronElement(SolidElement):

    """ A Solid cuboid element with 6 faces (extruded rectangle).

    Parameters:
        None

    Returns:
        None
    """

    def __init__(self):
        SolidElement.__init__(self)
        self.__name__ = 'HexahedronElement'
