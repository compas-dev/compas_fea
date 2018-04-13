
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
# from vtk import vtkLabeledDataMapper
from vtk import vtkLine
from vtk import vtkPoints
from vtk import vtkPolyData
from vtk import vtkPolyDataMapper
from vtk import vtkProperty
# from vtk import vtkPropPicker
from vtk import vtkRenderer
from vtk import vtkRenderWindow
from vtk import vtkRenderWindowInteractor
from vtk import vtkSliderRepresentation2D
from vtk import vtkSliderWidget
from vtk import vtkSphereSource
from vtk import vtkUnsignedCharArray
from vtk import vtkInteractorStyleTrackballCamera


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'App',
]


class InteractorStyle(vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver('LeftButtonPressEvent', self.leftButtonPressEvent)
        self.AddObserver('LeftButtonReleaseEvent', self.leftButtonReleaseEvent)
        self.AddObserver('MiddleButtonPressEvent', self.middleButtonPressEvent)
        self.AddObserver('MiddleButtonReleaseEvent', self.middleButtonReleaseEvent)
        self.AddObserver('RightButtonPressEvent', self.rightButtonPressEvent)
        self.AddObserver('RightButtonReleaseEvent', self.rightButtonReleaseEvent)

    def leftButtonPressEvent(self, obj, event):
        self.OnLeftButtonDown()
        return

    def leftButtonReleaseEvent(self, obj, event):
        self.OnLeftButtonUp()
        return

    def middleButtonPressEvent(self, obj, event):
        self.OnMiddleButtonDown()
        return

    def middleButtonReleaseEvent(self, obj, event):
        self.OnMiddleButtonUp()
        return

    def rightButtonPressEvent(self, obj, event):
        self.OnRightButtonDown()
        return

    def rightButtonReleaseEvent(self, obj, event):
        self.OnRightButtonUp()
        return


class App(object):

    """
    """

    def __init__(self, structure, name='compas_fea App'):

        self.structure = structure
        self.xb, self.yb, self.zb = structure.node_bounds()

        self.camera()
        self.setup(width=1500, height=1000, name=name)
        self.draw()
        self.gui()
        self.start()

    def camera(self):

        xm = 0.5 * (self.xb[0] + self.xb[1])
        ym = 0.5 * (self.yb[0] + self.yb[1])
        zm = 0.5 * (self.zb[0] + self.zb[1])
        yc = -5 * abs(self.yb[0])
        zc = self.zb[1]

        self.camera = camera = vtkCamera()
        camera.SetPosition(xm, yc, zc)
        camera.SetFocalPoint(xm, ym, zm)
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
        interactor.SetInteractorStyle(InteractorStyle())
        interactor.SetRenderWindow(render_window)


    def gui(self):
        pass

#         slider_width  = 0.002
#         slider_height = 0.015
#         slider_label  = 0.015

#         self.slider_node_size = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.95], [0.01, 0.95],
#                                                  0.0, 0.05, 0.01, 'Node size', self.interactor)

#         self.slider_line_width = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.80], [0.01, 0.80],
#                                                   0.1, 10.0, 1, 'Linewidth', self.interactor)

#         self.slider_face_opacity = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.65], [0.01, 0.65],
#                                                     0.0, 1.0, 1.0, 'Opacity', self.interactor)

#         self.slider_node_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.5], [0.01, 0.5],
#                                                    0.0, 0.5, 0.1, 'Node labels', self.interactor)

#         self.slider_ele_labels = self.make_slider(slider_width, slider_height, slider_label, [0.1, 0.35], [0.01, 0.35],
#                                                   0.0, 0.5, 0.1, 'Element labels', self.interactor)

#         self.slider_node_size.AddObserver(vtk.vtkCommand.InteractionEvent, node_size_callback(self.node_sphere))
#         self.slider_line_width.AddObserver(vtk.vtkCommand.InteractionEvent, line_width_callback(self.poly))
#         self.slider_face_opacity.AddObserver(vtk.vtkCommand.InteractionEvent, face_opacity_callback(self.poly))

#     @staticmethod
#     def make_slider(width, height, label, posx, posy, minimum, maximum, value, text, interactor):

#         slider = vtkSliderRepresentation2D()
#         slider.SetMinimumValue(minimum)
#         slider.SetMaximumValue(maximum)
#         slider.SetValue(value)
#         slider.SetTitleText(text)
#         slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
#         slider.GetPoint1Coordinate().SetValue(posy[0], posy[1])
#         slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
#         slider.GetPoint2Coordinate().SetValue(posx[0], posx[1])
#         slider.SetTubeWidth(width)
#         slider.SetTitleHeight(height)
#         slider.SetLabelHeight(label)

#         sliderwidget = vtkSliderWidget()
#         sliderwidget.SetInteractor(interactor)
#         sliderwidget.SetRepresentation(slider)
#         sliderwidget.SetAnimationModeToAnimate()
#         sliderwidget.EnabledOn()

#         return sliderwidget

    def draw(self):

        # Colours

        colors = vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)

        # Axes

        axes = vtkAxesActor()
        axes.AxisLabelsOff()
        self.renderer.AddActor(axes)

        # Initialise

        poly    = vtkPolyData()
        bcs     = vtkPolyData()
        bcs_pts = vtkPoints()
#         ele_ data  = vtkPolyData()
#         midpoints = vtkPoints()
        points  = vtkPoints()
        lines   = vtkCellArray()
        faces   = vtkCellArray()

        # Nodes

        for node in self.structure.nodes:
            points.InsertNextPoint(self.structure.node_xyz(node))
        poly.SetPoints(points)

        self.node = node = vtkSphereSource()
        node.SetRadius(0.01)
        node.SetPhiResolution(15)
        node.SetThetaResolution(15)

        mapper = vtkGlyph3DMapper()
        mapper.SetInputData(poly)
        mapper.SetSourceConnection(node.GetOutputPort())
        mapper.ScalingOff()
        mapper.ScalarVisibilityOff()
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetDiffuseColor(0.4, 0.4, 1.0)
        actor.GetProperty().SetDiffuse(.8)
        self.renderer.AddActor(actor)

        # BC

        for key in self.structure.steps[self.structure.steps_order[0]].displacements:
            displacement = self.structure.displacements[key]
            # components = displacement.components
            nodes = self.structure.sets[displacement.nodes]['selection']
            for node in nodes:
                bcs_pts.InsertNextPoint(self.structure.node_xyz(node))

        bcs.SetPoints(bcs_pts)

        bc = vtkSphereSource()
        bc.SetRadius(0.05)
        bc.SetPhiResolution(15)
        bc.SetThetaResolution(15)

        mapper = vtkGlyph3DMapper()
        mapper.SetInputData(bcs)
        mapper.SetSourceConnection(bc.GetOutputPort())
        mapper.ScalingOff()
        mapper.ScalarVisibilityOff()
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetDiffuseColor(1.0, 0.5, 0.0)
        actor.GetProperty().SetDiffuse(.8)
        self.renderer.AddActor(actor)

        # Group

        trusses = []
        beams   = []
        springs = []
        tris    = []
        quads   = []
#         line_types = []

        for ekey, element in self.structure.elements.items():
            nodes = element.nodes
#             midpoints.InsertNextPoint(self.structure.element_centroid(ekey))

            if len(nodes) == 2:
                if element.__name__ == 'TrussElement':
                    trusses.append(nodes)
                elif element.__name__ == 'BeamElement':
                    beams.append(nodes)
                elif element.__name__ == 'SpringElement':
                    springs.append(nodes)

            elif len(nodes) == 3:
                tris.append(nodes)

            if len(nodes) == 4:
                quads.append(nodes)

#         ele_data.SetPoints(midpoints)

        # Lines

        for u, v in springs:
            line = vtkLine()
            line.GetPointIds().SetId(0, u)
            line.GetPointIds().SetId(1, v)
            lines.InsertNextCell(line)
            try:
                colors.InsertNextTypedTuple([200, 255, 0])
            except:
                colors.InsertNextTupleValue([200, 255, 0])

        for u, v in trusses:
            line = vtkLine()
            line.GetPointIds().SetId(0, u)
            line.GetPointIds().SetId(1, v)
            lines.InsertNextCell(line)
            try:
                colors.InsertNextTypedTuple([255, 150, 150])
            except:
                colors.InsertNextTupleValue([255, 150, 150])

        for u, v in beams:
            line = vtkLine()
            line.GetPointIds().SetId(0, u)
            line.GetPointIds().SetId(1, v)
            lines.InsertNextCell(line)
            try:
                colors.InsertNextTypedTuple([150, 150, 255])
            except:
                colors.InsertNextTupleValue([150, 150, 255])

#         # Node labels

#         lmapper = vtkLabeledDataMapper()
#         lmapper.SetInputData(poly)
#         # lmapper.GetTextProperty().LabelHeight(10)
#         # lactor.GetTextProperty().SetFontSize(10)
#         lactor = vtkActor2D()
#         lactor.SetMapper(lmapper)
#         # self.renderer.AddActor(lactor)

#         # Element labels

#         emapper = vtkLabeledDataMapper()
#         emapper.SetInputData(ele_data)
#         eactor = vtkActor2D()
#         eactor.SetMapper(emapper)
#         # self.renderer.AddActor(eactor)

        # Faces

        for j in tris + quads:
            vil = vtkIdList()
            for i in j:
                vil.InsertNextId(i)
            faces.InsertNextCell(vil)
            try:
                colors.InsertNextTypedTuple([150, 255, 150])
            except:
                colors.InsertNextTupleValue([150, 255, 150])

        # Set-up PolyData

        poly.SetLines(lines)
        poly.SetPolys(faces)
        poly.GetCellData().SetScalars(colors)

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(poly)

        self.poly = actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(2)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor([0, 0.5, 0])
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetInterpolationToGouraud()
        self.renderer.AddActor(actor)

    def start(self):

        self.interactor.Initialize()
        self.interactor.Start()

#         # if self.fdraw_loads:

#         #     arrow = vtk.vtkArrowSource()
#         #     # geometricObjectSources.append(vtk.vtkConeSource()) for BC
#         # arrowSource.SetTipResolution(31)
#         # arrowSource.SetShaftResolution(21)
#         # https://lorensen.github.io/VTKExamples/site/Python/GeometricObjects/OrientedArrow/

#         # cylinder = vtk.vtkCylinderSource()
#         # cylinder.SetCenter(0, 0, 0)
#         # cylinder.SetRadius(0.5)
#         # cylinder.SetResolution(8)
#         # cylinderSource.SetHeight(7.0)
#         # cylinderMapper = vtkPolyDataMapper()
#         # cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
#         # cylinderActor = vtkActor()
#         # cylinderActor.SetMapper(cylinderMapper)
#         # # cylinderActor.RotateX(30.0)
#         # # cylinderActor.RotateY(-45.0)

#         #     scalars = vtk.vtkFloatArray()
#         #     for i in range(8):
#         #         scalars.InsertTuple1(i, i)
#         #     cube.GetPointData().SetScalars(scalars)

#         #     cubeMapper.SetScalarRange(0, 7)
#         #     cubeActor = vtk.vtkActor()
#         #     cubeActor.SetMapper(cubeMapper)

#     # transform = vtk.vtkTransform()
#     # transform.Translate(1.0, 0.0, 0.0)
#     # transform.Scale(length, length, length)
#     # axes.SetUserTransform(transform)

#     # contour = vtk.vtkDiscreteMarchingCubes()  # for label images
#     # if vtk.VTK_MAJOR_VERSION <= 5:
#     #     contour.SetInput(voi.GetOutput())
#     # else:
#     #     contour.SetInputConnection(voi.GetOutputPort())


# class node_size_callback():

#     def __init__(self, node_sphere):
#         self.node_sphere = node_sphere

#     def __call__(self, caller, ev):
#         value = caller.GetRepresentation().GetValue()
#         self.node_sphere.SetRadius(value)


# class line_width_callback():

#     def __init__(self, poly):
#         self.poly = poly

#     def __call__(self, caller, ev):
#         value = caller.GetRepresentation().GetValue()
#         self.poly.GetProperty().SetLineWidth(value)


# class face_opacity_callback():

#     def __init__(self, poly):
#         self.poly = poly

#     def __call__(self, caller, ev):
#         value = caller.GetRepresentation().GetValue()
#         self.poly.GetProperty().SetOpacity(value)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/mesh_roof.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
