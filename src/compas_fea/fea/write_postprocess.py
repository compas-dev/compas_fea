
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_postprocess',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}


def write_input_postprocess(f, software, structure):

    """ Writes any post-processing information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        The Structure object to read from.

    Returns
    -------
    None

    """

    c = comments[software]
    step = structure.steps[structure.steps_order[-1]].index  # assumption you want the last step

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ------------------------------------------------------------- Post-processing\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'abaqus':

        pass

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        f.write('$\n')
        f.write('CTRL SLS\n')
        f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
        f.write('$\n')
        # CTRL PFAI 2
        f.write('CRAC WK PARA\n')
        f.write('LC 10{0}\n'.format(step))

    elif software == 'ansys':

        pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
