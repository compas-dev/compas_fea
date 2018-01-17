
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

leader = {
    'abaqus':   '',
    'opensees': 'node ',
    'sofistik': '',
    'ansys':    '',
}


def write_input_nodes(f, software, nodes):

    """ Writes the nodal co-ordinates information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
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
    f.write('{0} No. x[m] y[m] z[m]\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'sofistik':
        f.write('UNIT 0\n')
        f.write('SYST 3D GDIR POSX,POSY,NEGZ\n')
        f.write('CTRL OPT OPTI 10\n')
        f.write('NODE NO X Y Z\n')
        f.write('{0}\n'.format(c))
        seperator = ' '

    elif software == 'abaqus':
        f.write('*NODE, NSET=nset_all\n')
        f.write('{0}\n'.format(c))
        seperator = ', '

    for key in sorted(nodes, key=int):
        xyz = [str(nodes[key][i]) for i in 'xyz']
        data = seperator.join([str(key + 1)] + xyz)
        f.write('{0}{1}\n'.format(leader[software], data))

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
