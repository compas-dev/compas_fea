"""An example compas_fea package for block elements."""

from compas_fea.cad import blender

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

from compas_blender.utilities import draw_plane
from compas_blender.utilities import clear_layer


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


clear_layer(layer=0)

# Create empty Structure object

mdl = Structure(name='block_deepbeam', path='/home/al/Temp/')

# Extrude mesh

ds = 0.05
bmesh = bmesh=draw_plane(Lx=1.0, Ly=2.0, dx=ds, dy=ds)
blender.mesh_extrude(mdl, bmesh, nz=int(1/ds), dz=ds, setname='elset_solids')

# Add node and element sets

pins = [[ds, ds, 0], [1 - ds, ds, 0], [1 - ds, 2 - ds, 0], [ds, 2 - ds, 0]]
supports = [mdl.check_node_exists(i) for i in pins]
top = [mdl.check_node_exists([0.5, 1.0, 1.0])]
mdl.add_set(name='nset_supports', type='node', selection=supports)
mdl.add_set(name='nset_load', type='node', selection=top)

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**10, v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = Properties(material='mat_elastic', section='sec_solid', elsets='elset_solids')
mdl.add_element_properties(ep, name='ep_solid')

# Add loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Add steps

mdl.add_step(GeneralStep(name='step', displacements=['disp_pinned'], loads=['load_point']))
mdl.steps_order = ['step']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot voxels

blender.plot_voxels(mdl, step='step', field='smises', vdx=ds, cbar=[0, 1.5], cube_size=[10, 20, 10], layer=1)
