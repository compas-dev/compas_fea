"""
compas_fea.structure.misc : Misc classes.
Miscellaneous objects.
"""


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'Amplitude',
    'Temperature'
]


class Amplitude(object):

    def __init__(self, name, values=[[0., 0.], [1., 1.]]):
        """ Initialises Amplitude object to act as discretised function f(x).

        Parameters:
            name (str): Amplitude object name.
            values (list): Amplitude function value pairs [[x0, y0], [x1, y1], ..].

        Returns:
            None
        """
        self.__name__ = 'Amplitude'
        self.name = name
        self.values = values


class Temperature(object):

    def __init__(self, name, file, tend=None):
        """ Define nodal temperatures from a time dependent data file.

        Parameters:
            name (str): Temperature object name.
            file (str): Location of nodal temperatures file.
            tend (int): End time in seconds.

        Returns:
            None
        """
        self.__name__ = 'Temperature'
        self.name = name
        self.file = file
        self.tend = tend
