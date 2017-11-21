"""An example compas_fea package use for meshes."""

from compas_blender.helpers import mesh_from_bmesh
from compas_blender.utilities import get_objects

from compas_fea.cad import blender

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='mesh_floor', path='/home/al/Temp/')

# Add truss and shell elements

blender.add_nodes_elements_from_layers(mdl, layers=0, mesh_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers=1, line_type='TrussElement')

## Add node and element sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_concrete')
blender.add_elset_from_bmeshes(mdl, layer=1, name='elset_ties')
blender.add_nset_from_objects(mdl, layer=3, name='nset_corners')
blender.add_nset_from_objects(mdl, layer=4, name='nset_corner1')
blender.add_nset_from_objects(mdl, layer=5, name='nset_corner2')

# Add materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355)])

# Add sections

mdl.add_sections([
    ShellSection(name='sec_concrete', t=0.020),
    TrussSection(name='sec_ties', A=0.0004)])

# Add element properties

epc = Properties(material='mat_concrete', section='sec_concrete', elsets='elset_concrete')
eps = Properties(material='mat_steel', section='sec_ties', elsets='elset_ties')
mdl.add_element_properties(epc, name='ep_concrete')
mdl.add_element_properties(eps, name='ep_steel')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_concrete'))

# Add tributary loads from mesh

mesh = mesh_from_bmesh(get_objects(layer=2)[0])
mdl.add_load(TributaryLoad(mdl, name='load_tributary', mesh=mesh, z=-2000))

# Add displacements

mdl.add_displacements([
    RollerDisplacementXY(name='disp_roller', nodes='nset_corners'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'),
    GeneralDisplacement(name='disp_dofx', nodes='nset_corner2', x=0)])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_roller', 'disp_pinned', 'disp_dofx']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_tributary'], factor=1.5)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot displacements

blender.plot_data(mdl, step='step_loads', field='um', radius=0.02, layer=6)

# Plot stress

blender.plot_data(mdl, step='step_loads', field='smises', radius=0.02, cbar=[0, 3*10**6], layer=7)
