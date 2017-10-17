"""An example compas_fea package use for beams in a tree structure."""

from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElasticPlastic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementZ
from compas_fea.structure import Structure
from compas_fea.structure import TrapezoidalSection


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='beam_tree', path='C:/Temp/')

# Add beam elements

layers = ['struts_mushroom', 'struts_bamboo', 'joints_mushroom', 'joints_bamboo', 'joints_grid']
rhino.add_nodes_elements_from_layers(mdl, element_type='BeamElement', layers=layers)

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['supports_bot', 'supports_top'])
rhino.add_sets_from_layers(mdl, layers=layers, explode=True)

# Add sections

mdl.add_section(TrapezoidalSection(name='sec_mushroom', b1=0.001, b2=0.150, h=0.225))
mdl.add_section(RectangularSection(name='sec_bamboo', b=0.020, h=0.100))
mdl.add_section(RectangularSection(name='sec_joints', b=0.020, h=0.075))

# Add materials

fm = [50000, 90000, 120000, 140000, 160000, 180000, 190000, 200000, 210000, 220000]
em = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
mdl.add_material(ElasticIsotropic(name='mat_bamboo', E=20*10**9, v=0.35, p=1100))
mdl.add_material(ElasticPlastic(name='mat_mushroom', E=5*10**6, v=0.30, p=350, f=fm, e=em))

# Add element properties

s_1 = ['struts_mushroom', 'joints_mushroom']
s_2 = ['struts_bamboo', 'joints_bamboo']
s_3 = ['joints_grid']
epm = ElementProperties(material='mat_mushroom', section='sec_mushroom', elsets=s_1)
epb = ElementProperties(material='mat_bamboo', section='sec_bamboo', elsets=s_2)
epj = ElementProperties(material='mat_bamboo', section='sec_joints', elsets=s_3)
mdl.add_element_properties(epm, name='ep_mushroom')
mdl.add_element_properties(epb, name='ep_bamboo')
mdl.add_element_properties(epj, name='ep_joints')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_bot', nodes='supports_bot'))
mdl.add_displacement(RollerDisplacementZ(name='disp_top', nodes='supports_top'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_bot', 'disp_top']))
mdl.add_step(GeneralStep(name='step_loads', loads=['load_gravity']))
mdl.set_steps_order(['step_bc', 'step_loads'])

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields={'U': 'all', 'SF': 'all'})

# Plot displacements

rhino.plot_data(mdl, step='step_loads', field='U', component='magnitude', radius=0.05)

# Plot section axial forces

rhino.plot_data(mdl, step='step_loads', field='SF', component='SF1', radius=0.05)
