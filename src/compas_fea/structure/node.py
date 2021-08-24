from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Node',
]


class Node(object):
    """Initialises base Node object.

    Parameters
    ----------
    key : int
        Node key number.
    xyz : list
        [x, y, z] co-ordinates of the node.
    ex : list
        Node's local x axis.
    ey : list
        Node's local y axis.
    ez : list
        Node's local z axis.
    mass : float
        Mass in kg associated with the node.

    Attributes
    ----------
    key : int
        Node key number.
    x : float
        x co-ordinates of the node.
    y : float
        y co-ordinates of the node.
    z : float
        z co-ordinates of the node.
    ex : list
        Node's local x axis.
    ey : list
        Node's local y axis.
    ez : list
        Node's local z axis.
    mass : float
        Mass in kg associated with the node.

    """

    def __init__(self, key, xyz, ex, ey, ez, mass):

        self.__name__ = 'Node'
        self.key = key
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.mass = mass

    def __str__(self):
        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in ['key', 'x', 'y', 'z', 'ex', 'ey', 'ez', 'mass']:
            print('{0:<5} : {1}'.format(attr, getattr(self, attr)))

        return ''

    def __repr__(self):
        return '{0}({1})'.format(self.__name__, self.key)
