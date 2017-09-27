"""A compas_fea package example for truss elements."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import blender

from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'truss-tower'
path = '/home/al/Temp/'

# Create empty Structure object

mdl = Structure()

# Add truss elements

blender.add_nodes_elements_from_layers(mdl, edge_type='TrussElement', layers=[0])

# Add node and element sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_struts')
blender.add_nset_from_objects(mdl, layer=1, name='nset_pins')
blender.add_nset_from_objects(mdl, layer=2, name='nset_load')

# Add materials

mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_section(TrussSection(name='sec_truss', A=0.0050))

# Add element properties

ep = ElementProperties(material='mat_steel', section='sec_truss', elsets='elset_struts')
mdl.add_element_properties(ep, name='ep_truss')

# Add loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1000000))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_pinned']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_point']))
mdl.set_steps_order(['step_bc', 'step_load'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

blender.plot_data(mdl, path, name, step='step_load', field='U', component='magnitude', layer=3)

# Plot stress

blender.plot_data(mdl, path, name, step='step_load', field='S', component='mises', iptype='max', layer=4)
