"""
compas_fea.structure.section : Section class.
Section definitions for 1D, 2D and 3D finite elements.
"""

from __future__ import print_function
from __future__ import absolute_import

from math import pi


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


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
    'TieSection'
]


# ==============================================================================
# 1D
# ==============================================================================

class AngleSection(object):

    """ Equal angle cross-section for beam elements.

    Parameters:
        name (str): Section name.
        b (float): Width.
        h (float): Height.
        t (float): Thickness.

    Returns:
        None
    """

    def __init__(self, name, b, h, t):
        xc = (b**2 + h * t - t**2) / (2. * (b + h - t))
        yc = (h**2 + b * t - t**2) / (2. * (b + h - t))
        A = t * (b + h - t)
        I11 = (1. / 3) * (b * h**3 - (b - t) * (h - t)**3) - A * (h - yc)**2
        I22 = (1. / 3) * (h * b**3 - (h - t) * (b - t)**3) - A * (b - xc)**2
        self.__name__ = 'AngleSection'
        self.geometry = {'b': b, 'h': h, 't': t, 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class BoxSection(object):

    """ Hollow rectangular box cross-section for beam elements.

    Parameters:
        name (str): Section name.
        b (float): Width.
        h (float): Height.
        tw (float): Web thickness.
        tf (float): Flange thickness.

    Returns:
        None
    """

    def __init__(self, name, b, h, tw, tf):
        A = b * h - (b - 2 * tw) * (h - 2 * tf)
        I11 = (b * h**3) / 12. - ((b - 2 * tw) * (h - 2 * tf)**3) / 12.
        I22 = (h * b**3) / 12. - ((h - 2 * tf) * (b - 2 * tw)**3) / 12.
        self.__name__ = 'BoxSection'
        self.geometry = {'b': b, 'h': h, 'tw': tw, 'tf': tf, 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class CircularSection(object):

    """ Solid circular cross-section for beam elements.

    Parameters:
        name (str): Section name.
        r (float): Radius.

    Returns:
        None
    """

    def __init__(self, name, r):
        D = 2 * r
        A = 0.25 * pi * D**2
        I11 = (pi * D**4) / 64.
        I22 = (pi * D**4) / 64.
        self.__name__ = 'CircularSection'
        self.geometry = {'r': r, 'D': D, 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class GeneralSection(object):

    """ General cross-section for beam elements.

    Parameters:
        name (str): Section name.
        A (float): Area.
        I11 (float): Second moment of area about axis 1-1.
        I12 (float): Cross moment of area.
        I22 (float): Second moment of area about axis 2-2.
        J (float): Torsional rigidity.
        g0 (float): Sectorial moment.
        gw (float): Warping constant.

    Returns:
        None
    """

    def __init__(self, name, A, I11, I12, I22, J, g0, gw):
        self.__name__ = 'GeneralSection'
        self.geometry = {'A': A, 'I11': I11, 'I12': I12, 'I22': I22, 'J': J, 'g0': g0, 'gw': gw}
        self.name = name


class ISection(object):

    """ Equal flanged I-section for beam elements.

    Parameters:
        name (str): Section name.
        b (float): Width.
        h (float): Height.
        tw (float): Web thickness.
        tf (float): Flange thickness.

    Returns:
        None
    """

    def __init__(self, name, b, h, tw, tf):
        A = 2 * b * tf + (h - 2 * tf) * tw
        I11 = (tw * (h - 2 * tf)**3) / 12. + 2 * ((tf**3) * b / 12. + b * tf * (h / 2. - tf / 2.)**2)
        I22 = ((h - 2 * tf) * tw**3) / 12. + 2 * ((b**3) * tf / 12.)
        self.__name__ = 'ISection'
        self.geometry = {'b': b, 'h': h, 'tw': tw, 'tf': tf, 'c': h / 2., 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class PipeSection(object):

    """ Hollow circular cross-section for beam elements.

    Parameters:
        name (str): Section name.
        r (float): Outer radius.
        t (float): Wall thickness.

    Returns:
        None
    """

    def __init__(self, name, r, t):
        D = 2 * r
        A = 0.25 * pi * (D**2 - (D - 2 * t)**2)
        I11 = 0.25 * pi * (r**4 - (r - t)**4)
        I22 = 0.25 * pi * (r**4 - (r - t)**4)
        self.__name__ = 'PipeSection'
        self.geometry = {'r': r, 't': t, 'D': D, 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class RectangularSection(object):

    """ Solid rectangular cross-section for beam elements.

    Parameters:
        name (str): Section name.
        b (float): Width.
        h (float): Height.

    Returns:
        None
    """

    def __init__(self, name, b, h):
        A = b * h
        I11 = (1 / 12.) * b * h**3
        I22 = (1 / 12.) * h * b**3
        self.__name__ = 'RectangularSection'
        self.geometry = {'b': b, 'h': h, 'A': A, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class TrapezoidalSection(object):

    """ Solid trapezoidal cross-section for beam elements.

    Parameters:
        name (str): Section name.
        b1 (float): Width at bottom.
        b2 (float): Width at top.
        h (float): Height.

    Returns:
        None
    """

    def __init__(self, name, b1, b2, h):
        c = (h * (2 * b2 + b1)) / (3. * (b1 + b2))
        A = 0.5 * (b1 + b2) * h
        I11 = (1 / 12.) * (3 * b2 + b1) * h**3
        I22 = (1 / 48.) * h * (b1 + b2) * (b2**2 + 7 * b1**2)
        self.__name__ = 'TrapezoidalSection'
        self.geometry = {'b1': b1, 'b2': b2, 'h': h, 'A': A, 'c': c, 'I11': I11, 'I22': I22, 'I12': 0}
        self.name = name


class TrussSection(object):

    """ For use with truss elements.

    Parameters:
        name (str): Section name.
        A (float): Area.

    Returns:
        None
    """

    def __init__(self, name, A):
        self.__name__ = 'TrussSection'
        self.geometry = {'A': A}
        self.name = name


class StrutSection(TrussSection):

    """ For use with strut elements.

    Parameters:
        name (str): Section name.
        A (float): Area.

    Returns:
        None
    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)
        self.__name__ = 'StrutSection'


class TieSection(TrussSection):

    """ For use with tie elements.

    Parameters:
        name (str): Section name.
        A (float): Area.

    Returns:
        None
    """

    def __init__(self, name, A):
        TrussSection.__init__(self, name=name, A=A)
        self.__name__ = 'TieSection'


# ==============================================================================
# 2D
# ==============================================================================

class ShellSection(object):

    """ Section for shell and membrane elements.

    Parameters:
        name (str): Section name.
        t (float): Thickness.

    Returns:
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

    Parameters:
        name (str): Section name.

    Returns:
        None
    """

    def __init__(self, name):
        self.__name__ = 'SolidSection'
        self.geometry = None
        self.name = name
