
from compas_fea.cad import blender
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoads
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure

from compas_blender.utilities import get_objects


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='mesh_mould', path='/home/al/temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, layers=[0, 1], mesh_type='ShellElement')

# Sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_wall')
blender.add_elset_from_bmeshes(mdl, layer=1, name='elset_plinth')
blender.add_nset_from_bmeshes(mdl, layer=3, name='nset_fixed')

# Materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=40),
    Steel(name='mat_rebar', fy=500, id='r')])

# Sections

mdl.add_sections([
    ShellSection(name='sec_wall', t=0.150),
    ShellSection(name='sec_plinth', t=0.300)])

# Properties

reb_plinth = {
    'p_u1': {'pos': +0.130, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 0},
    'p_u2': {'pos': +0.120, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 90},
    'p_l2': {'pos': -0.120, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 90},
    'p_l1': {'pos': -0.130, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 0}}

reb_wall = {
    'w_u1': {'pos': +0.055, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 0},
    'w_u2': {'pos': +0.045, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 90},
    'w_l2': {'pos': -0.045, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 90},
    'w_l1': {'pos': -0.055, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010, 'angle': 0}}

mdl.add_element_properties([
    Properties(name='ep_plinth', material='mat_concrete', section='sec_plinth', 
               elsets='elset_plinth', reinforcement=reb_plinth),
    Properties(name='ep_wall', material='mat_concrete', section='sec_wall',
               elsets='elset_wall', reinforcement=reb_wall)])
               
# Displacements

mdl.add_displacement(FixedDisplacement(name='disp_fixed', nodes='nset_fixed'))

# Loads

mdl.add_load(GravityLoad(name='load_gravity', elements=['elset_wall', 'elset_plinth']))
components = {}
for object in get_objects(layer=2):
    px, py, pz, _ = object.name.split(' ')
    components[mdl.check_node_exists(list(object.location))] = {'z': float(pz)*100}
mdl.add_load(PointLoads(name='load_points', components=components))
loads = ['load_gravity', 'load_points']

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', nlgeom=False, displacements=['disp_fixed']),
    GeneralStep(name='step_loads', nlgeom=False, loads=loads)])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u', 's', 'rbfor'], license='research')

blender.plot_data(mdl, step='step_loads', field='um', layer=4, colorbar_size=0.3)
blender.plot_data(mdl, step='step_loads', field='smaxp', layer=5, colorbar_size=0.3)
blender.plot_data(mdl, step='step_loads', field='sminp', layer=6, colorbar_size=0.3)
blender.plot_data(mdl, step='step_loads', field='rbfor', iptype='max', nodal='max', layer=7, colorbar_size=0.3)
