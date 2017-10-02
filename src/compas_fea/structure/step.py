"""
compas_fea.structure.step : Step class.
Analysis types to apply as Steps for the model.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'GeneralStep',
    'HeatStep',
    'ModalStep',
    'HarmonicStep',
    'BucklingStep'
]


class GeneralStep(object):

    """ Initialises GeneralStep object for use in static analysis types.

    Parameters:
        name (str): Name of the GeneralStep.
        increments (int): Number of step increments.
        factor (float): Proportionality factor on the loads and displacements.
        nlgeom (bool): Analyse non-linear geometry effects.
        displacements (list): Displacement object names (str).
        loads (list): Load object names (str).
        type (str): 'STATIC','STATIC,RIKS'.
        temperatures (str): Name of Temperature object to apply.
        duration (float): Duration of step.

    Returns:
        None
    """

    def __init__(self, name, increments=200, factor=1.0, nlgeom=True, displacements=[], loads=[], type='STATIC',
                 temperatures=None, duration=1):
        self.__name__ = 'GeneralStep'
        self.name = name
        self.increments = increments
        self.factor = factor
        self.nlgeom = nlgeom
        self.displacements = displacements
        self.loads = loads
        self.type = type
        self.temperatures = temperatures
        self.duration = duration


class HeatStep(object):

    """ Initialises HeatStep object for use in thermal analysis types.

    Parameters:
        name (str): Name of the HeatStep.
        interaction (str): Name of the HeatTransfer interaction.
        increments (int): Number of step increments.
        temp0 (float): Initial temperature of all nodes.
        dTmax (float): Maximum temperature increase per increment.
        type (str): 'HEAT TRANSFER'.
        duration (float): Duration of step.

    Returns:
        None
    """

    def __init__(self, name, interaction, increments=200, temp0=20, dTmax=1, type='HEAT TRANSFER', duration=1):
        self.__name__ = 'HeatStep'
        self.name = name
        self.interaction = interaction
        self.increments = increments
        self.temp0 = temp0
        self.dTmax = dTmax
        self.type = type
        self.duration = duration


class ModalStep(object):

    """ Initialises ModalStep object for use in modal analysis types.

    Parameters:
        name (str): Name of the ModalStep.
        modes (int): Number of modes to analyse.
        increments (int): Number of increments.
        nlgeom (bool): Analyse non-linear geometry effects.
        displacements (list): Displacement object names (str).
        type (str): 'MODAL'.

    Returns:
        None
    """

    def __init__(self, name, modes=10, increments=200, nlgeom=False, displacements=[], type='MODAL'):
        self.__name__ = 'ModalStep'
        self.name = name
        self.modes = modes
        self.increments = increments
        self.nlgeom = nlgeom
        self.displacements = displacements
        self.type = type


class HarmonicStep(object):

    """ Initialises HarmonicStep object analysis type.

    Parameters:
        name (str): Name of the HarmonicStep.
        displacements (list): Displacement object names (str).
        loads (list): Load object names (str).
        factor (float): Proportionality factor on the loads and displacements.
        freq_range (list): First and last frequencies to analyse.
        freq_steps (int): The number of frequency steps.
        damping (float): Constant harmonic damping ratio.
        type (str): 'HARMONIC'.

    Returns:
        None
    """

    def __init__(self, name, displacements=[], loads=[], factor=1.0, freq_range=None, freq_steps=None, damping=None,
                 type='HARMONIC'):
        self.__name__ = 'HarmonicStepStep'
        self.name = name
        self.displacements = displacements
        self.loads = loads
        self.factor = factor
        self.freq_range = freq_range
        self.freq_steps = freq_steps
        self.damping = damping
        self.type = type


class BucklingStep(object):

    """ Initialises BucklingStep object for use in buckling analysis types.

    Parameters:
        name (str): Name of the BucklingStep.
        modes (int): Number of modes to analyse.
        increments (int): Number of increments.
        factor (float): Proportionality factor on the loads and displacements.
        nlgeom (bool): Analyse non-linear geometry effects.
        displacements (list): Displacement object names (str).
        loads (list): Load object names (str).
        type (str): 'BUCKLE'.

    Returns:
        None
    """

    def __init__(self, name, modes=10, increments=200, factor=1.0, nlgeom=False, displacements=[], loads=[],
                 type='BUCKLE'):
        self.__name__ = 'BucklingStep'
        self.name = name
        self.modes = modes
        self.increments = increments
        self.factor = factor
        self.nlgeom = nlgeom
        self.displacements = displacements
        self.loads = loads
        self.type = type
