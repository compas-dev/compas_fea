
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
        Analysis software or library to use: 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    ndof : float
        Numbers of degrees-of-freedom per node (for OpenSees).

    Returns
    -------
    None

    """

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} --------------------------------------------------------------------- Heading\n'.format(c))
    f.write('{0}\n'.format(c))
    f.write('{0} {1} input file\n'.format(c, names[software]))
    f.write('{0} compas_fea contact: {1}\n'.format(c, authors[software]))
    f.write('{0}\n'.format(c))
    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))

    misc = {
        'abaqus':   '**\n*PHYSICAL CONSTANTS, ABSOLUTE ZERO=-273.15, STEFAN BOLTZMANN=5.67e-8\n',
        'opensees': '#\nwipe\nmodel basic -ndm 3 -ndf {0}\n'.format(ndof),
        'sofistik': '',
        'ansys':    '',
    }

    if misc[software]:
        f.write(misc[software])

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
