
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'GeneralStep',
    # 'HeatStep',
    'ModalStep',
    'HarmonicStep',
    'BucklingStep'
]


class GeneralStep(object):

    """ Initialises GeneralStep object for use in a static analysis.

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
    nlmat : bool
        Analyse non-linear material effects.
    displacements : list
        Displacement object names.
    loads : list
        Load object names.
    type : str
        'static','static,riks'.
    tolerance : float
        A tolerance for analysis solvers.
    state : str
        Limit state 'sls' or 'uls' for design.

    Returns
    -------
    None

    """

    def __init__(self, name, increments=100, iterations=100, factor=1.0, nlgeom=True, nlmat=True, displacements=[],
                 loads=[], type='static', tolerance=0.01, state='sls'):
        self.__name__ = 'GeneralStep'
        self.name = name
        self.increments = increments
        self.iterations = iterations
        self.factor = factor
        self.nlgeom = nlgeom
        self.nlmat = nlmat
        self.displacements = displacements
        self.loads = loads
        self.type = type
        self.tolerance = tolerance
        self.state = state


class HeatStep(object):

    """ Initialises HeatStep object for use in a thermal analysis.

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
        'heat transfer'.
    duration : float
        Duration of step.

    Returns
    -------
    None

    """

    def __init__(self, name, interaction, increments=100, temp0=20, dTmax=1, type='heat transfer', duration=1):
        self.__name__ = 'HeatStep'
        self.name = name
        self.interaction = interaction
        self.increments = increments
        self.temp0 = temp0
        self.dTmax = dTmax
        self.type = type
        self.duration = duration


class ModalStep(object):

    """ Initialises ModalStep object for use in a modal analysis.

    Parameters
    ----------
    name : str
        Name of the ModalStep.
    modes : int
        Number of modes to analyse.
    increments : int
        Number of increments.
    displacements : list
        Displacement object names.
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

    """ Initialises HarmonicStep object for use in a harmonic analysis.

    Parameters
    ----------
    name : str
        Name of the HarmonicStep.
    freq_list : list
        Sorted list of frequencies to analyse.
    displacements : list
        Displacement object names.
    loads : list
        Load object names.
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

    def __init__(self, name, freq_list, displacements=[], loads=[], factor=1.0, damping=None,
                 type='harmonic'):
        self.__name__ = 'HarmonicStep'
        self.name = name
        self.freq_list = freq_list
        self.displacements = displacements
        self.loads = loads
        self.factor = factor
        self.damping = damping
        self.type = type


class BucklingStep(object):

    """ Initialises BucklingStep object for use in a buckling analysis.

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
        Displacement object names.
    loads : list
        Load object names.
    type : str
        'buckle'.
    step : str
        Step to copy loads and displacements from.

    Returns
    -------
    None

    """

    def __init__(self, name, modes=10, increments=100, factor=1.0, displacements=[], loads=[], type='buckle', step=None):
        self.__name__ = 'BucklingStep'
        self.name = name
        self.modes = modes
        self.increments = increments
        self.factor = factor
        self.displacements = displacements
        self.loads = loads
        self.type = type
        self.step = step
