from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Element',
    'BeamElement',
    'SpringElement',
    'TrussElement',
    'StrutElement',
    'TieElement',
    'ShellElement',
    'MembraneElement',
    'FaceElement',
    'SolidElement',
    'PentahedronElement',
    'TetrahedronElement',
    'HexahedronElement',
    'MassElement'
]


# ==============================================================================
# General
# ==============================================================================

class Element(object):
    """Initialises base Element object.

    Parameters
    ----------
    nodes : list
        Node keys the element connects to.
    number : int
        Number of the element.
    thermal : bool
        Thermal properties on or off.
    axes : dict
        The local element axes.

    Attributes
    ----------
    nodes : list
        Node keys the element connects to.
    number : int
        Number of the element.
    thermal : bool
        Thermal properties on or off.
    axes : dict
        The local element axes.
    element_property : str
        Element property name

    """

    def __init__(self, nodes=None, number=None, thermal=None, axes={}):

        self.__name__ = 'Element'
        self.nodes = nodes
        self.number = number
        self.thermal = thermal
        self.axes = axes
        self.element_property = None

    def __str__(self):
        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in ['nodes', 'number', 'thermal', 'axes', 'element_property']:
            print('{0:<10} : {1}'.format(attr, getattr(self, attr)))

        return ''

    def __repr__(self):
        return '{0}({1})'.format(self.__name__, self.number)


# ==============================================================================
# 0D elements
# ==============================================================================

class MassElement(Element):

    """A 0D element for concentrated point mass.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'MassElement'


# ==============================================================================
# 1D elements
# ==============================================================================

class BeamElement(Element):

    """A 1D element that resists axial, shear, bending and torsion.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'BeamElement'


class SpringElement(Element):

    """A 1D spring element.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'SpringElement'


class TrussElement(Element):

    """A 1D element that resists axial loads.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'TrussElement'


class StrutElement(TrussElement):

    """A truss element that resists axial compressive loads.

    Parameters
    ----------
    None

    """

    def __init__(self):
        TrussElement.__init__(self)

        self.__name__ = 'StrutElement'


class TieElement(TrussElement):

    """A truss element that resists axial tensile loads.

    Parameters
    ----------
    None

    """

    def __init__(self):
        TrussElement.__init__(self)

        self.__name__ = 'TieElement'


# ==============================================================================
# 2D elements
# ==============================================================================

class ShellElement(Element):

    """A 2D element that resists axial, shear, bending and torsion.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'ShellElement'


class FaceElement(Element):

    """A 2D Face element used for special loading cases.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'FaceElement'


class MembraneElement(ShellElement):

    """A shell element that resists only axial loads.

    Parameters
    ----------
    None

    """

    def __init__(self):
        ShellElement.__init__(self)

        self.__name__ = 'MembraneElement'


# ==============================================================================
# 3D elements
# ==============================================================================

class SolidElement(Element):

    """A 3D element that resists axial, shear, bending and torsion.

    Parameters
    ----------
    None

    """

    def __init__(self):
        Element.__init__(self)

        self.__name__ = 'SolidElement'


class PentahedronElement(SolidElement):

    """A Solid element with 5 faces (extruded triangle).

    Parameters
    ----------
    None

    """

    def __init__(self):
        SolidElement.__init__(self)

        self.__name__ = 'PentahedronElement'


class TetrahedronElement(SolidElement):

    """A Solid element with 4 faces.

    Parameters
    ----------
    None

    """

    def __init__(self):
        SolidElement.__init__(self)

        self.__name__ = 'TetrahedronElement'


class HexahedronElement(SolidElement):

    """A Solid cuboid element with 6 faces (extruded rectangle).

    Parameters
    ----------
    None

    """

    def __init__(self):
        SolidElement.__init__(self)

        self.__name__ = 'HexahedronElement'
