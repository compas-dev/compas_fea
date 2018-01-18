
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'GeneralStep',
    'HeatStep',
    'ModalStep',
    'HarmonicStep',
    'BucklingStep'
]


class GeneralStep(object):

    """ Initialises GeneralStep object for use in static analysis types.

    Parameters
    ----------
    name : str
        Name of the GeneralStep.
    increments : int
        Number of step increments.
    iterations : int
        Number of step iterations.
    factor : float
        Proportionality factor on the loads and displacements.
    nlgeom : bool
        Analyse non-linear geometry effects.
    displacements : list
        Displacement object names (str).
    loads : list
        Load object names (str).
    type : str
        'static','static,riks'.
    temperatures : str
        Name of Temperature object to apply.
    duration : float
        Duration of step.
    tolerance : float
        A tolerance for analysis solvers.

    Returns
    -------
    None

    """

    def __init__(self, name, increments=100, iterations=10, factor=1.0, nlgeom=True, displacements=[], loads=[],
                 type='static', temperatures=None, duration=1, tolerance=0.01):
        self.__name__ = 'GeneralStep'
        self.name = name
        self.increments = increments
        self.iterations = iterations
        self.factor = factor
        self.nlgeom = nlgeom
        self.displacements = displacements
        self.loads = loads
        self.type = type
        self.temperatures = temperatures
        self.duration = duration
        self.tolerance = tolerance


class HeatStep(object):

    """ Initialises HeatStep object for use in thermal analysis types.

    Parameters
    ----------
    name : str
        Name of the HeatStep.
    interaction : str
        Name of the HeatTransfer interaction.
    increments : int
        Number of step increments.
    temp0 : float
        Initial temperature of all nodes.
    dTmax : float
        Maximum temperature increase per increment.
    type : str
        'HEAT TRANSFER'.
    duration : float
        Duration of step.

    Returns
    -------
    None

    """

    def __init__(self, name, interaction, increments=100, temp0=20, dTmax=1, type='HEAT TRANSFER', duration=1):
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

    Parameters
    ----------
    name : str
        Name of the ModalStep.
    modes : int
        Number of modes to analyse.
    increments : int
        Number of increments.
    displacements : list
        Displacement object names (str).
    type : str
        'modal'.

    Returns
    -------
    None

    """

    def __init__(self, name, modes=10, increments=100, displacements=[], type='modal'):
        self.__name__ = 'ModalStep'
        self.name = name
        self.modes = modes
        self.increments = increments
        self.displacements = displacements
        self.type = type


class HarmonicStep(object):

    """ Initialises HarmonicStep object analysis type.

    Parameters
    ----------
    name : str
        Name of the HarmonicStep.
    freq_range : list
        First and last frequencies to analyse.
    freq_steps : int
        The number of equally spaced frequency steps.
    displacements : list
        Displacement object names (str).
    loads : list
        Load object names (str).
    factor : float
        Proportionality factor on the loads and displacements.
    damping : float
        Constant harmonic damping ratio.
    type : str
        'harmonic'.

    Returns
    -------
    None

    """

    def __init__(self, name, freq_range, freq_steps, displacements=[], loads=[], factor=1.0, damping=None,
                 type='harmonic'):
        self.__name__ = 'HarmonicStep'
        self.name = name
        self.freq_range = freq_range
        self.freq_steps = freq_steps
        self.displacements = displacements
        self.loads = loads
        self.factor = factor
        self.damping = damping
        self.type = type


class BucklingStep(object):

    """ Initialises BucklingStep object for use in buckling analysis types.

    Parameters
    ----------
    name : str
        Name of the BucklingStep.
    modes : int
        Number of modes to analyse.
    increments : int
        Number of increments.
    factor : float
        Proportionality factor on the loads and displacements.
    displacements : list
        Displacement object names (str).
    loads : list
        Load object names (str).
    type : str
        'buckle'.

    Returns
    -------
    None

    """

    def __init__(self, name, modes=10, increments=100, factor=1.0, displacements=[], loads=[], type='buckle'):
        self.__name__ = 'BucklingStep'
        self.name = name
        self.modes = modes
        self.increments = increments
        self.factor = factor
        self.displacements = displacements
        self.loads = loads
        self.type = type
