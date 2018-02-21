
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from PySide.QtGui import QApplication
from PySide.QtGui import QBoxLayout
from PySide.QtGui import QDockWidget
from PySide.QtGui import QWidget
from PySide.QtGui import QLabel
from PySide.QtGui import QPushButton
from PySide.QtGui import QGridLayout

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
        self.setup()

    # ==============================================================================
    # Main
    # ==============================================================================

    def setup(self):
        self.setup_mainwindow()
        # self.setWindowTitle('compas_fea App - Structure: {0}'.format(self.structure.name))
        self.main.setFixedSize(1360, 768)

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
        self.view = view = View(self.structure)
#         view.setFocusPolicy(Qt.StrongFocus)
#         view.setFocus()
        self.main.setCentralWidget(view)

    def setup_menubar(self):
        self.menu = menu = self.main.menuBar()
        self.main.setMenuBar(menu)
        self.add_filemenu()

    # ==============================================================================
    # sidebar
    # ==============================================================================

    def setup_sidebar(self):
        self.sidebar = sidebar = QDockWidget()
        # sidebar.setAllowedAreas(Qt.LeftDockWidgetArea)
        # sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
        sidebar.setFixedWidth(150)
        widget = QWidget(sidebar)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        grid = QGridLayout()

        # Nodes

        def change_view_nodes():
            print('view nodes')
            # self.view.nodes_on = state
        #     self.view.updateGL()

        button_nodes_on = QPushButton('1')
        button_nodes_on.clicked.connect(change_view_nodes)

        grid.addWidget(QLabel('Nodes'), 0, 0)
        grid.addWidget(button_nodes_on, 1, 0)






        # toggle.stateChanged.connect(change)

        # # Node numbers

        # toggle = QCheckBox('Node numbers')
        # toggle.setCheckState(self.view.node_numbers_on)
        # grid.addWidget(toggle, 2, 0)

        # def change(state):
        #     self.view.node_numbers_on = state
        #     self.view.updateGL()

        # toggle.stateChanged.connect(change)

        # Elements

        grid.addWidget(QLabel('Elements'), 2, 0)

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

        grid.addWidget(QLabel('Boundary conditions'), 4, 0)

        # toggle = QCheckBox('Displacements')
        # toggle.setCheckState(self.view.displacements_on)
        # grid.addWidget(toggle, 6, 0)

        # def change(state):
        #     self.view.displacements_on = state
        #     self.view.updateGL()

        # toggle.stateChanged.connect(change)

        # Loads

        grid.addWidget(QLabel('Loads'), 6, 0)

        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        sidebar.setWidget(widget)
        self.main.addDockWidget(Qt.LeftDockWidgetArea, sidebar)

    # ==============================================================================
    # file menu
    # ==============================================================================

    def add_filemenu(self):
        menu = self.menu.addMenu('&File')
#         new_action = menu.addAction('&New')
#         open_action = menu.addAction('&Open')
#         save_action = menu.addAction('&Save')
#         new_action.triggered.connect(self.do_newfile)
#         open_action.triggered.connect(self.do_openfile)
#         save_action.triggered.connect(self.do_savefile)

#     def do_newfile(self):
#         """ Action for File > New.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.status.showMessage('File created')

#     def do_openfile(self):
#         """ Action for File > Open.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.status.showMessage('File opened')

#     def do_savefile(self):
#         """ Action for File > Save.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.status.showMessage('File saved')

    # ==============================================================================
    # statusbar
    # ==============================================================================

    def setup_statusbar(self):
        self.status = self.main.statusBar()
        self.main.setStatusBar(self.status)
        self.status.showMessage('-')
