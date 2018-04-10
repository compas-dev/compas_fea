
from compas_fea.cad import blender

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

from compas_blender.utilities import clear_layer
from compas_blender.utilities import draw_plane


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


clear_layer(layer=0)

# Create empty Structure object

mdl = Structure(name='block_deepbeam', path='C:/Temp/')

# Extrude mesh

ds = 0.05
Lx = 1
Ly = 2
bmesh = bmesh=draw_plane(Lx=Lx, Ly=Ly, dx=ds, dy=ds)
blender.mesh_extrude(mdl, bmesh=bmesh, nz=int(1/ds), dz=ds, setname='elset_blocks')

# Add node and element sets

pins = [[ds, ds, 0], [Lx - ds, ds, 0], [Lx - ds, Ly - ds, 0], [ds, Ly - ds, 0]]
supports = [mdl.check_node_exists(i) for i in pins]
top = [mdl.check_node_exists([0.5, 1.0, 1.0])]
mdl.add_set(name='nset_supports', type='node', selection=supports)
mdl.add_set(name='nset_load', type='node', selection=top)

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**10, v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = Properties(name='ep_solid', material='mat_elastic', section='sec_solid', elsets='elset_blocks')
mdl.add_element_properties(ep)

# Add loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_pinned']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_point']))
mdl.steps_order = ['step_bc', 'step_load']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot voxels

blender.plot_voxels(mdl, step='step_load', field='smises', vdx=ds, cbar=[0, 1.5], cube_size=[10, 20, 10], layer=1)
