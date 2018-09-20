
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Step',
    'GeneralStep',
    # 'HeatStep',
    'ModalStep',
    'HarmonicStep',
    'BucklingStep',
    'AcousticStep'
]


class Step(object):

    """ Initialises base Step object.

    Parameters
    ----------
    name : str
        Name of the Step object.

    Returns
    -------
    None

    """

    def __init__(self, name):

        self.__name__ = 'StepObject'
        self.name = name
        self.attr_list = ['name']

    def __str__(self):

        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 10))

        for attr in self.attr_list:
            print('{0:<13} : {1}'.format(attr, getattr(self, attr)))

        return ''


class GeneralStep(Step):

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

    def __init__(self, name, increments=100, iterations=100, factor=1.0, nlgeom=True, nlmat=False, displacements=[],
                 loads=[], type='static', tolerance=0.01, state='sls'):
        Step.__init__(self, name=name)

        self.__name__      = 'GeneralStep'
        self.name          = name
        self.increments    = increments
        self.iterations    = iterations
        self.factor        = factor
        self.nlgeom        = nlgeom
        self.nlmat         = nlmat
        self.displacements = displacements
        self.loads         = loads
        self.type          = type
        self.tolerance     = tolerance
        self.state         = state
        self.attr_list.extend(['increments', 'iterations', 'factor', 'nlgeom', 'nlmat', 'displacements', 'loads',
                               'type', 'tolerance', 'state'])


class HeatStep(Step):

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
        Step.__init__(self, name=name)

        self.__name__    = 'HeatStep'
        self.name        = name
        self.interaction = interaction
        self.increments  = increments
        self.temp0       = temp0
        self.dTmax       = dTmax
        self.type        = type
        self.duration    = duration
        self.attr_list.extend(['interaction', 'increments', 'temp0', 'dTmax', 'type', 'duration'])


class ModalStep(Step):

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
        Step.__init__(self, name=name)

        self.__name__      = 'ModalStep'
        self.name          = name
        self.modes         = modes
        self.increments    = increments
        self.displacements = displacements
        self.type          = type
        self.attr_list.extend(['modes', 'increments', 'displacements', 'type'])


class HarmonicStep(Step):

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

    def __init__(self, name, freq_list, displacements=[], loads=[], factor=1.0, damping=None, type='harmonic'):
        Step.__init__(self, name=name)

        self.__name__      = 'HarmonicStep'
        self.name          = name
        self.freq_list     = freq_list
        self.displacements = displacements
        self.loads         = loads
        self.factor        = factor
        self.damping       = damping
        self.type          = type
        self.attr_list.extend(['freq_list', 'displacements', 'loads', 'factor', 'damping', 'type'])


class BucklingStep(Step):

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

    def __init__(self, name, modes=5, increments=100, factor=1., displacements=[], loads=[], type='buckle', step=None):
        Step.__init__(self, name=name)

        self.__name__      = 'BucklingStep'
        self.name          = name
        self.modes         = modes
        self.increments    = increments
        self.factor        = factor
        self.displacements = displacements
        self.loads         = loads
        self.type          = type
        self.step          = step
        self.attr_list.extend(['modes', 'increments', 'factor', 'displacements', 'loads', 'type', 'step'])


class AcousticStep(Step):

    """ Initialises AcousticStep object for use in a acoustic analysis.

    Parameters
    ----------
    name : str
        Name of the AcousticStep.
    freq_range : list
        Range of frequencies to analyse.
    freq_step : int
        Step size for frequency range.
    displacements : list
        Displacement object names.
    loads : list
        Load object names.
    sources : list
        List of source elements or element sets radiating sound.
    samples : int
        Number of samples for acoustic analysis.
    factor : float
        Proportionality factor on the loads and displacements.
    damping : float
        Constant harmonic damping ratio.
    type : str
        'acoustic'.

    Returns
    -------
    None

    """

    def __init__(self, name, freq_range, freq_step, displacements=[], loads=[], sources=[], samples=5, factor=1.0,
                 damping=None, type='acoustic'):
        Step.__init__(self, name=name)

        self.__name__      = 'AcousticStep'
        self.name          = name
        self.freq_range    = freq_range
        self.freq_step     = freq_step
        self.displacements = displacements
        self.sources       = sources
        self.samples       = samples
        self.loads         = loads
        self.factor        = factor
        self.damping       = damping
        self.type          = type
        self.attr_list.extend(['freq_range', 'freq_step', 'displacements', 'sources', 'samples', 'loads', 'factor',
                               'damping', 'type'])
