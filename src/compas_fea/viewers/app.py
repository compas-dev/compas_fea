# import sys

# from PySide.QtCore import Qt
# from PySide.QtGui import QMainWindow
# from PySide.QtGui import QApplication
# from PySide.QtGui import QBoxLayout
# from PySide.QtGui import QDockWidget
# from PySide.QtGui import QWidget
# from PySide.QtGui import QLabel
# from PySide.QtGui import QGridLayout
# from PySide.QtGui import QCheckBox

# from compas_fea.viewers.view import View


# __author__     = ['Andrew Liew <liew@arch.ethz.ch>']
# __copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
# __license__    = 'MIT License'
# __email__      = 'liew@arch.ethz.ch'


# class App(QApplication):

#     def __init__(self, structure=None):
#         """ Initialises compas_fea App.

#         Parameters:
#             structure (obj): Structure object.

#         Returns:
#             None
#         """
#         super(App, self).__init__(sys.argv)
#         self.setApplicationName('compas_fea app')
#         self.structure = structure
#         self.setup()

#     # ==============================================================================
#     # main
#     # ==============================================================================

#     def setup(self):
#         self.setup_mainwindow()
#         self.main.setFixedSize(1360, 768)

#     def setup_mainwindow(self):
#         """ Set-up the main Qt window.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.main = QMainWindow()
#         self.setup_centralwidget()
#         self.setup_menubar()
#         self.setup_sidebar()
#         self.setup_statusbar()

#     def start(self):
#         """ Enter the main QT loop.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.main.show()
#         sys.exit(self.exec_())

#     def setup_centralwidget(self):
#         """ Set-up the central widget.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.view = view = View(self.structure)
#         view.setFocusPolicy(Qt.StrongFocus)
#         view.setFocus()
#         self.main.setCentralWidget(view)

#     def setup_menubar(self):
#         """ Set-up the main menubar.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.menu = menu = self.main.menuBar()
#         self.main.setMenuBar(menu)
#         self.add_filemenu()

#     # ==============================================================================
#     # sidebar
#     # ==============================================================================

#     def setup_sidebar(self):
#         """ Set-up the left sidebar.

#         Parameters:
#             None

#         Returns:
#             None
#         """

#         self.sidebar = sidebar = QDockWidget()
#         sidebar.setAllowedAreas(Qt.LeftDockWidgetArea)
#         sidebar.setFeatures(QDockWidget.NoDockWidgetFeatures)
#         sidebar.setFixedWidth(240)
#         widget = QWidget(sidebar)
#         layout = QBoxLayout(QBoxLayout.TopToBottom)
#         toggles = QGridLayout()

#         # Node displays

#         toggles.addWidget(QLabel('Node displays'), 0, 0)

#         # Nodes

#         toggle = QCheckBox('Nodes')
#         toggle.setCheckState(self.view.nodes_on)
#         toggles.addWidget(toggle, 1, 0)

#         def change(state):
#             self.view.nodes_on = state
#             self.view.updateGL()

#         toggle.stateChanged.connect(change)

#         # Node numbers

#         toggle = QCheckBox('Node numbers')
#         toggle.setCheckState(self.view.node_numbers_on)
#         toggles.addWidget(toggle, 2, 0)

#         def change(state):
#             self.view.node_numbers_on = state
#             self.view.updateGL()

#         toggle.stateChanged.connect(change)

#         # Element displays

#         toggles.addWidget(QLabel('Element displays'), 3, 0)

#         # Elements

#         toggle = QCheckBox('Elements')
#         toggle.setCheckState(self.view.elements_on)
#         toggles.addWidget(toggle, 4, 0)

#         def change(state):
#             self.view.elements_on = state
#             self.view.updateGL()

#         toggle.stateChanged.connect(change)

#         # Element numbers

#         toggle = QCheckBox('Element numbers')
#         toggle.setCheckState(self.view.element_numbers_on)
#         toggles.addWidget(toggle, 5, 0)

#         def change(state):
#             self.view.element_numbers_on = state
#             self.view.updateGL()

#         toggle.stateChanged.connect(change)

#         # Displacements

#         toggle = QCheckBox('Displacements')
#         toggle.setCheckState(self.view.displacements_on)
#         toggles.addWidget(toggle, 6, 0)

#         def change(state):
#             self.view.displacements_on = state
#             self.view.updateGL()

#         toggle.stateChanged.connect(change)

#         layout.addLayout(toggles)
#         layout.addStretch()
#         widget.setLayout(layout)
#         sidebar.setWidget(widget)
#         self.main.addDockWidget(Qt.LeftDockWidgetArea, sidebar)

#     # ==============================================================================
#     # file menu
#     # ==============================================================================

#     def add_filemenu(self):
#         """ Add a file menu item to the main menubar.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         menu = self.menu.addMenu('&File')
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

#     # ==============================================================================
#     # statusbar
#     # ==============================================================================

#     def setup_statusbar(self):
#         """ Set-up the statusbar.

#         Parameters:
#             None

#         Returns:
#             None
#         """
#         self.status = self.main.statusBar()
#         self.main.setStatusBar(self.status)
#         self.status.showMessage('')
