
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    import PySide2
except ImportError:
    from PySide import QtCore
    from PySide import QtGui
    import PySide.QtGui as QtWidgets
else:
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from compas.utilities import flatten

from compas.viewers.core import Camera
from compas.viewers.core import Mouse
from compas.viewers.core import Grid
from compas.viewers.core import Axes
from compas.viewers.core import GLWidget
from compas.viewers.core import App
from compas.viewers.core import Controller

import compas_fea


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = ['FeaApp']


COMPAS_FEA = compas_fea.__file__.split('__init__.py')[0]
ICONS = COMPAS_FEA + '/app/icons/'

config = {
    'menubar': [
        {'type': 'menu', 'text': 'File', 'items': [
            {'text': 'Open', 'action': 'file_open'},
            {'type': 'separator'},
            {'text': 'Exit', 'action': 'exit_app'},
            ]
        },
    ],
    'toolbar': [
        {'text': 'Zoom Extents', 'action': 'zoom_extents', 'image': ICONS + 'zoom/icons8-zoom-to-extents-50.png'},
        {'text': 'Zoom In', 'action': 'zoom_in', 'image': ICONS + 'zoom/icons8-zoom-in-50.png'},
        {'text': 'Zoom Out', 'action': 'zoom_out', 'image': ICONS + 'zoom/icons8-zoom-out-50.png'},
        {'text': 'Show Axes', 'action': 'toggle_show_axes', 'image': ICONS + 'xyz.png'},
        {'text': 'Show Grid', 'action': 'toggle_show_grid', 'image': ICONS + 'grid.png'},
    ],
    'sidebar': [

    ]
}

style = """
# QMainWindow {}

# QMenuBar {}

# QToolBar#Tools {
#     padding: 4px;
# }

# QDockWidget#Sidebar {}

# QDockWidget#Console {}

# QDockWidget#Console QPlainTextEdit {
#     background-color: #222222;
#     color: #eeeeee;
#     border-top: 8px solid #cccccc;
#     border-left: 1px solid #cccccc;
#     border-right: 1px solid #cccccc;
#     border-bottom: 1px solid #cccccc;
#     padding-left: 4px;
# }

"""


# ==============================================================================
# Controller
# ==============================================================================

class Front(Controller):

    settings = {
        'label_offset': 0.01,

        'vertices.on': True,
        'vertices.color': [1.0, 0.4, 0.4],
        'vertices_labels.color': [1.0, 0.4, 0.4, 1.0],
        'vertices.size:value': 100.0,
    }

    def __init__(self, app):
        super(Front, self).__init__(app)

        self.show_axes = True
        self.show_grid = True
        self.structure = app.structure

    def toggle_show_grid(self):
        self.show_grid = not self.show_grid
        self.view.update()

    def toggle_show_axes(self):
        self.show_axes = not self.show_axes
        self.view.update()


# ==============================================================================
# View
# ==============================================================================

def flist(items):
    return list(flatten(items))


class View(GLWidget):

    def __init__(self, controller):
        super(View, self).__init__()

        self.controller = controller
        self.axes = Axes()
        self.grid = Grid()
        self.grid.color = (0.8, 0.8, 0.8)
        self.n = 0
        self.v = 0
        self.e = 0
        self.f = 0

    @property
    def structure(self):
        return self.controller.structure

    @property
    def settings(self):
        return self.controller.settings

    def paint(self):
        if self.controller.show_axes:
            self.axes.draw()
        if self.controller.show_grid:
            self.grid.draw()
        self.draw_buffers()


    # @property
    # def faces(self):
    #     faces = []
    #     for fkey in self.mesh.faces():
    #         vertices = self.mesh.face_vertices(fkey)
    #         if len(vertices) == 3:
    #             faces.append(vertices)
    #             continue
    #         if len(vertices) == 4:
    #             a, b, c, d = vertices
    #             faces.append([a, b, c])
    #             faces.append([c, d, a])
    #             continue
    #         raise NotImplementedError
    #     return faces

    @property
    def array_xyz(self):
        return flist(self.structure.nodes_xyz())

    @property
    def array_vertices(self):
        return list(self.structure.nodes)

    # @property
    # def array_edges(self):
    #     return flist(self.mesh.edges())

    # @property
    # def array_faces_front(self):
    #     return flist(self.faces)

    # @property
    # def array_faces_back(self):
    #     return flist(face[::-1] for face in self.faces)

    @property
    def array_vertices_color(self):
        return flist(self.settings['vertices.color'] for i in self.structure.nodes)

    # @property
    # def array_edges_color(self):
    #     return flist(hex_to_rgb(self.settings['edges.color']) for key in self.mesh.vertices())

    # @property
    # def array_faces_color_front(self):
    #     return flist(hex_to_rgb(self.settings['faces.color:front']) for key in self.mesh.vertices())

    # @property
    # def array_faces_color_back(self):
    #     return flist(hex_to_rgb(self.settings['faces.color:back']) for key in self.mesh.vertices())

    def make_buffers(self):
        self.make_index_buffer(self.array_vertices)
        self.buffers = {
#            'xyz': self.make_vertex_buffer(self.array_xyz),
#            'vertices': self.make_index_buffer(self.array_vertices),
    #         'edges'            : self.make_index_buffer(self.array_edges),
    #         'faces:front'      : self.make_index_buffer(self.array_faces_front),
    #         'faces:back'       : self.make_index_buffer(self.array_faces_back),
#            'vertices.color': self.make_vertex_buffer(self.array_vertices_color, dynamic=True),
    #         'edges.color'      : self.make_vertex_buffer(self.array_edges_color, dynamic=True),
    #         'faces.color:front': self.make_vertex_buffer(self.array_faces_color_front, dynamic=True),
    #         'faces.color:back' : self.make_vertex_buffer(self.array_faces_color_back, dynamic=True),
        }
        self.n = len(self.array_xyz)
        self.v = len(self.array_vertices)
    #     self.e = len(self.array_edges)
    #     self.f = len(self.array_faces_front)

    def draw_buffers(self):
        if not self.buffers:
            return

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffers['xyz'])
        glVertexPointer(3, GL_FLOAT, 0, None)

    #     if self.settings['faces.on']:
    #         glBindBuffer(GL_ARRAY_BUFFER, self.buffers['faces.color:front'])
    #         glColorPointer(3, GL_FLOAT, 0, None)

    #         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['faces:front'])
    #         glDrawElements(GL_TRIANGLES, self.f, GL_UNSIGNED_INT, None)

    #         glBindBuffer(GL_ARRAY_BUFFER, self.buffers['faces.color:back'])
    #         glColorPointer(3, GL_FLOAT, 0, None)

    #         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['faces:back'])
    #         glDrawElements(GL_TRIANGLES, self.f, GL_UNSIGNED_INT, None)

    #     if self.settings['edges.on']:
    #         glLineWidth(self.settings['edges.width:value'])

    #         glBindBuffer(GL_ARRAY_BUFFER, self.buffers['edges.color'])
    #         glColorPointer(3, GL_FLOAT, 0, None)

    #         glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['edges'])
    #         glDrawElements(GL_LINES, self.e, GL_UNSIGNED_INT, None)

        if self.settings['vertices.on']:
            print('test')
            glPointSize(self.settings['vertices.size:value'])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers['vertices.color'])
            glColorPointer(3, GL_FLOAT, 0, None)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers['vertices'])
            glDrawElements(GL_POINTS, self.v, GL_UNSIGNED_INT, None)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)


# ==============================================================================
# Setup
# ==============================================================================

class FeaApp(App):

    def __init__(self, width=1440, height=900, structure=None):
        super(FeaApp, self).__init__(config=config, style=style)

        self.structure = structure
        self.controller = Front(self)
        self.view = View(self.controller)
        self.view.make_buffers()
        self.setup()
        self.setApplicationName('compas_fea App - Structure: {0}'.format(self.structure.name))
        self.init()
        print('***** FeaApp launched *****')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    # FeaApp().show()
    FeaApp()


























# # from functools import partial



# from compas_fea.structure import Structure

# # from compas.viewers.core import xdraw_polygons
# # from compas.viewers.core import xdraw_lines
# from compas.viewers.core import xdraw_points
# from compas.viewers.core import xdraw_texts
# # from compas.viewers.core import xdraw_cylinders
# # from compas.viewers.core import xdraw_spheres




# # get_obj_file = partial(
# #     QtWidgets.QFileDialog.getOpenFileName,
# #     caption='Select OBJ file',
# #     dir=compas.DATA,
# #     filter='OBJ files (*.obj)'
# # )


# # def center_mesh(mesh):
# #     xyz = [mesh.vertex_coordinates(key) for key in mesh.vertices()]
# #     cx, cy, cz = centroid_points(xyz)
# #     for key, attr in mesh.vertices(True):
# #         attr['x'] -= cx
# #         attr['y'] -= cy


# class Front(Controller):

#     def __init__(self, app):
#         self.app = app
#     #     self.mesh = None
#         self.settings = {}
#         self.settings['offset'] = 0.01 * self.app.offset
#         self.settings['vertices.on'] = True
#         self.settings['vertices_labels.on'] = False
#         self.settings['vertices.size'] = 10 * self.app.scale

#     #     self.settings['edges.width'] = 0.01
#     #     self.settings['edges.color'] = '#666666'
#     #     self.settings['faces.color:front'] = '#eeeeee'
#     #     self.settings['faces.color:back'] = '#eeeeee'
#     #     self.settings['edges.on'] = True
#     #     self.settings['faces.on'] = True
#     #     self.settings['edges_labels.on'] = False
#     #     self.settings['faces_labels.on'] = False
#     #     self.settings['vertices_normals.on'] = False
#     #     self.settings['faces_normals.on'] = False

#     @property
#     def view(self):
#         return self.app.view

#     def _make_lists(self):

#     #     if self.view.faces:
#     #         glDeleteLists(self.view.faces, 1)
#     #     if self.view.edges:
#     #         glDeleteLists(self.view.edges, 1)
#         if self.view.vertices:
#             glDeleteLists(self.view.vertices, 1)

#     #     key_xyz = {key: self.mesh.vertex_coordinates(key) for key in self.mesh.vertices()}
#     #     # faces list
#     #     faces = []
#     #     front = hex_to_rgb(self.settings['faces.color:front'], normalize=True)
#     #     front = list(front) + [1.0]
#     #     back  = hex_to_rgb(self.settings['faces.color:back'], normalize=True)
#     #     back  = list(back) + [1.0]
#     #     for fkey in self.mesh.faces():
#     #         faces.append({'points'      : [key_xyz[key] for key in self.mesh.face_vertices(fkey)],
#     #                       'color.front' : front,
#     #                       'color.back'  : back})
#     #     self.view.faces = glGenLists(1)
#     #     glNewList(self.view.faces, GL_COMPILE)
#     #     xdraw_polygons(faces)
#     #     glEndList()
#     #     # edges list
#     #     lines = []
#     #     color = hex_to_rgb(self.settings['edges.color'], normalize=True)
#     #     width = self.settings['edges.width']
#     #     for u, v in self.mesh.edges():
#     #         lines.append({'start' : key_xyz[u],
#     #                       'end'   : key_xyz[v],
#     #                       'color' : color,
#     #                       'width' : width})
#     #     self.view.edges = glGenLists(1)
#     #     glNewList(self.view.edges, GL_COMPILE)
#     #     xdraw_cylinders(lines)
#     #     glEndList()

#     # def from_obj(self):
#     #     filename, _ = get_obj_file()
#     #     if filename:
#     #         self.mesh = Mesh.from_obj(filename)
#     #         center_mesh(self.mesh)
#     #         self._make_lists()
#     #         self.view.update()

#     # def from_json(self):
#     #     filename, _ = get_json_file()
#     #     if filename:
#     #         self.mesh = Mesh.from_json(filename)
#     #         center_mesh(self.mesh)
#     #         self._make_lists()
#     #         self.view.update()

#     # def from_polyhedron(self):
#     #     print('from polyhedron')

#     # def zoom_extents(self):
#     #     print('zoom extents')

#     # def zoom_in(self):
#     #     print('zoom in')

#     # def zoom_out(self):
#     #     print('zoom out')


#     @property
#     def settings(self):
#         return self.controller.settings

# #         if self.settings['faces.on']:
# #             if self.faces:
# #                 glCallList(self.faces)
# #         if self.settings['edges.on']:
# #             if self.edges:
# #                 glCallList(self.edges)

#         if self.settings['vertices.on'] or self.settings['vertices_labels.on']:
#             nodes = []
#             node_numbers = []
#             size = self.settings['vertices.size']
#             for key, node in structure.nodes.items():
#                 xyz = structure.node_xyz(key)
#                 nodes.append({
#                     'pos':   xyz,
#                     'color': self.settings['vertices.color'],
#                     'size':  size,
#                 })
#                 node_numbers.append({
#                     'pos':   xyz,
#                     'color': self.settings['vertices_labels.color'],
#                     'text':  str(key),
#                     'shift': [0, 0, self.settings['offset']]
#                 })
#         if self.settings['vertices.on']:
#             xdraw_points(nodes)
#         if self.settings['vertices_labels.on']:
#             xdraw_texts(node_numbers)



#         # Nodes

#         def toggle_view_nodes():
#             self.controller.settings['vertices.on'] = not self.controller.settings['vertices.on']
#             self.view.updateGL()

#         def toggle_view_node_numbers():
#             self.controller.settings['vertices_labels.on'] = not self.controller.settings['vertices_labels.on']
#             self.view.updateGL()

#         layout.addWidget(QtGui.QLabel('Nodes'))

#         button_nodes_on = QtGui.QPushButton('On/Off')
#         button_nodes_on.setCheckable(True)
#         button_nodes_on.setChecked(True)
#         button_nodes_on.clicked.connect(toggle_view_nodes)

#         button_node_numbers_on = QtGui.QPushButton('Label')
#         button_node_numbers_on.setCheckable(True)
#         button_node_numbers_on.setChecked(False)
#         button_node_numbers_on.clicked.connect(toggle_view_node_numbers)

#         node_layout = QtGui.QHBoxLayout()
#         node_layout.addWidget(button_nodes_on)
#         node_layout.addWidget(button_node_numbers_on)



# #     def setup_steps_list(self):
# #         self.steps_list.clear()
# #         if self.structure.steps_order:
# #             self.steps_list.addItems(self.structure.steps_order)
# #         else:
# #             self.steps_list.addItems(['No Steps'])

# #     def setup_fields_list_nodes(self):
# #         self.fields_list_nodes.clear()
# #         current_step = self.steps_list.currentText()
# #         if (current_step != 'No Steps') and (current_step in self.structure.results.keys()):
# #             self.fields_list_nodes.addItems(list(self.structure.results[current_step]['nodal'].keys()))
# #         else:
# #             self.fields_list_nodes.addItems(['No Node Fields'])



# #         # Lines

# #         def change_view_lines():
# #             if self.view.lines_on:
# #                 self.view.lines_on = False
# #                 self.status.showMessage('Elements (lines) display: OFF')
# #             else:
# #                 self.view.lines_on = True
# #                 self.status.showMessage('Elements (lines) display: ON')
# #             self.view.updateGL()

# #         def change_view_line_numbers():
# #             if self.view.line_numbers_on:
# #                 self.view.line_numbers_on = False
# #                 self.status.showMessage('Element numbers (lines) display: OFF')
# #             else:
# #                 self.view.line_numbers_on = True
# #                 self.status.showMessage('Element numbers (lines) display: ON')
# #             self.view.updateGL()

# #         layout.addWidget(QLabel('Lines'))

# #         button_lines_on = QPushButton('On/Off')
# #         button_lines_on.setCheckable(True)
# #         button_lines_on.setChecked(True)
# #         button_lines_on.clicked.connect(change_view_lines)

# #         button_line_numbers_on = QPushButton('No.')
# #         button_line_numbers_on.setCheckable(True)
# #         button_line_numbers_on.setChecked(False)
# #         button_line_numbers_on.clicked.connect(change_view_line_numbers)

# #         lines_layout = QHBoxLayout()
# #         lines_layout.addWidget(button_lines_on)
# #         lines_layout.addWidget(button_line_numbers_on)
# #         layout.addLayout(lines_layout)

# #         # Faces

# #         layout.addWidget(QLabel('Faces'))

# #         def change_view_faces():
# #             if self.view.faces_on:
# #                 self.view.faces_on = False
# #                 self.status.showMessage('Elements (faces) display: OFF')
# #             else:
# #                 self.view.faces_on = True
# #                 self.status.showMessage('Elements (faces) display: ON')
# #             self.view.updateGL()

# #         def change_view_face_numbers():
# #             if self.view.face_numbers_on:
# #                 self.view.face_numbers_on = False
# #                 self.status.showMessage('Element numbers (faces) display: OFF')
# #             else:
# #                 self.view.face_numbers_on = True
# #                 self.status.showMessage('Element numbers (faces) display: ON')
# #             self.view.updateGL()

# #         button_faces_on = QPushButton('On/Off')
# #         button_faces_on.setCheckable(True)
# #         button_faces_on.setChecked(True)
# #         button_faces_on.clicked.connect(change_view_faces)

# #         button_face_numbers_on = QPushButton('No.')
# #         button_face_numbers_on.setCheckable(True)
# #         button_face_numbers_on.setChecked(False)
# #         button_face_numbers_on.clicked.connect(change_view_face_numbers)

# #         faces_layout = QHBoxLayout()
# #         faces_layout.addWidget(button_faces_on)
# #         faces_layout.addWidget(button_face_numbers_on)
# #         layout.addLayout(faces_layout)

# #         # Boundary conditions

# #         layout.addWidget(QLabel('Boundary conditions'))

# #         # toggle = QCheckBox('Displacements')
# #         # toggle.setCheckState(self.view.displacements_on)
# #         # grid.addWidget(toggle, 6, 0)

# #         # def change(state):
# #         #     self.view.displacements_on = state
# #         #     self.view.updateGL()

# #         # toggle.stateChanged.connect(change)

# #         # Loads

# #         layout.addWidget(QLabel('Loads'))

# #         # Results

# #         self.steps_list = QComboBox()
# #         self.steps_list.addItems(['No Steps'])
# #         self.setup_steps_list()

# #         self.fields_list_nodes = QComboBox()
# #         self.fields_list_nodes.addItems(['No Node Fields'])
# #         self.setup_fields_list_nodes()

# #         self.fields_list_elements = QComboBox()
# #         self.fields_list_elements.addItems(['No Element Fields'])
# #         # self.setup_fields_list_elements()

# #         self.components_list = QComboBox()
# #         self.components_list.addItems(['No Components'])

# #         self.steps_list.currentIndexChanged.connect(self.setup_fields_list_nodes)

# #         layout.addWidget(QLabel('Results'))
# #         layout.addWidget(self.steps_list)
# #         layout.addWidget(self.fields_list_nodes)
# #         layout.addWidget(self.fields_list_elements)
# #         layout.addWidget(self.components_list)



# # # ==============================================================================
# # # File menu
# # # ==============================================================================

# #     def file_open(self):
# #         filename, _ = QFileDialog.getOpenFileName(caption='File Open', dir='.', filter='*.obj')
# #         self.structure = Structure.load_from_obj(filename)
# #         self.setup_centralwidget()
# #         self.setup_steps_list()
# #         self.setup_fields_list_nodes()


# #     def add_file_menu(self):
# #         file_menu = self.menu.addMenu('&File')
# #         open_action = file_menu.addAction('&Open')
# #         open_action.triggered.connect(self.file_open)


# # # ==============================================================================
# # # Statusbar
# # # ==============================================================================

# #     def setup_statusbar(self):
# #         self.status = self.main.statusBar()
# #         self.main.setStatusBar(self.status)
# #         self.status.showMessage('-')





# # # ==============================================================================
# # # View
# # # ==============================================================================

# # class View(QGLWidget):

# #     def __init__(self, structure):
# #         QGLWidget.__init__(self)

# #         self.camera = Camera(self)
# #         self.mouse = Mouse(self)


# #         self.structure = structure
# #         self.nodes_on = True
# #         self.node_numbers_on = False
# #         self.lines_on = True
# #         self.line_numbers_on = False
# #         self.faces_on = True
# #         self.face_numbers_on = False

# #         self.update_nodes()
# #         self.update_elements()

# #     def initializeGL(self):
# #         glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
# #         glEnable(GL_MULTISAMPLE)
# #         glShadeModel(GL_SMOOTH)
# #         # glPolygonOffset(1.0, 1.0)
# #         # glEnable(GL_POLYGON_OFFSET_FILL)
# #         glEnable(GL_BLEND)
# #         glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
# #         glEnable(GL_POINT_SMOOTH)
# #         glEnable(GL_LINE_SMOOTH)
# #         glEnable(GL_POLYGON_SMOOTH)
# #         glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
# #         glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
# #         glutInit()

# #         self.qglClearColor(QColor.fromRgb(220, 220, 220))
# #         self.camera.aim()
# #         self.camera.focus()

# #     def resizeGl(self, w, h):
# #         glViewport(0, 0, w, h)
# #         self.camera.aim()
# #         self.camera.focus()

# #     def paintGL(self):

# #         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
# #         # glPushAttrib(GL_POLYGON_BIT)
# #         self.camera.aim()
# #         self.camera.focus()
# #         self.paint()
# #         # glPopAttrib()
# #         # glutSwapBuffers()

# #     def paint(self):
# #         self.draw_axes()

# #         if self.nodes_on:
# #             xdraw_points(self.nodes)
# #         if self.node_numbers_on:
# #             xdraw_texts(self.node_numbers)
# #         if self.lines_on:
# #             xdraw_lines(self.lines)
# #         if self.line_numbers_on:
# #             xdraw_texts(self.line_numbers)
# #         if self.faces_on:
# #             xdraw_polygons(self.faces)
# #         if self.face_numbers_on:
# #             xdraw_texts(self.face_numbers)


# # # ==============================================================================
# # # Events
# # # ==============================================================================

# #     def keyPressAction(self, key):
# #         if key == 45:
# #             self.camera.zoom_out()
# #         elif key == 61:
# #             self.camera.zoom_in()
# #         return

# #     def mouseMoveEvent(self, event):
# #         self.mouse.pos = event.pos()
# #         if event.buttons() & Qt.LeftButton:
# #             self.camera.rotate()
# #             self.mouse.last_pos = event.pos()
# #             self.updateGL()
# #         elif event.buttons() & Qt.RightButton:
# #             self.camera.translate()
# #             self.mouse.last_pos = event.pos()
# #             self.updateGL()

# #     def mousePressEvent(self, event):
# #         self.mouse.last_pos = event.pos()


# # # ==============================================================================
# # # Update
# # # ==============================================================================



# #     def update_elements(self):
# #         ds = 0.01 * self.scale
# #         self.lines = []
# #         self.line_numbers = []
# #         self.faces = []
# #         self.face_numbers = []
# #         line_colour = [0.5, 0.5, 1.0]
# #         face_colour = [0.5, 1.0, 0.5, 0.5]

# #         for key, element in self.structure.elements.items():
# #             nodes = element.nodes
# #             n = len(nodes)
# #             if n == 2:
# #                 sp = self.structure.node_xyz(nodes[0])
# #                 ep = self.structure.node_xyz(nodes[1])
# #                 self.lines.append({
# #                     'start': sp,
# #                     'end':   ep,
# #                     'color': line_colour,
# #                     'width': 5,
# #                 })
# #                 self.line_numbers.append({
# #                     'pos':   self.structure.element_centroid(key),
# #                     'color': [0.5, 0.5, 1.0, 1.0],
# #                     'text':  str(key),
# #                     'shift': [0, 0, ds],
# #                 })
# #             elif (n == 3) or (n == 4):
# #                 points = [self.structure.node_xyz(node) for node in nodes]
# #                 self.faces.append({
# #                     'points':      points,
# #                     'color.front': face_colour,
# #                     'color.back':  face_colour,
# #                 })
# #                 self.face_numbers.append({
# #                     'pos':   self.structure.element_centroid(key),
# #                     'color': [0.0, 0.7, 0.0, 1.0],
# #                     'text':  str(key),
# #                     'shift': [0, 0, ds],
# #                 })



# # #         if self.displacements_on:
# # #             xdraw_lines(self.bcs_translations)
# # #             xdraw_lines(self.bcs_rotations)



# # #             # Displacements

# # #             bc_colour = [0.2, 0.8, 0.2]
# # #             db = -2 * ds
# # #             self.bcs_translations = []
# # #             self.bcs_rotations = []
# # #             for key, displacement in structure.displacements.items():
# # #                 for i, val in displacement.components.items():
# # #                     if val != '-':
# # #                         nodes = displacement.nodes
# # #                         if isinstance(nodes, str):
# # #                             selection = structure.sets[nodes]['selection']
# # #                         elif isinstance(nodes, list):
# # #                             selection = nodes
# # #                         for node in selection:
# # #                             sp = [structure.nodes[node][j] for j in 'xyz']
# # #                             if i == 'x':
# # #                                 ep = add_vectors(sp, [db, 0, 0])
# # #                             elif i == 'y':
# # #                                 ep = add_vectors(sp, [0, db, 0])
# # #                             elif i == 'z':
# # #                                 ep = add_vectors(sp, [0, 0, db])
# # #                             if i in ['x', 'y', 'z']:
# # #                                 self.bcs_translations.append({'start': sp, 'end': ep, 'color': bc_colour, 'width': 3})
# # #                             if i == 'xx':
# # #                                 a = add_vectors(sp, [db / 2, 0, -ds / 2.])
# # #                                 b = add_vectors(sp, [db / 2, 0, +ds / 2.])
# # #                             elif i == 'yy':
# # #                                 a = add_vectors(sp, [0, db / 2, -ds / 2.])
# # #                                 b = add_vectors(sp, [0, db / 2, +ds / 2.])
# # #                             elif i == 'zz':
# # #                                 a = add_vectors(sp, [-ds / 2., 0, db / 2])
# # #                                 b = add_vectors(sp, [+ds / 2., 0, db / 2])
# # #                             if i in ['xx', 'yy', 'zz']:
# # #                                 self.bcs_rotations.append({'start': a, 'end': b, 'color': bc_colour, 'width': 3})
