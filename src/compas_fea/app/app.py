
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from vtk import vtkAxesActor
from vtk import vtkActor2D
from vtk import vtkActor
from vtk import vtkCellArray
from vtk import vtkCamera
from vtk import vtkGlyph3DMapper
from vtk import vtkIdList
from vtk import vtkLabeledDataMapper
from vtk import vtkLine
from vtk import vtkPoints
from vtk import vtkCellArray
from vtk import vtkPolyData
from vtk import vtkPolyDataMapper
from vtk import vtkRenderer
from vtk import vtkRenderWindow
from vtk import vtkRenderWindowInteractor

import vtk


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
]


class App(object):

    """
    """

    def __init__(self, structure, name='compas_fea App'):

        self.name = name
        self.structure = structure
        self.xb, self.yb, self.zb = structure.node_bounds()

        self.draw_axes  = True
        self.draw_grid  = True
        self.draw_nodes = True
        self.draw_lines = True
        self.draw_faces = True
        self.draw_loads = True
        self.draw_bcs   = True

        self.draw_node_labels = True
        self.draw_line_labels = True
        self.draw_face_labels = True

        self.camera()
        self.setup(width=1000, height=700)
        self.draw()
        self.start()

    def camera(self):

        self.camera = vtkCamera()
        self.camera.SetPosition(0.5 * (self.xb[0] + self.xb[1]), -5 * abs(self.yb[0]), self.zb[1])
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetViewUp(0, 0, 1)
        self.camera.Azimuth(30)
        self.camera.Elevation(30)

    def setup(self, width, height):

        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.renderer.SetBackground2(0.7, 0.7, 0.7)
        self.renderer.GradientBackgroundOn()

        self.render_window = vtkRenderWindow()
        self.render_window.SetSize(width, height)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName(self.name)

        self.interactor = vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.Initialize()

        self.renderer.SetActiveCamera(self.camera)
        self.renderer.ResetCamera()
        # self.renderer.ResetCameraClippingRange()
        # self.renderer.GetActiveCamera().Zoom(0.5)
        # self.render_window.Render()

    def draw(self):

        PolyData = vtkPolyData()
        points   = vtkPoints()
        lines    = vtkCellArray()
        polys    = vtkCellArray()

        for node in self.structure.nodes:
            points.InsertNextPoint(self.structure.node_xyz(node))
        PolyData.SetPoints(points)

        line_nodes = []
        tri_nodes = []
        quad_nodes = []

        for ekey, element in self.structure.elements.items():
            nodes = element.nodes

            if len(nodes) == 2:
                line_nodes.append(nodes)

            elif len(nodes) == 3:
                tri_nodes.append(nodes)

            if len(nodes) == 4:
                quad_nodes.append(nodes)

        if self.draw_axes:

            axes = vtkAxesActor()
            self.renderer.AddActor(axes)

        # if self.draw_nodes:

        #     node_size = 0.1
        #     res = 10

        #     sphere = vtk.vtkSphereSource()
        #     sphere.SetCenter(0, 0, 0)
        #     sphere.SetRadius(node_size)
        #     sphere.SetPhiResolution(res)
        #     sphere.SetThetaResolution(res)

        #     sphereMapper = vtkPolyDataMapper()
        #     sphereMapper.SetInputConnection(sphere.GetOutputPort())
        #     sphereActor = vtkActor()
        #     sphereActor.SetMapper(sphereMapper)
        #     # # sphereActor.GetProperty().SetSpecular(.6)
        #     # # sphereActor.GetProperty().SetSpecularPower(30)
        #     self.renderer.AddActor(sphereActor)

        #     pointMapper = vtkGlyph3DMapper()
        #     # pointMapper.SetInputConnection(cylinder.GetOutputPort())
        #     # pointMapper.SetSourceConnection(sphere.GetOutputPort())
        #     # # pointMapper.ScalingOff()
        #     # # pointMapper.ScalarVisibilityOff()

        #     # pointActor = vtkActor()
        #     # pointActor.SetMapper(pointMapper)
        #     # # pointActor.GetProperty().SetDiffuseColor()
        #     # # pointActor.GetProperty().SetSpecular(.6)
        #     # # pointActor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
        #     # # pointActor.GetProperty().SetSpecularPower(100)

        #     # self.renderer.AddActor(pointActor)

        if self.draw_node_labels:

            labelMapper = vtkLabeledDataMapper()
            # labelMapper.SetInputConnection(PolyData.GetOutputPort())
            # labelActor = vtkActor2D()
            # labelActor.SetMapper(labelMapper)
            # self.renderer.AddActor(labelActor)

        if self.draw_lines:

            for u, v in line_nodes:
                line = vtkLine()
                line.GetPointIds().SetId(0, u)
                line.GetPointIds().SetId(1, v)
                lines.InsertNextCell(line)

        #     namedColors = vtk.vtkNamedColors()
        #     colors = vtk.vtkUnsignedCharArray()
        #     colors.SetNumberOfComponents(4)
        #     # try:
        #     # colors.InsertNextTupleValue(namedColors.GetColor3ub("Tomato"))
        #     # colors.InsertNextTupleValue(namedColors.GetColor3ub("Mint"))
        #     # except AttributeError:
        #         # For compatibility with new VTK generic data arrays.
        #     # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))
        #     # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Mint"))
        #     # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Mint"))
        #     # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))

        #     # PolyData.GetCellData().SetScalars(colors)

        # # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(colors.GetColor3d("Red"));

        if self.draw_faces:

            for nodes in tri_nodes + quad_nodes:
                vil = vtkIdList()
                for i in nodes:
                    vil.InsertNextId(i)
                polys.InsertNextCell(vil)

        #             faces = [1,  # number of faces
        #                      3, nodes[0], nodes[1], nodes[2]]  # number of ids on face, ids
        #             #          5, 19, 14, 9, 13, 18,
        #             #          5, 19, 18, 17, 16, 15]
        #             # PolyData.SetFaces(faces)
        #             # PolyData.Initialize()

        line_width = 4

        PolyData.SetLines(lines)
        PolyData.SetPolys(polys)

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(PolyData)
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(line_width)
        self.renderer.AddActor(actor)

        # if self.fdraw_loads:

        #     arrow = vtk.vtkArrowSource()
        #     # geometricObjectSources.append(vtk.vtkConeSource()) for BC

    def start(self):

        self.interactor.Start()

        # # cylinder = vtk.vtkCylinderSource()
        # # cylinder.SetCenter(0, 0, 0)
        # # cylinder.SetRadius(0.5)
        # # cylinder.SetResolution(8)
        # # cylinderMapper = vtkPolyDataMapper()
        # # cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
        # # cylinderActor = vtkActor()
        # # cylinderActor.SetMapper(cylinderMapper)
        # # # cylinderActor.RotateX(30.0)
        # # # cylinderActor.RotateY(-45.0)


        #     scalars = vtk.vtkFloatArray()
        #     for i in range(8):
        #         scalars.InsertTuple1(i, i)
        #     cube.GetPointData().SetScalars(scalars)

        #     cubeMapper.SetScalarRange(0, 7)
        #     cubeActor = vtk.vtkActor()
        #     cubeActor.SetMapper(cubeMapper)

    # transform = vtk.vtkTransform()
    # transform.Translate(1.0, 0.0, 0.0)
    # axes.SetUserTransform(transform)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    app = App(structure=None)
    app.start()
