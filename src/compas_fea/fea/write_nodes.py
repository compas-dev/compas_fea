
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
    'abaqus':   ', ',
    'opensees': ' ',
    'sofistik': ' ',
    'ansys':    ' ',
}


def write_input_nodes(f, software, nodes, sets={}):

    """ Writes the nodal co-ordinates information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use: 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    nodes : dict
        Node dictionary from structure.nodes.
    sets : dict
        Set dictionary from structure.sets.

    Returns
    -------
    None

    """

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Nodes\n'.format(c))
    f.write('{0}\n'.format(c))

    # Header

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

    # Nodes

    f.write('{0} No. x[m] y[m] z[m]\n'.format(c))
    f.write('{0}\n'.format(c))

    for key in sorted(nodes, key=int):
        data = spacer[software].join([str(key + 1)] + [str(nodes[key][i]) for i in 'xyz'])
        f.write('{0}{1}\n'.format(prefix[software], data))

    # Sets

    if software == 'abaqus':

        for key, item in sets.items():

            if item['type'] == 'node':

                f.write('**\n')
                f.write('** {0}\n'.format(key))
                f.write('** ' + '-' * len(key) + '\n')
                f.write('**\n')
                f.write('*NSET, NSET={0}\n'.format(key))
                f.write('**\n')

                selection = [i + 1 for i in item['selection']]
                cnt = 0
                for i in selection:
                    f.write(str(i))
                    if (cnt < 9) and (i != selection[-1]):
                        f.write(',')
                        cnt += 1
                    elif cnt >= 9:
                        f.write('\n')
                        cnt = 0
                    else:
                        f.write('\n')

    elif software == 'opensees':

        pass

    elif software == 'ansys':

        pass

    elif software == 'sofistik':

        pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
