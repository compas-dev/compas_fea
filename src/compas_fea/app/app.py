
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from PySide.QtGui import QApplication
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QDockWidget
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QPushButton
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QComboBox

from compas_fea.app.view import View

import sys


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


class App(QApplication):

    """ Initialises compas_fea App.

    Parameters
    ----------
    structure : obj
        Structure object.

    Returns
    -------
    None

    """

    def __init__(self, structure=None):
        super(App, self).__init__(sys.argv)

        self.structure = structure
        self.height = 900
        self.width = 1500
        # self.setWindowTitle('compas_fea App - Structure: {0}'.format(self.structure.name))
        self.setup()

# ==============================================================================
# Main
# ==============================================================================

    def setup(self):
        self.setup_mainwindow()
        self.main.setFixedSize(self.width, self.height)

    def setup_mainwindow(self):
        self.main = QMainWindow()
        self.setup_centralwidget()
        self.setup_menubar()
        self.setup_sidebar()
        self.setup_statusbar()

    def start(self):
        self.main.show()
        sys.exit(self.exec_())

    def setup_centralwidget(self):
        self.view = View(self.structure)
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.view.setFocus()
        self.view.setFixedSize(self.width, self.height - 45)
        self.main.setCentralWidget(self.view)

    def setup_menubar(self):
        self.menu = self.main.menuBar()
        self.main.setMenuBar(self.menu)
        self.add_file_menu()
        self.add_view_menu()

# ==============================================================================
# Sidebar
# ==============================================================================

    def setup_sidebar(self):
        self.sidebar = QDockWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setWindowTitle('Sidebar')

        widget = QWidget(self.sidebar)
        layout = QVBoxLayout()

        # Nodes

        def change_view_nodes():
            if self.view.nodes_on:
                self.view.nodes_on = False
                self.status.showMessage('Nodes display: OFF')
            else:
                self.view.nodes_on = True
                self.status.showMessage('Nodes display: ON')
            self.view.updateGL()

        def change_view_node_numbers():
            if self.view.node_numbers_on:
                self.view.node_numbers_on = False
                self.status.showMessage('Node numbers display: OFF')
            else:
                self.view.node_numbers_on = True
                self.status.showMessage('Node numbers display: ON')
            self.view.updateGL()

        layout.addWidget(QLabel('Nodes'))

        button_nodes_on = QPushButton('1')
        button_nodes_on.clicked.connect(change_view_nodes)

        button_node_numbers_on = QPushButton('2')
        button_node_numbers_on.clicked.connect(change_view_node_numbers)

        node_layout = QHBoxLayout()
        node_layout.addWidget(button_nodes_on)
        node_layout.addWidget(button_node_numbers_on)

        layout.addLayout(node_layout)

        # toggle.stateChanged.connect(change)

        # toggle = QCheckBox('Node numbers')
        # toggle.setCheckState(self.view.node_numbers_on)

        # toggle.stateChanged.connect(change)

        # Elements

        def change_view_lines():
            if self.view.lines_on:
                self.view.lines_on = False
                self.status.showMessage('Elements (lines) display: OFF')
            else:
                self.view.lines_on = True
                self.status.showMessage('Elements (lines) display: ON')
            self.view.updateGL()

        def change_view_line_numbers():
            if self.view.line_numbers_on:
                self.view.line_numbers_on = False
                self.status.showMessage('Element numbers (lines) display: OFF')
            else:
                self.view.line_numbers_on = True
                self.status.showMessage('Element numbers (lines) display: ON')
            self.view.updateGL()

        def change_view_faces():
            if self.view.faces_on:
                self.view.faces_on = False
                self.status.showMessage('Elements (faces) display: OFF')
            else:
                self.view.faces_on = True
                self.status.showMessage('Elements (faces) display: ON')
            self.view.updateGL()

        def change_view_face_numbers():
            if self.view.face_numbers_on:
                self.view.face_numbers_on = False
                self.status.showMessage('Element numbers (faces) display: OFF')
            else:
                self.view.face_numbers_on = True
                self.status.showMessage('Element numbers (faces) display: ON')
            self.view.updateGL()

        layout.addWidget(QLabel('Elements'))

        button_lines_on = QPushButton('1')
        button_lines_on.clicked.connect(change_view_lines)

        button_line_numbers_on = QPushButton('2')
        button_line_numbers_on.clicked.connect(change_view_line_numbers)

        button_faces_on = QPushButton('3')
        button_faces_on.clicked.connect(change_view_faces)

        button_face_numbers_on = QPushButton('4')
        button_face_numbers_on.clicked.connect(change_view_face_numbers)

        element_layout = QHBoxLayout()
        element_layout.addWidget(button_lines_on)
        element_layout.addWidget(button_line_numbers_on)
        element_layout.addWidget(button_faces_on)
        element_layout.addWidget(button_face_numbers_on)

        layout.addLayout(element_layout)

        # toggle = QCheckBox('Elements')
        # toggle.setCheckState(self.view.elements_on)
        # grid.addWidget(toggle, 4, 0)

        # def change(state):
        #     self.view.elements_on = state
        #     self.view.updateGL()

        # toggle.stateChanged.connect(change)

        # toggle = QCheckBox('Element numbers')
        # toggle.setCheckState(self.view.element_numbers_on)
        # grid.addWidget(toggle, 5, 0)

        # def change(state):
        #     self.view.element_numbers_on = state
        #     self.view.updateGL()

        # toggle.stateChanged.connect(change)

        # Boundary conditions

        layout.addWidget(QLabel('Boundary conditions'))

        # toggle = QCheckBox('Displacements')
        # toggle.setCheckState(self.view.displacements_on)
        # grid.addWidget(toggle, 6, 0)

        # def change(state):
        #     self.view.displacements_on = state
        #     self.view.updateGL()

        # toggle.stateChanged.connect(change)

        # Loads

        layout.addWidget(QLabel('Loads'))

        # Results

        steps_list = QComboBox()
        steps_list.addItems(['Step1', 'Step2'])

        fields_list = QComboBox()
        fields_list.addItems(['Field1', 'Field2'])

        components_list = QComboBox()
        components_list.addItems(['Component1', 'Component2'])

        layout.addWidget(QLabel('Results'))
        layout.addWidget(steps_list)
        layout.addWidget(fields_list)
        layout.addWidget(components_list)

        layout.addStretch()
        widget.setLayout(layout)
        self.sidebar.setWidget(widget)
        self.main.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

# ==============================================================================
# File menu
# ==============================================================================

    def add_file_menu(self):
        file_menu = self.menu.addMenu('&File')
#         new_action = menu.addAction('&New')
#         open_action = menu.addAction('&Open')
#         save_action = menu.addAction('&Save')
#         new_action.triggered.connect(self.do_newfile)
#         open_action.triggered.connect(self.do_openfile)
#         save_action.triggered.connect(self.do_savefile)


# ==============================================================================
# View menu
# ==============================================================================

    def add_view_menu(self):
        view_menu = self.menu.addMenu('&View')

        sidebar_action = view_menu.addAction('&Sidebar')
        sidebar_action.triggered.connect(self.do_view_sidebar)

    def do_view_sidebar(self):
        self.setup_sidebar()


# ==============================================================================
# Statusbar
# ==============================================================================

    def setup_statusbar(self):
        self.status = self.main.statusBar()
        self.main.setStatusBar(self.status)
        self.status.showMessage('-')
