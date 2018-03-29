
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from vtk import vtkAxesActor
from vtk import vtkActor2D
from vtk import vtkActor
from vtk import vtkCamera
from vtk import vtkGlyph3DMapper
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

        self.draw_axes = True
        self.draw_nodes = True
        self.draw_lines = True
        self.draw_faces = True
        self.draw_node_labels = True
        self.draw_line_labels = True
        self.draw_face_labels = True

        self.camera()
        self.setup(width=1000, height=700)
        self.draw()
        self.start()

    def camera(self):

        xm = 0.5 * (self.xb[0] + self.xb[1])

        self.camera = vtkCamera()
        self.camera.SetPosition(xm, 5 * self.yb[0], self.zb[1])
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetViewUp(0, 0, 1)
        # self.camera.Azimuth(150)
        # self.camera.Elevation(30)

    def setup(self, width, height):

        self.renderer = vtkRenderer()
        self.renderer.SetBackground(1.0, 1.0, 1.0)
        self.renderer.SetBackground2(0.7, 0.7, 0.7)
        self.renderer.GradientBackgroundOn()

        self.render_window = vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(width, height)
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

        # cylinder = vtk.vtkCylinderSource()
        # cylinder.SetCenter(0, 0, 0)
        # cylinder.SetRadius(0.5)
        # cylinder.SetResolution(8)
        # cylinderMapper = vtkPolyDataMapper()
        # cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
        # cylinderActor = vtkActor()
        # cylinderActor.SetMapper(cylinderMapper)
        # # cylinderActor.RotateX(30.0)
        # # cylinderActor.RotateY(-45.0)

        # self.renderer.AddActor(cylinderActor)

        if self.draw_axes:

            axes = vtkAxesActor()
            # transform = vtk.vtkTransform()
            # transform.Translate(1.0, 0.0, 0.0)
            # axes.SetUserTransform(transform)
            self.renderer.AddActor(axes)

        pts = vtkPoints()
        for node in self.structure.nodes:
            pts.InsertNextPoint(self.structure.node_xyz(node))
        PolyData = vtkPolyData()
        PolyData.SetPoints(pts)

        if self.draw_nodes:

            node_size = 0.1
            res = 10

            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(0, 0, 0)
            sphere.SetRadius(node_size)
            sphere.SetPhiResolution(res)
            sphere.SetThetaResolution(res)

            sphereMapper = vtkPolyDataMapper()
            sphereMapper.SetInputConnection(sphere.GetOutputPort())
            sphereActor = vtkActor()
            sphereActor.SetMapper(sphereMapper)
            # # sphereActor.GetProperty().SetSpecular(.6)
            # # sphereActor.GetProperty().SetSpecularPower(30)
            self.renderer.AddActor(sphereActor)

            pointMapper = vtkGlyph3DMapper()
            # pointMapper.SetInputConnection(cylinder.GetOutputPort())
            # pointMapper.SetSourceConnection(sphere.GetOutputPort())
            # # pointMapper.ScalingOff()
            # # pointMapper.ScalarVisibilityOff()

            # pointActor = vtkActor()
            # pointActor.SetMapper(pointMapper)
            # # pointActor.GetProperty().SetDiffuseColor()
            # # pointActor.GetProperty().SetSpecular(.6)
            # # pointActor.GetProperty().SetSpecularColor(1.0, 1.0, 1.0)
            # # pointActor.GetProperty().SetSpecularPower(100)

            # self.renderer.AddActor(pointActor)

            # labelMapper = vtkLabeledDataMapper()
            # labelMapper.SetInputConnection(cylinder.GetOutputPort())
            # labelActor = vtkActor2D()
            # labelActor.SetMapper(labelMapper)

            # self.renderer.AddActor(labelActor)

        if self.draw_lines:

            lines = vtkCellArray()
            line_width = 4

            for ekey, element in self.structure.elements.items():
                nodes = element.nodes

                if len(nodes) == 2:
                    u, v = nodes
                    line = vtkLine()
                    line.GetPointIds().SetId(0, u)
                    line.GetPointIds().SetId(1, v)
                    lines.InsertNextCell(line)

            PolyData.SetLines(lines)

            namedColors = vtk.vtkNamedColors()
            colors = vtk.vtkUnsignedCharArray()
            colors.SetNumberOfComponents(4)
            # try:
            # colors.InsertNextTupleValue(namedColors.GetColor3ub("Tomato"))
            # colors.InsertNextTupleValue(namedColors.GetColor3ub("Mint"))
            # except AttributeError:
                # For compatibility with new VTK generic data arrays.
            # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))
            # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Mint"))
            # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Mint"))
            # colors.InsertNextTypedTuple(namedColors.GetColor3ub("Tomato"))

            # PolyData.GetCellData().SetScalars(colors)

        # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(colors.GetColor3d("Red"));

        if self.draw_faces:

            for ekey, element in self.structure.elements.items():
                nodes = element.nodes

                if len(nodes) == 3:

                    faces = [1,  # number of faces
                             3, nodes[0], nodes[1], nodes[2]]  # number of ids on face, ids
                    #          5, 19, 14, 9, 13, 18,
                    #          5, 19, 18, 17, 16, 15]

                    # PolyData.SetFaces(faces)
                    # PolyData.Initialize()

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(PolyData)
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(line_width)
        self.renderer.AddActor(actor)

            # mapper.SetInputData(dodecahedron.GetPolyData())

    def start(self):

        self.interactor.Start()




    # def MakePolyVertex():
    #     # A polyvertex is a cell represents a set of 0D vertices
    #     numberOfVertices = 6

    #     points = vtk.vtkPoints()
    #     points.InsertNextPoint(0, 0, 0)
    #     points.InsertNextPoint(1, 0, 0)
    #     points.InsertNextPoint(0, 1, 0)
    #     points.InsertNextPoint(0, 0, 1)
    #     points.InsertNextPoint(1, 0, .4)
    #     points.InsertNextPoint(0, 1, .6)

    #     polyVertex = vtk.vtkPolyVertex()
    #     polyVertex.GetPointIds().SetNumberOfIds(numberOfVertices)

    #     for i in range(0, numberOfVertices):
    #         polyVertex.GetPointIds().SetId(i, i)

    #     ug = vtk.vtkUnstructuredGrid()
    #     ug.SetPoints(points)
    #     ug.InsertNextCell(polyVertex.GetCellType(), polyVertex.GetPointIds())

    #     return ug


    # def MakePolyLine():
    #     # A polyline is a cell that represents a set of 1D lines
    #     numberOfVertices = 5

    #     points = vtk.vtkPoints()
    #     points.InsertNextPoint(0, .5, 0)
    #     points.InsertNextPoint(.5, 0, 0)
    #     points.InsertNextPoint(1, .3, 0)
    #     points.InsertNextPoint(1.5, .4, 0)
    #     points.InsertNextPoint(2.0, .4, 0)

    #     polyline = vtk.vtkPolyLine()
    #     polyline.GetPointIds().SetNumberOfIds(numberOfVertices)

    #     for i in range(0, numberOfVertices):
    #         polyline.GetPointIds().SetId(i, i)

    #     ug = vtk.vtkUnstructuredGrid()
    #     ug.SetPoints(points)
    #     ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

    #     return ug


    # def MakeTriangleStrip():
    #     # A triangle is a cell that represents a triangle strip
    #     numberOfVertices = 10

    #     points = vtk.vtkPoints()
    #     points.InsertNextPoint(0, 0, 0)
    #     points.InsertNextPoint(.5, 1, 0)
    #     points.InsertNextPoint(1, -.1, 0)
    #     points.InsertNextPoint(1.5, .8, 0)
    #     points.InsertNextPoint(2.0, -.1, 0)
    #     points.InsertNextPoint(2.5, .9, 0)
    #     points.InsertNextPoint(3.0, 0, 0)
    #     points.InsertNextPoint(3.5, .8, 0)
    #     points.InsertNextPoint(4.0, -.2, 0)
    #     points.InsertNextPoint(4.5, 1.1, 0)

    #     trianglestrip = vtk.vtkTriangleStrip()
    #     trianglestrip.GetPointIds().SetNumberOfIds(numberOfVertices)
    #     for i in range(0, numberOfVertices):
    #         trianglestrip.GetPointIds().SetId(i, i)

    #     ug = vtk.vtkUnstructuredGrid()
    #     ug.SetPoints(points)
    #     ug.InsertNextCell(trianglestrip.GetCellType(), trianglestrip.GetPointIds())

    #     return ug


    # def MakePolygon():
    #     # A polygon is a cell that represents a polygon
    #     numberOfVertices = 6

    #     points = vtk.vtkPoints()
    #     points.InsertNextPoint(0, 0, 0)
    #     points.InsertNextPoint(1, -.1, 0)
    #     points.InsertNextPoint(.8, .5, 0)
    #     points.InsertNextPoint(1, 1, 0)
    #     points.InsertNextPoint(.6, 1.2, 0)
    #     points.InsertNextPoint(0, .8, 0)

    #     polygon = vtk.vtkPolygon()
    #     polygon.GetPointIds().SetNumberOfIds(numberOfVertices)
    #     for i in range(0, numberOfVertices):
    #         polygon.GetPointIds().SetId(i, i)

    #     ug = vtk.vtkUnstructuredGrid()
    #     ug.SetPoints(points)
    #     ug.InsertNextCell(polygon.GetCellType(), polygon.GetPointIds())

    #     return ug


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    app = App(structure=None)
    app.start()
