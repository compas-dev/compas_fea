
from compas_blender.helpers import mesh_from_bmesh
from compas_blender.utilities import get_objects

from compas_fea.cad import blender
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PrestressLoad
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='mesh_floor', path='/home/al/temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, layers=0, mesh_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers=1, line_type='TrussElement')

# Sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_concrete')
blender.add_elset_from_bmeshes(mdl, layer=1, name='elset_ties')
blender.add_nset_from_objects(mdl, layer=3, name='nset_corners')
blender.add_nset_from_objects(mdl, layer=4, name='nset_corner1')
blender.add_nset_from_objects(mdl, layer=5, name='nset_corner2')

# Materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355)])

# Sections

mdl.add_sections([
    ShellSection(name='sec_concrete', t=0.020),
    TrussSection(name='sec_ties', A=0.0004)])

# Properties

mdl.add_element_properties([
    Properties(name='ep_concrete', material='mat_concrete', section='sec_concrete', elsets='elset_concrete'),
    Properties(name='ep_steel', material='mat_steel', section='sec_ties', elsets='elset_ties')])

# Displacements

mdl.add_displacements([
    RollerDisplacementXY(name='disp_roller', nodes='nset_corners'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'),
    GeneralDisplacement(name='disp_xdof', nodes='nset_corner2', x=0)])
    
# Loads

mesh = mesh_from_bmesh(get_objects(layer=2)[0])
mdl.add_loads([
    GravityLoad(name='load_gravity', elements='elset_concrete'),
    PrestressLoad(name='load_prestress', elements='elset_ties', sxx=50*10**6),
    TributaryLoad(mdl, name='load_tributary', mesh=mesh, z=-5000)])

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_roller', 'disp_pinned', 'disp_xdof']),
    GeneralStep(name='step_prestress', loads=['load_prestress']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_tributary'], factor=1.1)])
mdl.steps_order = ['step_bc', 'step_prestress', 'step_loads']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u', 's'], license='research')

blender.plot_data(mdl, step='step_prestress', field='uz', radius=0.02, layer=6, colorbar_size=0.5)
blender.plot_data(mdl, step='step_loads', field='uz', radius=0.02, layer=7, colorbar_size=0.5)
blender.plot_data(mdl, step='step_loads', field='smises', radius=0.02, layer=8, colorbar_size=0.5,
                  iptype='max', nodal='max', cbar=[0, 1*10**6])
