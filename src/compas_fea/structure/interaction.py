from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Interaction',
    'HeatTransfer',
]


class Interaction(object):
    """Initialises base Interaction object.

    Parameters
    ----------
    name : str
        Interaction object name.

    Returns
    -------
    None

    """

    def __init__(self, name):
        self.__name__ = 'Interaction'
        self.name = name
        self.attr_list = ['name']

    def __str__(self):
        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in self.attr_list:
            print('{0:<12} : {1}'.format(attr, getattr(self, attr)))

        return ''


class HeatTransfer(Interaction):
    """Heat transfer across an interface.

    Parameters
    ----------
    name : str
        Heat transfer name.
    amplitude : str
        Name of the heat transfer amplitude function.
    interface : str
        Name of the interaction interface.
    sink_temp : float
        Sink temperature in K.
    film_coef : float
        Film coefficient.
    ambient_temp : float
        Ambient temperature in K.
    emissivity : float
        Emissivity.

    Returns
    -------
    None

    """

    def __init__(self, name, amplitude, interface, sink_temp, film_coef, ambient_temp, emissivity):
        Interaction.__init__(self, name=name)

        self.__name__ = 'HeatTransfer'
        self.name = name
        self.amplitude = amplitude
        self.interface = interface
        self.sink_temp = sink_temp
        self.film_coef = film_coef
        self.ambient_temp = ambient_temp
        self.emissivity = emissivity
        self.attr_list.extend(['amplitude', 'interface', 'sink_temp', 'film_coef', 'ambient_temp', 'emissivity'])
