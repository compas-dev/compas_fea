from PySide.QtCore import Qt
from PySide.QtGui import QColor

from compas.visualization.viewers.widgets.glview import GLView
from compas.visualization.viewers.drawing import xdraw_points
from compas.visualization.viewers.drawing import xdraw_lines
from compas.visualization.viewers.drawing import xdraw_polygons
from compas.visualization.viewers.drawing import xdraw_texts

from compas.geometry import add_vectors


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


class View(GLView):

    def __init__(self, structure):

    # ==============================================================================
    # initialise
    # ==============================================================================

        super(View, self).__init__()

        self.nodes_on = Qt.Checked
        self.node_numbers_on = Qt.Unchecked
        self.elements_on = Qt.Checked
        self.element_numbers_on = Qt.Unchecked
        self.displacements_on = Qt.Checked

        self.clear_color = QColor.fromRgb(0, 0, 0)
        self.near = 0.1

    # ==============================================================================
    # geometry
    # ==============================================================================

        if structure:

            # Nodes

            bx, by, bz = structure.node_bounds()
            s = max([(bx[1] - bx[0]), (by[1] - by[0]), (bz[1] - bz[0])])
            ds = s / 50.

            self.nodes = []
            self.node_numbers = []
            for nkey, node in structure.nodes.items():
                self.nodes.append({'pos': [node[i] for i in 'xyz'],
                                   'color': [0.5, 0.5, 1.0],
                                   'size': 10})
                self.node_numbers.append({'pos': [node[i] for i in 'xyz'],
                                          'color': [0.5, 0.5, 1.0, 1.0],
                                          'text': nkey,
                                          'shift': [0, 0, ds]})

            # Elements

            self.lines = []
            self.faces = []
            self.element_numbers = []
            for ekey, element in structure.elements.items():
                nodes = element.nodes
                n = len(nodes)
                line_colour = [0.4, 0.4, 0.4]
                face_colour = [0.8, 0.8, 0.8, 0.5]
                if n == 2:
                    sp = [structure.nodes[nodes[0]][i] for i in 'xyz']
                    ep = [structure.nodes[nodes[1]][i] for i in 'xyz']
                    self.lines.append({'start': sp,
                                       'end': ep,
                                       'color': line_colour,
                                       'width': 5})
                elif (n == 3) or (n == 4):
                    points = [[structure.nodes[str(node)][i] for i in 'xyz'] for node in nodes]
                    self.faces.append({'points': points,
                                       'color.front': face_colour,
                                       'color.back' : face_colour})
                self.element_numbers.append({'pos': structure.element_centroid(ekey),
                                             'color': [0.4, 0.4, 0.4, 1.0],
                                             'text': ekey,
                                             'shift': [0, 0, ds]})

            # Displacements

            bc_colour = [0.2, 0.8, 0.2]
            db = -2 * ds
            self.bcs_translations = []
            self.bcs_rotations = []
            for key, displacement in structure.displacements.items():
                for i, val in displacement.components.items():
                    if val != '-':
                        nodes = displacement.nodes
                        if isinstance(nodes, str):
                            selection = structure.sets[nodes]['selection']
                        elif isinstance(nodes, list):
                            selection = nodes
                        for node in selection:
                            sp = [structure.nodes[node][j] for j in 'xyz']
                            if i == 'x':
                                ep = add_vectors(sp, [db, 0, 0])
                            elif i == 'y':
                                ep = add_vectors(sp, [0, db, 0])
                            elif i == 'z':
                                ep = add_vectors(sp, [0, 0, db])
                            if i in ['x', 'y', 'z']:
                                self.bcs_translations.append({'start': sp, 'end': ep, 'color': bc_colour, 'width': 3})
                            if i == 'xx':
                                a = add_vectors(sp, [db / 2, 0, -ds / 2.])
                                b = add_vectors(sp, [db / 2, 0, +ds / 2.])
                            elif i == 'yy':
                                a = add_vectors(sp, [0, db / 2, -ds / 2.])
                                b = add_vectors(sp, [0, db / 2, +ds / 2.])
                            elif i == 'zz':
                                a = add_vectors(sp, [-ds / 2., 0, db / 2])
                                b = add_vectors(sp, [+ds / 2., 0, db / 2])
                            if i in ['xx', 'yy', 'zz']:
                                self.bcs_rotations.append({'start': a, 'end': b, 'color': bc_colour, 'width': 3})

    # ==============================================================================
    # keyboard
    # ==============================================================================

    def keyPressAction(self, key):
        """ Defines the paint function.

        Parameters:
            key (int): Pressed key.

        Returns:
            None
        """
        if key == 45:
            self.camera.zoom_out()
        elif key == 61:
            self.camera.zoom_in()
        return

    # ==============================================================================
    # paint
    # ==============================================================================

    def paint(self):
        """ Defines the paint function.

        Parameters:
            None

        Returns:
            None
        """
        if self.nodes_on:
            xdraw_points(self.nodes)
        if self.node_numbers_on:
            xdraw_texts(self.node_numbers)
        if self.elements_on:
            xdraw_lines(self.lines)
            xdraw_polygons(self.faces)
        if self.element_numbers_on:
            xdraw_texts(self.element_numbers)
        if self.displacements_on:
            xdraw_lines(self.bcs_translations)
            xdraw_lines(self.bcs_rotations)
