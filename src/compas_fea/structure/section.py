from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Section',
    'AngleSection',
    'BoxSection',
    'CircularSection',
    'GeneralSection',
    'ISection',
    'PipeSection',
    'RectangularSection',
    'ShellSection',
    'MembraneSection',
    'SolidSection',
    'TrapezoidalSection',
    'TrussSection',
    'StrutSection',
    'TieSection',
    'SpringSection',
    'MassSection'
]


class Section(object):
    """Initialises base Section object.

    Parameters
    ----------
    name : str
        Section object name.

    Attributes
    ----------
    name : str
        Section object name.
    geometry : dict
        Geometry of the Section.

    """

    def __init__(self, name):

        self.__name__ = 'Section'
        self.name = name
        self.geometry = {}

    def __str__(self):

        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))
        print('name  : {0}'.format(self.name))

        for i, j in self.geometry.items():
            print('{0:<5} : {1}'.format(i, j))

        return ''

    def __repr__(self):

        return '{0}({1})'.format(self.__name__, self.name)


# ==============================================================================
# 1D
# ==============================================================================

class AngleSection(Section):
    """Uniform thickness angle cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b : float
        Width.
    h : float
        Height.
    t : float
        Thickness.

    Notes
    -----
    - Ixy not yet calculated.

    """

    def __init__(self, name, b, h, t):
        Section.__init__(self, name=name)

        p = 2. * (b + h - t)
        xc = (b**2 + h * t - t**2) / p
        yc = (h**2 + b * t - t**2) / p
        A = t * (b + h - t)
        Ixx = (1. / 3) * (b * h**3 - (b - t) * (h - t)**3) - A * (h - yc)**2
        Iyy = (1. / 3) * (h * b**3 - (h - t) * (b - t)**3) - A * (b - xc)**2
        J = (1. / 3) * (h + b - t) * t**3

        self.__name__ = 'AngleSection'
        self.name = name
        self.geometry = {'b': b, 'h': h, 't': t, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': None}


class BoxSection(Section):
    """Hollow rectangular box cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b : float
        Width.
    h : float
        Height.
    tw : float
        Web thickness.
    tf : float
        Flange thickness.

    """

    def __init__(self, name, b, h, tw, tf):
        Section.__init__(self, name=name)

        A = b * h - (b - 2 * tw) * (h - 2 * tf)
        Ap = (h - tf) * (b - tw)
        Ixx = (b * h**3) / 12. - ((b - 2 * tw) * (h - 2 * tf)**3) / 12.
        Iyy = (h * b**3) / 12. - ((h - 2 * tf) * (b - 2 * tw)**3) / 12.
        p = 2 * ((h - tf) / tw + (b - tw) / tf)
        J = 4 * (Ap**2) / p

        self.__name__ = 'BoxSection'
        self.name = name
        self.geometry = {'b': b, 'h': h, 'tw': tw, 'tf': tf, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}


class CircularSection(Section):
    """Solid circular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    r : float
        Radius.

    """

    def __init__(self, name, r):
        Section.__init__(self, name=name)

        D = 2 * r
        A = 0.25 * pi * D**2
        Ixx = Iyy = (pi * D**4) / 64.
        J = (pi * D**4) / 32

        self.__name__ = 'CircularSection'
        self.name = name
        self.geometry = {'r': r, 'D': D, 'A': A, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0, 'J': J}


class GeneralSection(Section):
    """General cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.
    Ixx : float
        Second moment of area about axis x-x.
    Ixy : float
        Cross moment of area.
    Iyy : float
        Second moment of area about axis y-y.
    J : float
        Torsional rigidity.
    g0 : float
        Sectorial moment.
    gw : float
        Warping constant.

    """

    def __init__(self, name, A, Ixx, Ixy, Iyy, J, g0, gw):
        Section.__init__(self, name=name)

        self.__name__ = 'GeneralSection'
        self.name = name
        self.geometry = {'A': A, 'Ixx': Ixx, 'Ixy': Ixy, 'Iyy': Iyy, 'J': J, 'g0': g0, 'gw': gw}


class ISection(Section):
    """Equal flanged I-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b : float
        Width.
    h : float
        Height.
    tw : float
        Web thickness.
    tf : float
        Flange thickness.

    """

    def __init__(self, name, b, h, tw, tf):
        Section.__init__(self, name=name)

        A = 2 * b * tf + (h - 2 * tf) * tw
        Ixx = (tw * (h - 2 * tf)**3) / 12. + 2 * ((tf**3) * b / 12. + b * tf * (h / 2. - tf / 2.)**2)
        Iyy = ((h - 2 * tf) * tw**3) / 12. + 2 * ((b**3) * tf / 12.)
        J = (1. / 3) * (2 * b * tf**3 + (h - tf) * tw**3)

        self.__name__ = 'ISection'
        self.name = name
        self.geometry = {'b': b, 'h': h, 'tw': tw, 'tf': tf, 'c': h/2., 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}


class PipeSection(Section):

    """Hollow circular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    r : float
        Outer radius.
    t : float
        Wall thickness.

    """

    def __init__(self, name, r, t):
        Section.__init__(self, name=name)

        D = 2 * r
        A = 0.25 * pi * (D**2 - (D - 2 * t)**2)
        Ixx = Iyy = 0.25 * pi * (r**4 - (r - t)**4)
        J = (2. / 3) * pi * (r + 0.5 * t) * t**3

        self.__name__ = 'PipeSection'
        self.name = name
        self.geometry = {'r': r, 't': t, 'D': D, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}


class RectangularSection(Section):
    """Solid rectangular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b : float
        Width.
    h : float
        Height.

    """

    def __init__(self, name, b, h):
        Section.__init__(self, name=name)

        A = b * h
        Ixx = (1 / 12.) * b * h**3
        Iyy = (1 / 12.) * h * b**3
        l1 = max([b, h])
        l2 = min([b, h])
        # Avy = 0.833 * A
        # Avx = 0.833 * A
        J = (l1 * l2**3) * (0.33333 - 0.21 * (l2 / l1) * (1 - (l2**4) / (12 * l1**4)))

        self.__name__ = 'RectangularSection'
        self.name = name
        self.geometry = {'b': b, 'h': h, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}


class TrapezoidalSection(Section):
    """Solid trapezoidal cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b1 : float
        Width at bottom.
    b2 : float
        Width at top.
    h : float
        Height.

    Notes
    -----
    - J not yet calculated.

    """

    def __init__(self, name, b1, b2, h):
        Section.__init__(self, name=name)

        c = (h * (2 * b2 + b1)) / (3. * (b1 + b2))
        A = 0.5 * (b1 + b2) * h
        Ixx = (1 / 12.) * (3 * b2 + b1) * h**3
        Iyy = (1 / 48.) * h * (b1 + b2) * (b2**2 + 7 * b1**2)

        self.__name__ = 'TrapezoidalSection'
        self.name = name
        self.geometry = {'b1': b1, 'b2': b2, 'h': h, 'A': A, 'c': c, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0, 'J': None}


class TrussSection(Section):
    """For use with truss elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    """

    def __init__(self, name, A):
        Section.__init__(self, name=name)

        self.__name__ = 'TrussSection'
        self.name = name
        self.geometry = {'A': A, 'Ixx': 0, 'Iyy': 0, 'Ixy': 0, 'J': 0}


class StrutSection(TrussSection):
    """For use with strut elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)

        self.__name__ = 'StrutSection'


class TieSection(TrussSection):
    """For use with tie elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)

        self.__name__ = 'TieSection'


class SpringSection(Section):
    """For use with spring elements.

    Parameters
    ----------
    name : str
        Section name.
    forces : dict
        Forces data for non-linear springs.
    displacements : dict
        Displacements data for non-linear springs.
    stiffness : dict
        Elastic stiffness for linear springs.

    Notes
    -----
    - Force and displacement data should range from negative to positive values.
    - Requires either a stiffness dict for linear springs, or forces and displacement lists for non-linear springs.
    - Directions are 'axial', 'lateral', 'rotation'.

    """

    def __init__(self, name, forces={}, displacements={}, stiffness={}):
        Section.__init__(self, name=name)

        self.__name__ = 'SpringSection'
        self.name = name
        self.geometry = None
        self.forces = forces
        self.displacements = displacements
        self.stiffness = stiffness


# ==============================================================================
# 2D
# ==============================================================================

class ShellSection(Section):
    """Section for shell elements.

    Parameters
    ----------
    name : str
        Section name.
    t : float
        Thickness.

    """

    def __init__(self, name, t):
        Section.__init__(self, name=name)

        self.__name__ = 'ShellSection'
        self.name = name
        self.geometry = {'t': t}


class MembraneSection(Section):
    """Section for membrane elements.

    Parameters
    ----------
    name : str
        Section name.
    t : float
        Thickness.

    """

    def __init__(self, name, t):
        Section.__init__(self, name=name)

        self.__name__ = 'MembraneSection'
        self.name = name
        self.geometry = {'t': t}


# ==============================================================================
# 3D
# ==============================================================================

class SolidSection(Section):
    """Section for solid elements.

    Parameters
    ----------
    name : str
        Section name.

    """

    def __init__(self, name):
        Section.__init__(self, name=name)

        self.__name__ = 'SolidSection'
        self.name = name
        self.geometry = None


# ==============================================================================
# 0D
# ==============================================================================

class MassSection(Section):
    """Section for mass elements.

    Parameters
    ----------
    name : str
        Section name.

    """

    def __init__(self, name):
        Section.__init__(self, name=name)

        self.__name__ = 'MassSection'
        self.name = name
        self.geometry = None
