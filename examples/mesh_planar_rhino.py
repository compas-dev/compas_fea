
from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoads
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PrestressLoad
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import TrussSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_planar', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers=['Mesh', 'Plates'])
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers=['Tie'])

# Sets

rhino.add_sets_from_layers(mdl, layers=['Pin', 'Roller'])

# Materials

mdl.add_material(Concrete(name='mat_concrete', fck=50))
mdl.add_material(Steel(name='mat_steel', fy=460))

# Sections

mdl.add_section(ShellSection(name='sec_planar', t=0.050))
mdl.add_section(TrussSection(name='sec_tie', A=0.0001))

# Properties

mdl.add_element_properties([
    Properties(name='ep_planar', material='mat_concrete', section='sec_planar', elsets='Mesh'),
    Properties(name='ep_plate', material='mat_steel', section='sec_planar', elsets='Plates'),
    Properties(name='ep_tie', material='mat_steel', section='sec_tie', elsets='Tie')])

# Displacements

mdl.add_displacements([
    PinnedDisplacement(name='disp_pin', nodes='Pin'),
    RollerDisplacementX(name='disp_roller', nodes='Roller')])

# Loads

loads = {}
for i in rs.ObjectsByLayer('Loads'):
    loads[mdl.check_node_exists(rs.PointCoordinates(i))] = {'y': float(rs.ObjectName(i))}
mdl.add_loads([
    PointLoads(name='load_points', components=loads),
    PrestressLoad(name='load_prestress', elements='Tie', sxx=50*10**6)])

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pin', 'disp_roller']),
    GeneralStep(name='step_prestress', loads=['load_prestress']),
    GeneralStep(name='step_load', loads=['load_points'])])
mdl.steps_order = ['step_bc', 'step_prestress', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 'cf', 's', 'rf'])

rhino.plot_data(mdl, step='step_load', field='um', radius=0.01)
rhino.plot_data(mdl, step='step_prestress', field='smaxp', iptype='max', nodal='max', cbar=[0, 1*10**6], radius=0.01)
rhino.plot_data(mdl, step='step_prestress', field='sminp', iptype='min', nodal='min', cbar=[-3*10**6, 0], radius=0.01)
rhino.plot_data(mdl, step='step_load', field='smaxp', iptype='max', nodal='max', cbar=[0, 2*10**6], radius=0.01)
rhino.plot_data(mdl, step='step_load', field='sminp', iptype='min', nodal='min', cbar=[-4*10**6, 0], radius=0.01)
rhino.plot_data(mdl, step='step_load', field='smises', iptype='max', nodal='max', cbar=[0, 3*10**6], radius=0.01)

rhino.plot_principal_stresses(mdl, step='step_load', ptype='max', scale=1)
rhino.plot_principal_stresses(mdl, step='step_load', ptype='min', scale=1, rotate=1)
