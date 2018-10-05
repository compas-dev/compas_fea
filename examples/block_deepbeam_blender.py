
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

# Structure

mdl = Structure(name='block_deepbeam', path='/home/al/temp/')

# Mesh

ds = 0.05
Lx = 1
Ly = 2
Lz = 1
bmesh = bmesh=draw_plane(Lx=Lx, Ly=Ly, dx=ds, dy=ds)
blender.mesh_extrude(mdl, bmesh=bmesh, layers=int(Lz/ds), thickness=ds, blocks_name='elset_blocks')

# Sets

pins = [[ds, ds, 0], [Lx - ds, ds, 0], [Lx - ds, Ly - ds, 0], [ds, Ly - ds, 0]]
supports = [mdl.check_node_exists(i) for i in pins]
top = [mdl.check_node_exists([Lx * 0.5, Ly * 0.5, Lz])]
mdl.add_set(name='nset_supports', type='node', selection=supports)
mdl.add_set(name='nset_load', type='node', selection=top)

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**10, v=0.3, p=1))

# Sections

mdl.add_section(SolidSection(name='sec_solid'))

# Properties

mdl.add_element_properties(
    Properties(name='ep_solid', material='mat_elastic', section='sec_solid', elsets='elset_blocks'))

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_pinned']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_point']))
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u', 's'], license='research')

# Plot (VtkVoxels)

blender.plot_voxels(mdl, step='step_load', field='smises', vdx=ds, cbar=[0, 1.5], plot='vtk')
