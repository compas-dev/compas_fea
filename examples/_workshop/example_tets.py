
from compas_fea.cad import rhino
from compas_fea.structure import Structure
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import SolidSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import GeneralStep

import rhinoscriptsyntax as rs


# Author(s): Andrew Liew (github.com/andrewliew)


mdl = Structure(name='example_tets', path='C:/Temp/')

# Triangles

guid = rs.ObjectsByLayer('mesh_triangle')[0]
rhino.discretise_mesh(mesh=guid, layer='mesh_discretised', target=0.300, min_angle=15)

# Weld

rhino.weld_meshes_from_layer(layer_input='mesh_discretised', layer_output='mesh_tetgen')

# Tetrahedrons

mesh = rs.ObjectsByLayer('mesh_tetgen')[0]
rhino.add_tets_from_mesh(mdl, name='mesh_tets', mesh=mesh, volume=0.10, draw_tets=None)

# Analyse

zmin, zmax = mdl.node_bounds()[2]
nodes_top = [i for i, node in mdl.nodes.items() if node.z > zmax - 0.010]
nodes_bot = [i for i, node in mdl.nodes.items() if node.z < zmin + 0.010]
mdl.add_set(name='nset_top', type='node', selection=nodes_top)
mdl.add_set(name='nset_bot', type='node', selection=nodes_bot)

mdl.add([
    ElasticIsotropic(name='mat_elastic', E=50*10**9, v=0.3, p=1),
    SolidSection(name='sec_solid'),
    ElementProperties(name='ep_tets', material='mat_elastic', section='sec_solid', elset='mesh_tets'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_bot'),
    PointLoad(name='load_top', nodes='nset_top', y=10000, z=10000),
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_top']),
])
mdl.steps_order = ['step_bc', 'step_load']

mdl.summary()

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

rhino.plot_data(mdl, step='step_load', field='um')
rhino.plot_data(mdl, step='step_load', field='smises')
#rhino.plot_voxels(mdl, step='step_load', field='um', vdx=0.100)

mdl.save_to_obj()
