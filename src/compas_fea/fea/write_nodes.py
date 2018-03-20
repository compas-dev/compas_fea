
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_nodes',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}

prefix = {
    'abaqus':   '',
    'opensees': 'node ',
    'sofistik': '',
    'ansys':    '',
}

spacer = {
    'abaqus':   ',\t ',
    'opensees': '\t ',
    'sofistik': '\t ',
    'ansys':    '\t ',
}


def write_input_nodes(f, software, nodes):

    """ Writes the nodal co-ordinates information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use: 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    nodes : dic
        Node dictionary from structure.nodes.

    Returns
    -------
    None

    """

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Nodes\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'sofistik':

        f.write('+PROG SOFIMSHA\n')
        f.write('$\n')
        f.write('UNIT 0\n')
        f.write('SYST 3D GDIR POSX,POSY,NEGZ\n')
        f.write('CTRL OPT OPTI 10\n')
        f.write('NODE NO X Y Z\n')
        f.write('$\n')

    elif software == 'abaqus':

        f.write('*NODE, NSET=nset_all\n')
        f.write('**\n')

    elif software == 'opensees':

        pass

    elif software == 'ansys':

        pass

    f.write('{0} No.\t x[m]\t y[m]\t z[m]\n'.format(c))
    f.write('{0}\n'.format(c))

    for key in sorted(nodes, key=int):
        xyz = [str(nodes[key][i]) for i in 'xyz']
        data = spacer[software].join([str(key + 1)] + xyz)
        f.write('{0}{1}\n'.format(prefix[software], data))

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
