"""An example compas_fea package use for meshes."""

from compas_fea.cad import rhino

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='mesh_yieldline', path='C:/Temp/')

# Add shell elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['elset_mesh', 'nset_roller_x', 'nset_roller_y'])

# Add materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=30),
    Steel(name='mat_steel', fy=500)])

# Add sections

mdl.add_section(ShellSection(name='sec_concrete', t=0.100))

# Add element properties

rebar = {
    'l2': {'pos': -0.035, 'spacing': 0.100, 'material': 'mat_steel', 'dia': 0.010, 'angle': 90},
    'l1': {'pos': -0.040, 'spacing': 0.100, 'material': 'mat_steel', 'dia': 0.010, 'angle': 0}}

ep = Properties(material='mat_concrete', section='sec_concrete', elsets='elset_mesh', reinforcement=rebar)
mdl.add_element_properties(ep, name='ep_concrete')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_mesh'))

# Add displacements

mdl.add_displacements([
    GeneralDisplacement(name='disp_x', nodes='nset_roller_x', z=0, y=0),
    GeneralDisplacement(name='disp_y', nodes='nset_roller_y', z=0, x=0)])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', type='STATIC', displacements=['disp_x', 'disp_y']),
    GeneralStep(name='step_loads', increments=100, type='STATIC,RIKS', loads=['load_gravity'])])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 'e', 'pe', 's', 'rbfor'])

# Plot strain

#rhino.plot_data(mdl, step='step_loads', field='emaxp', cbar=[None, 0.0001], scale=0)
