
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Sets',
]


class Sets(object):

    def __init__(self):

        pass

    def write_node_sets(self):

        self.write_section('Node sets')
        self.blank_line()

        for key in sorted(self.structure.sets):
            node_set = self.structure.sets[key]
            if node_set['type'] == 'node':
                self.write_node_set(key, node_set)
                self.blank_line()
                self.blank_line()

    def write_node_set(self, key, node_set):

        self.write_subsection(key)

        header = {
            'abaqus':   '*NSET, NSET={0}'.format(key),
            'opensees': '',
            'sofistik': '',
            'ansys':    '',
        }

        self.write_line(header[self.software])
        self.blank_line()

        nodes = [i + 1 for i in node_set['selection']]

        for i in range(0, len(nodes), 8):
            self.write_line(self.spacer[self.software].join([str(j) for j in nodes[i:i + 8]]))
