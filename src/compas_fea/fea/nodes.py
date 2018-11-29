
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Nodes',
]


class Nodes(object):

    def __init__(self):

        pass


    def write_nodes(self):

        header = {
            'abaqus':   '**\n*NODE, NSET=nset_all\n**',
            'opensees': '#',
            'ansys':    '!',
        }

        self.prefix = {
            'abaqus':   '',
            'opensees': 'node ',
            'ansys':    '',
        }

        self.write_section('Nodes')
        self.write_line(header[self.software])

        for key in sorted(self.structure.nodes, key=int):
            self.write_node(key)

        self.blank_line()
        self.blank_line()


    def write_node(self, key):

        prefix  = self.prefix[self.software]
        spacer  = self.spacer[self.software]
        x, y, z = self.structure.node_xyz(key)

        line    = '{0}{1}{2}{3:.3f}{2}{4:.3f}{2}{5:.3f}'.format(prefix, key + 1, spacer, x, y, z)
        self.write_line(line)
