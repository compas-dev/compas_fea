
from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoads
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_planar', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='Mesh')

# Sets

rhino.add_sets_from_layers(mdl, layers=['Pins'])

# Materials

mdl.add_material(Concrete(name='mat_concrete', fck=50))

# Sections

mdl.add_section(ShellSection(name='sec_plate', t=0.050))

# Properties

ep = Properties(name='ep_plate', material='mat_concrete', section='sec_plate', elsets='Mesh')
mdl.add_element_properties(ep)

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='Pins'))

# Loads

loads = {}
for i in rs.ObjectsByLayer('Loads'):
    loads[mdl.check_node_exists(rs.PointCoordinates(i))] = {'y': float(rs.ObjectName(i))}
mdl.add_load(PointLoads(name='load_points', components=loads))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_points'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 'cf', 's', 'rf'])

rhino.plot_data(mdl, step='step_load', field='um')
rhino.plot_data(mdl, step='step_load', field='smises', iptype='max', nodal='max')
rhino.plot_data(mdl, step='step_load', field='smaxp', iptype='max', nodal='max')
rhino.plot_data(mdl, step='step_load', field='sminp', iptype='min', nodal='min')
rhino.plot_principal_stresses(mdl, step='step_load', ptype='max', scale=3)
rhino.plot_principal_stresses(mdl, step='step_load', ptype='min', scale=2, rotate=1)
