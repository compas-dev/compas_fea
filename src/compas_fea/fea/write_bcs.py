
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_bcs',
]

dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']
fixitys = ['PX', 'PY', 'PZ', 'MX', 'MY' 'MZ']

comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}


def write_input_bcs(f, software, structure, steps, displacements, ndof=6):

    """ Writes boundary condition information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        Struture object.
    steps : dic
        Step objects from structure.steps.
    displacements : dic
        Displacement objects from structure.displacements.
    ndof : int
        Number of degrees-of-freedom per node.

    Returns
    -------
    None

    """

    headers = {
        'abaqus':   '**',
        'opensees': 'node {0}'.format(' '.join(dofs[:ndof])),
        'sofistik': 'node fixity',
        'ansys':    '!',
    }

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ------------------------------------------------------------------------- BCs\n'.format(c))

    key = structure.steps_order[0]
    step = steps[key]

    f.write('{0}\n'.format(c))
    f.write('{0} {1}\n'.format(c, key))
    f.write('{0} '.format(c) + '-' * len(key) + '\n')

    for k in step.displacements:

        displacement = displacements[k]
        com = displacement.components
        nset = displacement.nodes

        f.write('{0}\n'.format(c))
        f.write('{0} {1}\n'.format(c, k))
        f.write('{0} '.format(c) + '-' * len(k) + '\n')
        f.write('{0}\n'.format(c))
        f.write('{0} {1}\n'.format(c, headers[software]))
        f.write('{0}\n'.format(c))

        if software == 'opensees':

            j = []
            for dof in dofs[:ndof]:
                if com[dof] is not None:
                    j.append('1')
                else:
                    j.append('0')

            for node in sorted(structure.sets[nset]['selection'], key=int):
                f.write('fix {0} {1}\n'.format(node + 1, ' '.join(j)))

        elif software == 'sofistik':

            f.write('NODE NO FIX\n')
            f.write('{0}\n'.format(c))
            j = ''
            for dof, fixity in zip(dofs, fixitys):
                if com[dof] == 0:
                    j += fixity

            for node in sorted(structure.sets[nset]['selection'], key=int):
                f.write('{0} {1}\n'.format(node + 1, j))

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
