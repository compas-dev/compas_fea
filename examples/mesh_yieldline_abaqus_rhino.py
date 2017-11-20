"""An example compas_fea package use for meshes."""

from compas_fea.cad import rhino

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import PointLoad
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

rhino.add_sets_from_layers(mdl, layers=['elset_mesh', 'nset_roller_x', 'nset_roller_y', 'nset_loads'])

# Add materials

mdl.add_material(Steel(name='mat_yield', fy=100))

# Add sections

mdl.add_section(ShellSection(name='sec_yield', t=0.010))

# Add element properties

ep = Properties(material='mat_yield', section='sec_yield', elsets='elset_mesh')
mdl.add_element_properties(ep, name='ep_yield')

# Add loads

pz = 110000 / mdl.node_count()
mdl.add_load(PointLoad(name='load_points', nodes='nset_loads', z=-pz))

# Add displacements

mdl.add_displacements([
    GeneralDisplacement(name='disp_x', nodes='nset_roller_x', z=0, y=0),
    GeneralDisplacement(name='disp_y', nodes='nset_roller_y', z=0, x=0)])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', type='STATIC', displacements=['disp_x', 'disp_y']),
    GeneralStep(name='step_loads', nlgeom=0, type='STATIC', loads=['load_points'])])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 'pe'])

# Plot strain

rhino.plot_data(mdl, step='step_loads', field='pemaxp', cbar=[None, 0.0005], scale=0)
