
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from vtk import vtkActor2D
from vtk import vtkActor
from vtk import vtkAxesActor
from vtk import vtkCamera
from vtk import vtkCellArray
from vtk import vtkGlyph3DMapper
from vtk import vtkIdList
from vtk import vtkLabeledDataMapper
from vtk import vtkLine
from vtk import vtkNamedColors
from vtk import vtkPoints
from vtk import vtkPolyData
from vtk import vtkPolyDataMapper
from vtk import vtkRenderer
from vtk import vtkRenderWindow
from vtk import vtkRenderWindowInteractor
from vtk import vtkSliderRepresentation2D
from vtk import vtkSliderWidget
from vtk import vtkSphereSource
from vtk import vtkUnsignedCharArray

import vtk


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'App',
]


class App(object):

    """
    """

    def __init__(self, structure, name='compas_fea App'):

        self.structure = structure
        self.xb, self.yb, self.zb = structure.node_bounds()
        self.draw_axes  = True
        self.draw_grid  = True

        self.camera()
        self.setup(width=1000, height=700, name=name)
        self.draw()
        self.gui()
        self.start()

    def camera(self):

        xc = 0.5 * (self.xb[0] + self.xb[1])
        yc = -5 * abs(self.yb[0])
        zc = self.zb[1]

        self.camera = camera = vtkCamera()
        camera.SetPosition(xc, yc, zc)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.Azimuth(30)
        camera.Elevation(30)

    def setup(self, width, height, name):

        self.renderer = renderer = vtkRenderer()
        renderer.SetBackground(1.0, 1.0, 1.0)
        renderer.SetBackground2(0.8, 0.8, 0.8)
        renderer.GradientBackgroundOn()
        renderer.SetActiveCamera(self.camera)
        renderer.ResetCamera()
        renderer.ResetCameraClippingRange()

        self.render_window = render_window = vtkRenderWindow()
        render_window.SetSize(width, height)
        render_window.SetWindowName(name)
        render_window.AddRenderer(renderer)

        self.interactor = interactor = vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

    def gui(self):

        slider_width  = 0.002
        slider_height = 0.015
        slider_label  = 0.015

        self.slider_node_size = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.95], [0.01, 0.95],
                                                 0.0, 0.05, 0.01, 'Node size', self.interactor)

        self.slider_line_width = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.80], [0.01, 0.80],
                                                 0.1, 10.0, 1, 'Linewidth', self.interactor)

        self.slider_face_opacity = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.65], [0.01, 0.65],
                                                    0.0, 1.0, 1.0, 'Opacity', self.interactor)

        self.slider_node_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.5], [0.01, 0.5],
                                                   0.0, 0.5, 0.1, 'Node labels', self.interactor)

        self.slider_ele_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.35], [0.01, 0.35],
                                                  0.0, 0.5, 0.1, 'Element labels', self.interactor)

        self.slider_node_size.AddObserver(vtk.vtkCommand.InteractionEvent, node_size_callback(self.node_sphere))
        self.slider_line_width.AddObserver(vtk.vtkCommand.InteractionEvent, line_width_callback(self.poly_data))
        self.slider_face_opacity.AddObserver(vtk.vtkCommand.InteractionEvent, face_opacity_callback(self.poly_data))

    @staticmethod
    def make_slider(width, height, label, posx, posy, minimum, maximum, value, text, interactor):

        slider = vtkSliderRepresentation2D()
        slider.SetMinimumValue(minimum)
        slider.SetMaximumValue(maximum)
        slider.SetValue(value)
        slider.SetTitleText(text)
        slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider.GetPoint1Coordinate().SetValue(posy[0], posy[1])
        slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider.GetPoint2Coordinate().SetValue(posx[0], posx[1])
        slider.SetTubeWidth(width)
        slider.SetTitleHeight(height)
        slider.SetLabelHeight(label)

        sliderwidget = vtkSliderWidget()
        sliderwidget.SetInteractor(interactor)
        sliderwidget.SetRepresentation(slider)
        sliderwidget.SetAnimationModeToAnimate()
        sliderwidget.EnabledOn()

        return sliderwidget

    def draw(self):

        # Colours

        named_colors = vtkNamedColors()
        named_colors.SetColor('red', [255, 100, 100, 255])
        named_colors.SetColor('green', [150, 255, 150, 255])
        named_colors.SetColor('dark_green', [0, 20, 0, 255])
        named_colors.SetColor('blue', [100, 100, 255, 255])
        named_colors.SetColor('black', [0, 0, 0, 255])
        colors = vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)

        # Axes

        if self.draw_axes:
            axes = vtkAxesActor()
            axes.AxisLabelsOff()
            self.renderer.AddActor(axes)

        # Initialise PolyData

        poly_data = vtkPolyData()
        ele_data  = vtkPolyData()
        midpoints = vtkPoints()
        points    = vtkPoints()
        lines     = vtkCellArray()
        faces     = vtkCellArray()

        # Nodes

        for node in self.structure.nodes:
            points.InsertNextPoint(self.structure.node_xyz(node))
        poly_data.SetPoints(points)

        self.node_sphere = node_sphere = vtkSphereSource()
        node_sphere.SetRadius(0.01)
        node_sphere.SetPhiResolution(15)
        node_sphere.SetThetaResolution(15)
        pmapper = vtkGlyph3DMapper()
        pmapper.SetInputData(poly_data)
        pmapper.SetSourceConnection(node_sphere.GetOutputPort())
        pmapper.ScalingOff()
        pmapper.ScalarVisibilityOff()
        pactor = vtkActor()
        pactor.SetMapper(pmapper)
        pactor.GetProperty().SetColor(named_colors.GetColor3d('blue'))
        self.renderer.AddActor(pactor)

        # Group elements

        line_nodes = []
        tri_nodes  = []
        quad_nodes = []
        line_types = []

        for ekey, element in self.structure.elements.items():
            nodes = element.nodes
            midpoints.InsertNextPoint(self.structure.element_centroid(ekey))

            if len(nodes) == 2:
                line_nodes.append(nodes)
                line_types.append(element.__name__)

            elif len(nodes) == 3:
                tri_nodes.append(nodes)

            if len(nodes) == 4:
                quad_nodes.append(nodes)

        ele_data.SetPoints(midpoints)

        # Lines

        for uv, etype in zip(line_nodes, line_types):

            u, v = uv

            line = vtkLine()
            line.GetPointIds().SetId(0, u)
            line.GetPointIds().SetId(1, v)
            lines.InsertNextCell(line)

            if etype == 'BeamElement':
                col = 'red'
            elif etype == 'TrussElement':
                col = 'blue'
            elif etype == 'SpringElement':
                col = 'black'

            try:
                colors.InsertNextTypedTuple(named_colors.GetColor3ub(col))
            except:
                colors.InsertNextTupleValue(named_colors.GetColor3ub(col))

        # Node labels

        lmapper = vtkLabeledDataMapper()
        lmapper.SetInputData(poly_data)
        # lmapper.GetTextProperty().LabelHeight(10)
        # lactor.GetTextProperty().SetFontSize(10)
        lactor = vtkActor2D()
        lactor.SetMapper(lmapper)
        # self.renderer.AddActor(lactor)

        # Element labels

        emapper = vtkLabeledDataMapper()
        emapper.SetInputData(ele_data)
        eactor = vtkActor2D()
        eactor.SetMapper(emapper)
        # self.renderer.AddActor(eactor)

        # Faces

        for nodes in tri_nodes + quad_nodes:

            vil = vtkIdList()
            for i in nodes:
                vil.InsertNextId(i)
            faces.InsertNextCell(vil)
            try:
                colors.InsertNextTypedTuple(named_colors.GetColor3ub('green'))
            except:
                colors.InsertNextTupleValue(named_colors.GetColor3ub('green'))

        # Set-up PolyData

        poly_data.SetLines(lines)
        poly_data.SetPolys(faces)
        poly_data.GetCellData().SetScalars(colors)
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        self.poly_data = actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(1)
        # actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(named_colors.GetColor3ub('dark_green'))
        actor.GetProperty().SetOpacity(1.0)
        self.renderer.AddActor(actor)

    def start(self):

        self.interactor.Initialize()
        self.interactor.Start()

        # if self.fdraw_loads:

        #     arrow = vtk.vtkArrowSource()
        #     # geometricObjectSources.append(vtk.vtkConeSource()) for BC
        # arrowSource.SetTipResolution(31)
        # arrowSource.SetShaftResolution(21)
        # https://lorensen.github.io/VTKExamples/site/Python/GeometricObjects/OrientedArrow/

        # cylinder = vtk.vtkCylinderSource()
        # cylinder.SetCenter(0, 0, 0)
        # cylinder.SetRadius(0.5)
        # cylinder.SetResolution(8)
        # cylinderSource.SetHeight(7.0)
        # cylinderMapper = vtkPolyDataMapper()
        # cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
        # cylinderActor = vtkActor()
        # cylinderActor.SetMapper(cylinderMapper)
        # # cylinderActor.RotateX(30.0)
        # # cylinderActor.RotateY(-45.0)

        #     scalars = vtk.vtkFloatArray()
        #     for i in range(8):
        #         scalars.InsertTuple1(i, i)
        #     cube.GetPointData().SetScalars(scalars)

        #     cubeMapper.SetScalarRange(0, 7)
        #     cubeActor = vtk.vtkActor()
        #     cubeActor.SetMapper(cubeMapper)

    # transform = vtk.vtkTransform()
    # transform.Translate(1.0, 0.0, 0.0)
    # transform.Scale(length, length, length)
    # axes.SetUserTransform(transform)

    # contour = vtk.vtkDiscreteMarchingCubes()  # for label images
    # if vtk.VTK_MAJOR_VERSION <= 5:
    #     contour.SetInput(voi.GetOutput())
    # else:
    #     contour.SetInputConnection(voi.GetOutputPort())


class node_size_callback():

    def __init__(self, node_sphere):
        self.node_sphere = node_sphere

    def __call__(self, caller, ev):
        value = caller.GetRepresentation().GetValue()
        self.node_sphere.SetRadius(value)


class line_width_callback():

    def __init__(self, poly_data):
        self.poly_data = poly_data

    def __call__(self, caller, ev):
        value = caller.GetRepresentation().GetValue()
        self.poly_data.GetProperty().SetLineWidth(value)


class face_opacity_callback():

    def __init__(self, poly_data):
        self.poly_data = poly_data

    def __call__(self, caller, ev):
        value = caller.GetRepresentation().GetValue()
        self.poly_data.GetProperty().SetOpacity(value)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/mesh_roof.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
