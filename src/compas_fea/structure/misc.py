
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Amplitude',
    'Temperature'
]


class Amplitude(object):

    """ Initialises Amplitude object to act as discretised function f(x).

    Parameters
    ----------
    name : str
        Amplitude object name.
    values : list
        Amplitude function value pairs [[x0, y0], [x1, y1], ..].

    Returns
    -------
    None

    """

    def __init__(self, name, values=[[0., 0.], [1., 1.]]):
        self.__name__ = 'Amplitude'
        self.name = name
        self.values = values


class Temperature(object):

    """ Define nodal temperatures from a time dependent data file.

    Parameters
    ----------
    name : str
        Temperature object name.
    file : str
        Location of nodal temperatures file.
    tend : int
        End time in seconds.

    Returns
    -------
    None

    """

    def __init__(self, name, file, tend=None):
        self.__name__ = 'Temperature'
        self.name = name
        self.file = file
        self.tend = tend
