
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
        data['edges'] = []

        # data['faces'] = {
        #     0: {'vertices': [0, 1, 4], 'color': [250, 150, 150]},
        # }
        # 'fixed': [[0, 1]],

        for ekey, element in structure.elements.items():
            nodes = element.nodes

            if len(nodes) == 2:
                sp, ep = nodes
                if element.__name__ == 'TrussElement':
                    col = [255, 150, 150]
                elif element.__name__ == 'BeamElement':
                    col = [150, 150, 255]
                elif element.__name__ == 'SpringElement':
                    col = [200, 255, 0]
                data['edges'].append({'u': sp, 'v': ep, 'color': col})

        #     # elif len(nodes) == 3:
        #     #     tris.append(nodes)

        #     # if len(nodes) == 4:
        #     #     quads.append(nodes)

        VtkViewer.__init__(self, name=name, width=width, height=height, data=data)

#         self.structure = structure
#         self.xb, self.yb, self.zb = structure.node_bounds()

#             midpoints.InsertNextPoint(self.structure.element_centroid(ekey))
    #         xm = 0.5 * (self.xb[0] + self.xb[1])
    #         ym = 0.5 * (self.yb[0] + self.yb[1])
    #         zm = 0.5 * (self.zb[0] + self.zb[1])
    #         yc = -5 * abs(self.yb[0])
    #         zc = self.zb[1]

#         # BC

#         for key in self.structure.steps[self.structure.steps_order[0]].displacements:
#             displacement = self.structure.displacements[key]
#             # components = displacement.components
#             nodes = self.structure.sets[displacement.nodes]['selection']
#             for node in nodes:
#                 bcs_pts.InsertNextPoint(self.structure.node_xyz(node))

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
