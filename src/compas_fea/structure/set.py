from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Set',
]


class Set(object):
    """Initialises base Set object.

    Parameters
    ----------
    name : str
        Name of the set.
    type : str
        'node', 'element', 'surface_node', surface_element'.
    selection : list, dict
        The integer keys of the nodes, elements or the element numbers and sides.
    index : int
        Set index number.

    Attributes
    ----------
    name : str
        Name of the set.
    type : str
        'node', 'element', 'surface_node', surface_element'.
    selection : list, dict
        The integer keys of the nodes, elements or the element numbers and sides.
    index : int
        Set index number.

    """

    def __init__(self, name, type, selection, index):
        self.__name__ = 'Set'
        self.name = name
        self.type = type
        self.selection = selection
        self.index = index

    def __str__(self):
        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in ['name', 'type', 'selection', 'index']:
            print('{0:<9} : {1}'.format(attr, getattr(self, attr)))

        return ''

    def __repr__(self):
        return '{0}({1})'.format(self.__name__, self.name)
