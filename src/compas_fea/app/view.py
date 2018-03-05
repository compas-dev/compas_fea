
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide.QtCore import Qt
from PySide.QtCore import QPoint
from PySide.QtGui import QApplication
from PySide.QtGui import QColor
from PySide.QtOpenGL import QGLWidget

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from compas.viewers import xdraw_points
from compas.viewers import xdraw_lines
from compas.viewers import xdraw_texts
from compas.viewers import xdraw_polygons

# from compas.geometry import add_vectors


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tom Van Mele <vanmelet@ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# ==============================================================================
# Camera
# ==============================================================================

class Camera(object):

    def __init__(self, view):
        self.view = view
        self.fov = 60.
        self.near = 0.
        self.far = 100.
        self.rx  = -60.
        self.rz = +45.
        self.tx = +0.
        self.ty = +0.
        self.tz = -10.
        self.dr = +0.5
        self.dt = +0.05

    @property
    def aspect(self):
        w = self.view.width()
        h = self.view.height()
        return float(w) / float(h)

    def zoom_in(self, steps=1):
        self.tz -= steps * self.tz * self.dt

    def zoom_out(self, steps=1):
        self.tz += steps * self.tz * self.dt

    def rotate(self):
        dx = self.view.mouse.dx()
        dy = self.view.mouse.dy()
        self.rx += self.dr * dy
        self.rz += self.dr * dx

    def translate(self):
        dx = self.view.mouse.dx()
        dy = self.view.mouse.dy()
        self.tx += self.dt * dx
        self.ty -= self.dt * dy

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


# ==============================================================================
# Mouse
# ==============================================================================

class Mouse(object):

    def __init__(self, view):
        self.view  = view
        self.pos = QPoint()
        self.last_pos = QPoint()

    def dx(self):
        return self.pos.x() - self.last_pos.x()

    def dy(self):
        return self.pos.y() - self.last_pos.y()


# ==============================================================================
# View
# ==============================================================================

class View(QGLWidget):

    def __init__(self, structure):
        QGLWidget.__init__(self)

        self.camera = Camera(self)
        self.mouse = Mouse(self)

        bx, by, bz = structure.node_bounds()
        self.scale = max([(bx[1] - bx[0]), (by[1] - by[0]), (bz[1] - bz[0])])
        self.structure = structure
        self.nodes_on = True
        self.node_numbers_on = True
        self.lines_on = True
        self.line_numbers_on = True
        self.faces_on = True
        self.face_numbers_on = True

        self.update_nodes()
        self.update_elements()

    def initializeGL(self):
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
        glEnable(GL_MULTISAMPLE)
        glShadeModel(GL_SMOOTH)
        # glPolygonOffset(1.0, 1.0)
        # glEnable(GL_POLYGON_OFFSET_FILL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glutInit()

        self.qglClearColor(QColor.fromRgb(220, 220, 220))
        self.camera.aim()
        self.camera.focus()

    def resizeGl(self, w, h):
        glViewport(0, 0, w, h)
        self.camera.aim()
        self.camera.focus()

    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glPushAttrib(GL_POLYGON_BIT)
        self.camera.aim()
        self.camera.focus()
        self.paint()
        # glPopAttrib()
        # glutSwapBuffers()

    def paint(self):
        self.draw_axes()

        if self.nodes_on:
            xdraw_points(self.nodes)
        if self.node_numbers_on:
            xdraw_texts(self.node_numbers)
        if self.lines_on:
            xdraw_lines(self.lines)
        if self.line_numbers_on:
            xdraw_texts(self.line_numbers)
        if self.faces_on:
            xdraw_polygons(self.faces)
        if self.face_numbers_on:
            xdraw_texts(self.face_numbers)

    def draw_axes(self):
        glLineWidth(3)
        glBegin(GL_LINES)
        glColor3f(*(1, 0, 0))
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glColor3f(*(0, 1, 0))
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        glColor3f(*(0, 0, 1))
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)
        glEnd()


# ==============================================================================
# Events
# ==============================================================================

    def keyPressAction(self, key):
        if key == 45:
            self.camera.zoom_out()
        elif key == 61:
            self.camera.zoom_in()
        return

    def mouseMoveEvent(self, event):
        self.mouse.pos = event.pos()
        if event.buttons() & Qt.LeftButton:
            self.camera.rotate()
            self.mouse.last_pos = event.pos()
            self.updateGL()
        elif event.buttons() & Qt.RightButton:
            self.camera.translate()
            self.mouse.last_pos = event.pos()
            self.updateGL()

    def mousePressEvent(self, event):
        self.mouse.last_pos = event.pos()


# ==============================================================================
# Update
# ==============================================================================

    def update_nodes(self):
        ds = 0.01 * self.scale
        self.nodes = []
        self.node_numbers = []
        for key, node in self.structure.nodes.items():
            xyz = self.structure.node_xyz(key)
            self.nodes.append({
                'pos':   xyz,
                'color': [1.0, 0.4, 0.4],
                'size':  10
            })
            self.node_numbers.append({
                'pos':   xyz,
                'color': [1.0, 0.4, 0.4, 1.0],
                'text':  str(key),
                'shift': [0, 0, ds]
            })

    def update_elements(self):
        ds = 0.01 * self.scale
        self.lines = []
        self.line_numbers = []
        self.faces = []
        self.face_numbers = []
        line_colour = [0.5, 0.5, 1.0]
        face_colour = [0.5, 1.0, 0.5, 0.5]

        for key, element in self.structure.elements.items():
            nodes = element.nodes
            n = len(nodes)
            if n == 2:
                sp = self.structure.node_xyz(nodes[0])
                ep = self.structure.node_xyz(nodes[1])
                self.lines.append({
                    'start': sp,
                    'end':   ep,
                    'color': line_colour,
                    'width': 5,
                })
                self.line_numbers.append({
                    'pos':   self.structure.element_centroid(key),
                    'color': [0.5, 0.5, 1.0, 1.0],
                    'text':  str(key),
                    'shift': [0, 0, ds],
                })
            elif (n == 3) or (n == 4):
                points = [self.structure.node_xyz(node) for node in nodes]
                self.faces.append({
                    'points':      points,
                    'color.front': face_colour,
                    'color.back':  face_colour,
                })
                self.face_numbers.append({
                    'pos':   self.structure.element_centroid(key),
                    'color': [0.0, 0.7, 0.0, 1.0],
                    'text':  str(key),
                    'shift': [0, 0, ds],
                })



#         if self.displacements_on:
#             xdraw_lines(self.bcs_translations)
#             xdraw_lines(self.bcs_rotations)



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


