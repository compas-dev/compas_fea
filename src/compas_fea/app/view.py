
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide.QtCore import Qt
from PySide.QtGui import QApplication
from PySide.QtGui import QColor
from PySide.QtOpenGL import QGLWidget

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# from compas.visualization.viewers.drawing import xdraw_points
# from compas.visualization.viewers.drawing import xdraw_lines
# from compas.visualization.viewers.drawing import xdraw_polygons
# from compas.visualization.viewers.drawing import xdraw_texts

# from compas.geometry import add_vectors


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


class Camera(object):

    def __init__(self, view):
        self.view = view
        self.fov = 60.
        self.near = 1.
        self.far = 100.
        self.rx = -60.
        self.rz = +45.
        self.tx = +0.
        self.ty = +0.
        self.tz = -10.
    #     self.dr = +0.5
    #     self.dt = +0.05

    @property
    def aspect(self):
        w = self.view.width()
        h = self.view.height()
        return float(w) / float(h)

    # def zoom_in(self, steps=1):
    #     self.tz -= steps * self.tz * self.dt

    # def zoom_out(self, steps=1):
    #     self.tz += steps * self.tz * self.dt

    # def rotate(self):
    #     dx = self.view.mouse.dx()
    #     dy = self.view.mouse.dy()
    #     self.rx += self.dr * dy
    #     self.rz += self.dr * dx

    # def translate(self):
    #     dx = self.view.mouse.dx()
    #     dy = self.view.mouse.dy()
    #     self.tx += self.dt * dx
    #     self.ty -= self.dt * dy

    def aim(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.tx, self.ty, self.tz)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.rz, 0, 0, 1)

    def focus(self):
        glPushAttrib(GL_TRANSFORM_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.aspect, self.near, self.far)
        glPopAttrib()


class View(QGLWidget):

    def __init__(self, structure):
        QGLWidget.__init__(self)
        self.camera = Camera(self)
        # self.mouse = Mouse(self)

    def initializeGL(self):

        self.qglClearColor(QColor.fromRgb(220, 220, 220))
        self.camera.aim()
        self.camera.focus()

        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        # glCullFace(GL_BACK)
        # glShadeModel(GL_SMOOTH)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glPolygonOffset(1.0, 1.0)
        # glEnable(GL_POLYGON_OFFSET_FILL)
        # glEnable(GL_CULL_FACE)
        # glEnable(GL_POINT_SMOOTH)
        # glEnable(GL_LINE_SMOOTH)
        # glEnable(GL_POLYGON_SMOOTH)
        # glEnable(GL_DEPTH_TEST)
        # glEnable(GL_BLEND)
        # glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)


    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glPushAttrib(GL_POLYGON_BIT)
        # self.camera.aim()
        # self.camera.focus()
        self.paint()
        # glPopAttrib()
        # glutSwapBuffers()

    def paint(self):

        self.draw_axes()

#         if self.nodes_on:
#             xdraw_points(self.nodes)
#         if self.node_numbers_on:
#             xdraw_texts(self.node_numbers)
#         if self.elements_on:
#             xdraw_lines(self.lines)
#             xdraw_polygons(self.faces)
#         if self.element_numbers_on:
#             xdraw_texts(self.element_numbers)
#         if self.displacements_on:
#             xdraw_lines(self.bcs_translations)
#             xdraw_lines(self.bcs_rotations)


    def draw_axes(self):

        glLineWidth(3)
        glBegin(GL_LINES)

        glColor3f(*(1, 0, 0))
        glVertex3f(0, 0, 0)
        glVertex3f(0.1, 0, 0)

        glColor3f(*(0, 1, 0))
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.1, 0)

        glColor3f(*(0, 0, 1))
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 0.1)

        glEnd()

#         if structure:

#             # Nodes

#             bx, by, bz = structure.node_bounds()
#             s = max([(bx[1] - bx[0]), (by[1] - by[0]), (bz[1] - bz[0])])
#             ds = s / 50.

#             self.nodes = []
#             self.node_numbers = []
#             for nkey, node in structure.nodes.items():
#                 self.nodes.append({'pos': [node[i] for i in 'xyz'],
#                                    'color': [0.5, 0.5, 1.0],
#                                    'size': 10})
#                 self.node_numbers.append({'pos': [node[i] for i in 'xyz'],
#                                           'color': [0.5, 0.5, 1.0, 1.0],
#                                           'text': nkey,
#                                           'shift': [0, 0, ds]})

#             # Elements

#             self.lines = []
#             self.faces = []
#             self.element_numbers = []
#             for ekey, element in structure.elements.items():
#                 nodes = element.nodes
#                 n = len(nodes)
#                 line_colour = [0.4, 0.4, 0.4]
#                 face_colour = [0.8, 0.8, 0.8, 0.5]
#                 if n == 2:
#                     sp = [structure.nodes[nodes[0]][i] for i in 'xyz']
#                     ep = [structure.nodes[nodes[1]][i] for i in 'xyz']
#                     self.lines.append({'start': sp,
#                                        'end': ep,
#                                        'color': line_colour,
#                                        'width': 5})
#                 elif (n == 3) or (n == 4):
#                     points = [[structure.nodes[str(node)][i] for i in 'xyz'] for node in nodes]
#                     self.faces.append({'points': points,
#                                        'color.front': face_colour,
#                                        'color.back' : face_colour})
#                 self.element_numbers.append({'pos': structure.element_centroid(ekey),
#                                              'color': [0.4, 0.4, 0.4, 1.0],
#                                              'text': ekey,
#                                              'shift': [0, 0, ds]})

#             # Displacements

#             bc_colour = [0.2, 0.8, 0.2]
#             db = -2 * ds
#             self.bcs_translations = []
#             self.bcs_rotations = []
#             for key, displacement in structure.displacements.items():
#                 for i, val in displacement.components.items():
#                     if val != '-':
#                         nodes = displacement.nodes
#                         if isinstance(nodes, str):
#                             selection = structure.sets[nodes]['selection']
#                         elif isinstance(nodes, list):
#                             selection = nodes
#                         for node in selection:
#                             sp = [structure.nodes[node][j] for j in 'xyz']
#                             if i == 'x':
#                                 ep = add_vectors(sp, [db, 0, 0])
#                             elif i == 'y':
#                                 ep = add_vectors(sp, [0, db, 0])
#                             elif i == 'z':
#                                 ep = add_vectors(sp, [0, 0, db])
#                             if i in ['x', 'y', 'z']:
#                                 self.bcs_translations.append({'start': sp, 'end': ep, 'color': bc_colour, 'width': 3})
#                             if i == 'xx':
#                                 a = add_vectors(sp, [db / 2, 0, -ds / 2.])
#                                 b = add_vectors(sp, [db / 2, 0, +ds / 2.])
#                             elif i == 'yy':
#                                 a = add_vectors(sp, [0, db / 2, -ds / 2.])
#                                 b = add_vectors(sp, [0, db / 2, +ds / 2.])
#                             elif i == 'zz':
#                                 a = add_vectors(sp, [-ds / 2., 0, db / 2])
#                                 b = add_vectors(sp, [+ds / 2., 0, db / 2])
#                             if i in ['xx', 'yy', 'zz']:
#                                 self.bcs_rotations.append({'start': a, 'end': b, 'color': bc_colour, 'width': 3})

#     # ==============================================================================
#     # keyboard
#     # ==============================================================================

#     def keyPressAction(self, key):
#         """ Defines the paint function.

#         Parameters:
#             key (int): Pressed key.

#         Returns:
#             None
#         """
#         if key == 45:
#             self.camera.zoom_out()
#         elif key == 61:
#             self.camera.zoom_in()
#         return
