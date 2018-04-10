
from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoads
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_mould', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers=['elset_wall', 'elset_plinth'])

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_fixed'])

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
for guid in rs.ObjectsByLayer('nset_loads'):
    px, py, pz = rs.ObjectName(guid).split(' ')
    components[mdl.check_node_exists(rs.PointCoordinates(guid))] = {'z': float(pz)*100}
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

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'rbfor'])

rhino.plot_data(mdl, step='step_loads', field='um', colorbar_size=0.3)
rhino.plot_data(mdl, step='step_loads', field='smaxp', colorbar_size=0.3)
rhino.plot_data(mdl, step='step_loads', field='sminp', colorbar_size=0.3)
rhino.plot_data(mdl, step='step_loads', field='rbfor', iptype='max', nodal='max', colorbar_size=0.3)

# Run (Sofistik)

mdl.write_input_file(software='sofistik')
