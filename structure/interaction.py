"""
compas_fea.structure.interaction : Interaction class.
Objects for interactions between elements and/or processes across an interface.
"""


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'HeatTransfer'
]


class HeatTransfer(object):
    def __init__(self, name, amplitude, interface, sink_temp, film_coef, ambient_temp, emissivity):
        """ Heat transfer across an interface.

        Parameters:
            name (str): Heat transfer name.
            amplitude (str): Name of the heat transfer amplitude function.
            interface (str): Name of the interaction interface.
            sink_temp (float): Sink temperature in K.
            film_coef (float): Film coefficient.
            ambient_temp (float): Ambient temperature in K.
            emissivity (float): Emissivity.

        Returns:
            None
        """
        self.__name__ = 'HeatTransfer'
        self.name = name
        self.amplitude = amplitude
        self.interface = interface
        self.sink_temp = sink_temp
        self.film_coef = film_coef
        self.ambient_temp = ambient_temp
        self.emissivity = emissivity
