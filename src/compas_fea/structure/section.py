
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'AngleSection',
    'BoxSection',
    'CircularSection',
    'GeneralSection',
    'ISection',
    'PipeSection',
    'RectangularSection',
    'ShellSection',
    'SolidSection',
    'TrapezoidalSection',
    'TrussSection',
    'StrutSection',
    'TieSection',
    'SpringSection'
]


# ==============================================================================
# 1D
# ==============================================================================

class AngleSection(object):

    """ Equal angle cross-section for beam elements.

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

    Returns
    -------
    None

    Notes
    -----
    - Ixy not yet calculated.

    """

    def __init__(self, name, b, h, t):
        xc = (b**2 + h * t - t**2) / (2. * (b + h - t))
        yc = (h**2 + b * t - t**2) / (2. * (b + h - t))
        A = t * (b + h - t)
        Ixx = (1. / 3) * (b * h**3 - (b - t) * (h - t)**3) - A * (h - yc)**2
        Iyy = (1. / 3) * (h * b**3 - (h - t) * (b - t)**3) - A * (b - xc)**2
        J = (1. / 3) * (h + b - t) * t**3
        self.__name__ = 'AngleSection'
        self.geometry = {'b': b, 'h': h, 't': t, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}
        self.name = name


class BoxSection(object):

    """ Hollow rectangular box cross-section for beam elements.

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

    Returns
    -------
    None

    """

    def __init__(self, name, b, h, tw, tf):
        A = b * h - (b - 2 * tw) * (h - 2 * tf)
        Ixx = (b * h**3) / 12. - ((b - 2 * tw) * (h - 2 * tf)**3) / 12.
        Iyy = (h * b**3) / 12. - ((h - 2 * tf) * (b - 2 * tw)**3) / 12.
        Ap = (h - tf) * (b - tw)
        p = 2 * ((h - tf) / tw + (b - tw) / tf)
        J = 4 * (Ap**2) / p
        self.__name__ = 'BoxSection'
        self.geometry = {'b': b, 'h': h, 'tw': tw, 'tf': tf, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}
        self.name = name


class CircularSection(object):

    """ Solid circular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    r : float
        Radius.

    Returns
    -------
    None

    """

    def __init__(self, name, r):
        D = 2 * r
        A = 0.25 * pi * D**2
        Ixx = (pi * D**4) / 64.
        Iyy = (pi * D**4) / 64.
        J = (pi * D**4) / 32
        self.__name__ = 'CircularSection'
        self.geometry = {'r': r, 'D': D, 'A': A, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0, 'J': J}
        self.name = name


class GeneralSection(object):

    """ General cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.
    Ixx : float
        Second moment of area about axis 1-1.
    Ixy : float
        Cross moment of area.
    Iyy : float
        Second moment of area about axis 2-2.
    J : float
        Torsional rigidity.
    g0 : float
        Sectorial moment.
    gw : float
        Warping constant.

    Returns
    -------
    None

    """

    def __init__(self, name, A, Ixx, Ixy, Iyy, J, g0, gw):
        self.__name__ = 'GeneralSection'
        self.geometry = {'A': A, 'Ixx': Ixx, 'Ixy': Ixy, 'Iyy': Iyy, 'J': J, 'g0': g0, 'gw': gw}
        self.name = name


class ISection(object):

    """ Equal flanged I-section for beam elements.

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

    Returns
    -------
    None

    """

    def __init__(self, name, b, h, tw, tf):
        A = 2 * b * tf + (h - 2 * tf) * tw
        Ixx = (tw * (h - 2 * tf)**3) / 12. + 2 * ((tf**3) * b / 12. + b * tf * (h / 2. - tf / 2.)**2)
        Iyy = ((h - 2 * tf) * tw**3) / 12. + 2 * ((b**3) * tf / 12.)
        J = (1. / 3) * (2 * b * tf**3 + (h - tf) * tw**3)
        self.__name__ = 'ISection'
        self.geometry = {
            'b': b, 'h': h, 'tw': tw, 'tf': tf, 'c': h / 2., 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}
        self.name = name


class PipeSection(object):

    """ Hollow circular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    r : float
        Outer radius.
    t : float
        Wall thickness.

    Returns
    -------
    None

    """

    def __init__(self, name, r, t):
        D = 2 * r
        A = 0.25 * pi * (D**2 - (D - 2 * t)**2)
        Ixx = 0.25 * pi * (r**4 - (r - t)**4)
        Iyy = 0.25 * pi * (r**4 - (r - t)**4)
        J = (2. / 3) * pi * (r + 0.5 * t) * t**3
        self.__name__ = 'PipeSection'
        self.geometry = {'r': r, 't': t, 'D': D, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}
        self.name = name


class RectangularSection(object):

    """ Solid rectangular cross-section for beam elements.

    Parameters
    ----------
    name : str
        Section name.
    b : float
        Width.
    h : float
        Height.

    Returns
    -------
    None

    """

    def __init__(self, name, b, h):
        A = b * h
        Ixx = (1 / 12.) * b * h**3
        Iyy = (1 / 12.) * h * b**3
        l1 = max([b, h])
        l2 = min([b, h])
        Avy = 0.833 * A
        Avx = 0.833 * A
        J = (l1 * l2**3) * (0.33333 - 0.21 * (l2 / l1) * (1 - (l2**4) / (12 * l1**4)))
        self.__name__ = 'RectangularSection'
        self.geometry = {'b': b, 'h': h, 'A': A, 'J': J, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0, 'Avx': Avx, 'Avy': Avy}
        self.name = name


class TrapezoidalSection(object):

    """ Solid trapezoidal cross-section for beam elements.

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

    Returns
    -------
    None

    Notes
    -----
    - J not yet calculated.

    """

    def __init__(self, name, b1, b2, h):
        c = (h * (2 * b2 + b1)) / (3. * (b1 + b2))
        A = 0.5 * (b1 + b2) * h
        Ixx = (1 / 12.) * (3 * b2 + b1) * h**3
        Iyy = (1 / 48.) * h * (b1 + b2) * (b2**2 + 7 * b1**2)
        self.__name__ = 'TrapezoidalSection'
        self.geometry = {'b1': b1, 'b2': b2, 'h': h, 'A': A, 'c': c, 'Ixx': Ixx, 'Iyy': Iyy, 'Ixy': 0}
        self.name = name


class TrussSection(object):

    """ For use with truss elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    Returns
    -------
    None

    """

    def __init__(self, name, A):
        self.__name__ = 'TrussSection'
        self.geometry = {'A': A}
        self.name = name


class StrutSection(TrussSection):

    """ For use with strut elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    Returns
    -------
    None

    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)
        self.__name__ = 'StrutSection'


class TieSection(TrussSection):

    """ For use with tie elements.

    Parameters
    ----------
    name : str
        Section name.
    A : float
        Area.

    Returns
    -------
    None

    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)
        self.__name__ = 'TieSection'


class SpringSection(object):

    """ For use with spring elements. Requires either a stiffness dictonary for
    linear springs, or forces and displacement lists for non-linear springs.

    Parameters
    ----------
    name : str
        Section name.
    forces : dic
        Forces data for non-linear springs.
    displacements : dic
        Displacements data for non-linear springs.
    stiffness : dic
        Elastic stiffness for linear springs. The dictionary keys show the spring
        axis and the values represent the stifness.

    Returns
    -------
    None

    Notes
    -----
    - Force and displacement data should start from negative to positive.

    """

    def __init__(self, name, forces={}, displacements={}, stiffness={}):
        self.__name__ = 'SpringSection'
        self.name = name
        self.geometry = None
        self.forces = forces
        self.displacements = displacements
        self.stiffness = stiffness


# ==============================================================================
# 2D
# ==============================================================================

class ShellSection(object):

    """ Section for shell and membrane elements.

    Parameters
    ----------
    name : str
        Section name.
    t : float
        Thickness.

    Returns
    -------
    None

    """

    def __init__(self, name, t):
        self.__name__ = 'ShellSection'
        self.geometry = {'t': t}
        self.name = name


# ==============================================================================
# 3D
# ==============================================================================

class SolidSection(object):

    """ Section for solid elements.

    Parameters
    ----------
    name : str
        Section name.


    Returns
    -------
    None

    """

    def __init__(self, name):
        self.__name__ = 'SolidSection'
        self.geometry = None
        self.name = name
