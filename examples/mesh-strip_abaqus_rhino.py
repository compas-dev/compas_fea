"""An example compas_fea package use for meshes."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'mesh-strip'
path = 'C:/Temp/'

# Create empty Structure object

mdl = Structure()

# Add shell elements

rhino.add_nodes_elements_from_layers(mdl, element_type='ShellElement', layers='elset_mesh')

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['nset_left'])
rhino.add_sets_from_layers(mdl, layers=['nset_right'])
rhino.add_sets_from_layers(mdl, layers=['nset_middle'])
rhino.add_sets_from_layers(mdl, layers=['elset_mesh'])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_alu_linear', E=75*10**9, v=0.3, p=2700))

# Add sections

mdl.add_section(ShellSection(name='sec_plate', t=0.003))

# Add element properties

ep = ElementProperties(material='mat_alu_linear', section='sec_plate', elsets='elset_mesh')
mdl.add_element_properties(ep, name='ep_plate')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_mesh'))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_left', nodes='nset_left'))
mdl.add_displacement(RollerDisplacementX(name='disp_right', nodes='nset_right'))
mdl.add_displacement(GeneralDisplacement(name='disp_middle', nodes='nset_middle', z=0.2))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_gravity']))
mdl.add_step(GeneralStep(name='step_lift', displacements=['disp_middle']))
mdl.set_steps_order(['step_bc', 'step_load', 'step_lift'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

rhino.plot_data(mdl, path, name, step='step_lift', field='U', component='magnitude')

# Plot stress

rhino.plot_data(mdl, path, name, step='step_lift', field='S', component='mises')
