
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.viewers import VtkViewer


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'App',
]


class App(VtkViewer):

    def __init__(self, structure, name='compas_fea App', width=1500, height=1000, data={}):

        data = {}

        data['vertices'] = {i: structure.node_xyz(i) for i in structure.nodes}
        # data['edges'] = [
        #     {'start': 0, 'end': 4, 'color': [0, 0, 0]},
        # ]
        # data['faces'] = {
        #     0: {'vertices': [0, 1, 4], 'color': [250, 150, 150]},
        # }
        # 'fixed': [[0, 1]],

        VtkViewer.__init__(self, name=name, width=width, height=height, data=data)

#         self.structure = structure
#         self.xb, self.yb, self.zb = structure.node_bounds()

    #         xm = 0.5 * (self.xb[0] + self.xb[1])
    #         ym = 0.5 * (self.yb[0] + self.yb[1])
    #         zm = 0.5 * (self.zb[0] + self.zb[1])
    #         yc = -5 * abs(self.yb[0])
    #         zc = self.zb[1]

# #         self.slider_node_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.5], [0.01, 0.5],
# #                                                    0.0, 0.5, 0.1, 'Node labels', self.interactor)

# #         self.slider_ele_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.35], [0.01, 0.35],
# #                                                   0.0, 0.5, 0.1, 'Element labels', self.interactor)
# #         self.slider_line_width.AddObserver(vtk.vtkCommand.InteractionEvent, line_width_callback(self.poly))
# #         self.slider_face_opacity.AddObserver(vtk.vtkCommand.InteractionEvent, face_opacity_callback(self.poly))

#         bcs     = vtkPolyData()
#         bcs_pts = vtkPoints()
# #         ele_ data  = vtkPolyData()
# #         midpoints = vtkPoints()
#         points  = vtkPoints()
#         lines   = vtkCellArray()
#         faces   = vtkCellArray()

#         # BC

#         for key in self.structure.steps[self.structure.steps_order[0]].displacements:
#             displacement = self.structure.displacements[key]
#             # components = displacement.components
#             nodes = self.structure.sets[displacement.nodes]['selection']
#             for node in nodes:
#                 bcs_pts.InsertNextPoint(self.structure.node_xyz(node))

#         bcs.SetPoints(bcs_pts)

#         bc = vtkSphereSource()
#         bc.SetRadius(0.05)
#         bc.SetPhiResolution(15)
#         bc.SetThetaResolution(15)

#         mapper = vtkGlyph3DMapper()
#         mapper.SetInputData(bcs)
#         mapper.SetSourceConnection(bc.GetOutputPort())
#         mapper.ScalingOff()
#         mapper.ScalarVisibilityOff()
#         actor = vtkActor()
#         actor.SetMapper(mapper)
#         actor.GetProperty().SetDiffuseColor(1.0, 0.5, 0.0)
#         actor.GetProperty().SetDiffuse(.8)
#         self.renderer.AddActor(actor)

#         # Group

#         trusses = []
#         beams   = []
#         springs = []
#         tris    = []
#         quads   = []
# #         line_types = []

#         for ekey, element in self.structure.elements.items():
#             nodes = element.nodes
# #             midpoints.InsertNextPoint(self.structure.element_centroid(ekey))

#             if len(nodes) == 2:
#                 if element.__name__ == 'TrussElement':
#                     trusses.append(nodes)
#                 elif element.__name__ == 'BeamElement':
#                     beams.append(nodes)
#                 elif element.__name__ == 'SpringElement':
#                     springs.append(nodes)

#             elif len(nodes) == 3:
#                 tris.append(nodes)

#             if len(nodes) == 4:
#                 quads.append(nodes)

# #         ele_data.SetPoints(midpoints)

#         # Lines

#         for u, v in springs:
#             line = vtkLine()
#             line.GetPointIds().SetId(0, u)
#             line.GetPointIds().SetId(1, v)
#             lines.InsertNextCell(line)
#             try:
#                 colors.InsertNextTypedTuple([200, 255, 0])
#             except:
#                 colors.InsertNextTupleValue([200, 255, 0])

#         for u, v in trusses:
#             line = vtkLine()
#             line.GetPointIds().SetId(0, u)
#             line.GetPointIds().SetId(1, v)
#             lines.InsertNextCell(line)
#             try:
#                 colors.InsertNextTypedTuple([255, 150, 150])
#             except:
#                 colors.InsertNextTupleValue([255, 150, 150])

#         for u, v in beams:
#             line = vtkLine()
#             line.GetPointIds().SetId(0, u)
#             line.GetPointIds().SetId(1, v)
#             lines.InsertNextCell(line)
#             try:
#                 colors.InsertNextTypedTuple([150, 150, 255])
#             except:
#                 colors.InsertNextTupleValue([150, 150, 255])

# #         # Node labels

# #         lmapper = vtkLabeledDataMapper()
# #         lmapper.SetInputData(poly)
# #         # lmapper.GetTextProperty().LabelHeight(10)
# #         # lactor.GetTextProperty().SetFontSize(10)
# #         lactor = vtkActor2D()
# #         lactor.SetMapper(lmapper)
# #         # self.renderer.AddActor(lactor)

# #         # Element labels

# #         emapper = vtkLabeledDataMapper()
# #         emapper.SetInputData(ele_data)
# #         eactor = vtkActor2D()
# #         eactor.SetMapper(emapper)
# #         # self.renderer.AddActor(eactor)

# #         # if self.fdraw_loads:

# #         #     arrow = vtk.vtkArrowSource()
# #         #     # geometricObjectSources.append(vtk.vtkConeSource()) for BC
# #         # arrowSource.SetTipResolution(31)
# #         # arrowSource.SetShaftResolution(21)
# #         # https://lorensen.github.io/VTKExamples/site/Python/GeometricObjects/OrientedArrow/

# #         #     scalars = vtk.vtkFloatArray()
# #         #     for i in range(8):
# #         #         scalars.InsertTuple1(i, i)
# #         #     cube.GetPointData().SetScalars(scalars)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/truss_tower.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
