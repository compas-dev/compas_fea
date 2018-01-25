
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


def write_input_postprocess(f, software, structure, steps):

    """ Writes any post-processing information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        The Structure object to read from.
    steps : dic
        Step objects from structure.steps.

    Returns
    -------
    None

    """

    c = comments[software]
    key = structure.steps_order[-1]  # assumption you want the last step
    step = steps[key]
    step_index = step.index

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ------------------------------------------------------------- Post-processing\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'abaqus':

        pass

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        f.write('$\n')
        f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
        f.write('CTRL SLS\n')
        # f.write('CTRL ULTI\n')
        # CTRL PFAI 2
        f.write('CRAC WK PARA\n')
        f.write('$\n')
        f.write('LC 10{0}\n'.format(step_index))

    elif software == 'ansys':

        pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
