from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


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

            if node_set.type == 'node':
                self.write_node_set(key, node_set)
                self.blank_line()
                self.blank_line()

    def write_node_set(self, key, node_set):

        self.write_subsection(key)

        header = {
            'abaqus':   '*NSET, NSET={0}'.format(key),
            'opensees': '',
            'ansys':    '',
        }

        self.write_line(header[self.software])
        self.blank_line()

        nodes = [i + 1 for i in node_set.selection]

        for i in range(0, len(nodes), 8):
            self.write_line(self.spacer[self.software].join([str(j) for j in nodes[i:i + 8]]))

    def write_element_sets(self):

        self.write_section('Element sets')
        self.blank_line()

        for key in sorted(self.structure.sets):

            element_set = self.structure.sets[key]

            if element_set.type != 'node':
                self.write_element_set(key, element_set)
                self.blank_line()
                self.blank_line()

    def write_element_set(self, key, element_set):

        stype = element_set.type

        self.write_subsection(key)

        if stype in ['element', 'surface_node']:

            if stype == 'element':
                self.write_line('*ELSET, ELSET={0}'.format(key))

            elif stype == 'surface_node':
                self.write_line('*SURFACE, TYPE=NODE, NAME={0}'.format(key))

            self.blank_line()

            selection = [i + 1 for i in element_set.selection]

            for i in range(0, len(selection), 8):
                self.write_line(self.spacer[self.software].join([str(j) for j in selection[i:i + 8]]))

        if stype == 'surface_element':

            self.write_line('*SURFACE, TYPE=ELEMENT, NAME={0}'.format(key))
            self.write_line('** ELEMENT, SIDE')

            for element, sides in element_set.selection.items():
                for side in sides:
                    self.write_line('{0}, {1}'.format(element + 1, side))
                    self.blank_line()
