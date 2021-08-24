from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Misc',
    'Amplitude',
    'Temperatures'
]


class Misc(object):
    """Initialises base Misc object.

    Parameters
    ----------
    name : str
        Misc object name.

    Returns
    -------
    None

    """

    def __init__(self, name):

        self.__name__ = 'Misc'
        self.name = name
        self.attr_list = ['name']

    def __str__(self):

        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in self.attr_list:
            print('{0:<10} : {1}'.format(attr, getattr(self, attr)))

        return ''


class Amplitude(Misc):
    """Initialises an Amplitude object to act as a discretised function f(x).

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

    def __init__(self, name, values=[[0, 0], [1, 1]]):
        Misc.__init__(self, name=name)

        self.__name__ = 'Amplitude'
        self.name = name
        self.values = values
        self.attr_list.extend(['values'])


class Temperatures(Misc):
    """Define nodal temperatures data.

    Parameters
    ----------
    name : str
        Temperature object name.
    file : str
        Path of nodal temperatures file to extract data from.
    values : list
        List of [[node, temperature, time], ...] data.
    tend : float
        End time in seconds to read data till.

    Returns
    -------
    None

    """

    def __init__(self, name, file=None, values=[], tend=None):
        Misc.__init__(self, name=name)

        self.__name__ = 'Temperatures'
        self.name = name
        self.file = file
        self.values = values
        self.tend = tend
        self.attr_list.extend(['file', 'values', 'tend'])
