
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Amplitude',
    # 'Temperatures'
]


class Amplitude(object):

    """ Initialises an Amplitude object to act as a discretised function f(x).

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


# class Temperatures(object):

#     """ Define nodal temperatures.

#     Parameters
#     ----------
#     name : str
#         Temperature object name.
#     file : str
#         Path of nodal temperatures file.
#     values : list
#         List of [node, temperature, time] data.
#     time_end : int
#         End time in seconds.

#     Returns
#     -------
#     None

#     """

#     def __init__(self, name, file=None, values=[], time_end=None):
#         self.__name__ = 'Temperatures'
#         self.name = name
#         self.file = file
#         self.values = values
#         self.time_end = time_end
