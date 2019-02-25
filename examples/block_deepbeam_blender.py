
from compas_fea.cad import blender
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

from compas_blender.utilities import get_object_by_name


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='block_deepbeam', path='C:/Temp/')

# Mesh

ds = 0.05
Lx = 1
Ly = 2
Lz = 1

mesh = get_object_by_name(name='plane')
blender.mesh_extrude(mdl, mesh=mesh, layers=int(Lz / ds), thickness=ds, blocks_name='elset_blocks')

# Sets

pins = [[ds, ds, 0], [Lx - ds, ds, 0], [Lx - ds, Ly - ds, 0], [ds, Ly - ds, 0]]
mdl.add_set(name='nset_supports', type='node', selection=[mdl.check_node_exists(i) for i in pins])
mdl.add_set(name='nset_load', type='node', selection=[mdl.check_node_exists([Lx * 0.5, Ly * 0.5, Lz])])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10**10, v=0.3, p=1))

# Sections

mdl.add(SolidSection(name='sec_solid'))

# Properties

mdl.add(Properties(name='ep_solid', material='mat_elastic', section='sec_solid', elset='elset_blocks'))

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Loads

mdl.add(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_point']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], components=['ux', 'uy', 'uz', 'smises'])

mdl.save_to_obj()

# Plot

# blender.plot_data(mdl, step='step_load', field='smises', cbar=[0, 2])
# blender.plot_voxels(mdl, step='step_load', field='smises', vdx=ds, cbar=[0, 1.5])
