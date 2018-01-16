
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_heading',
]

comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}

names = {
    'abaqus':   'Abaqus',
    'opensees': 'OpenSees',
    'sofistik': 'Sofistik',
    'ansys':    'Ansys',
}

units = {
    'abaqus':   '[N, m, kg, s]',
    'opensees': '[N, m, kg, s]',
    'sofistik': '[kN, m, kg, s]',
    'ansys':    '',
}

authors = {
    'abaqus':   'Dr Andrew Liew - liew@arch.ethz.ch',
    'opensees': 'Dr Andrew Liew - liew@arch.ethz.ch',
    'sofistik': 'Dr Andrew Liew - liew@arch.ethz.ch',
    'ansys':    'Dr Tomas Mendez - mendez@arch.ethz.ch',
}


def write_input_heading(f, software, ndof=6):

    """ Creates the input file heading.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    ndof : float
        Numbers of degrees-of-freedom per node.

    Returns
    -------
    None

    """

    c = comments[software]
    name = names[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} --------------------------------------------------------------------- Heading\n'.format(c))
    f.write('{0}\n'.format(c))
    f.write('{0} {1} input file\n'.format(c, name))
    f.write('{0} Units: {1}\n'.format(c, units[software]))
    f.write('{0} compas_fea package: {1}\n'.format(c, authors[software]))
    f.write('{0}\n'.format(c))
    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))

    if software == 'abaqus':

        f.write('**\n')
        f.write('*PHYSICAL CONSTANTS, ABSOLUTE ZERO=-273.15, STEFAN BOLTZMANN=5.67e-8\n')
        f.write('**\n')

    elif software == 'opensees':

        f.write('#\n')
        f.write('wipe\n')
        f.write('model basic -ndm 3 -ndf {0}\n'.format(ndof))
        f.write('#\n')

    f.write('{0}\n'.format(c))
