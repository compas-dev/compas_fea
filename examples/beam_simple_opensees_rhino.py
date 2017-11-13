"""An example compas_fea package use for beam elements."""

from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import LineLoad
from compas_fea.structure import Structure


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='beam_simple', path='/home/al/Temp/')

# Add nodes

mdl.add_nodes(nodes=[[0, 0, 0.], [0, 1, 0], [1, 1, 0], [1, 0, 0]])

# Add elements

mdl.add_elements(elements=[[0, 1], [1, 2], [2, 3]], type='BeamElement', axes={'ex': [0, 0, 1]})

# Add sets

mdl.add_set(name='nset_pins', type='node', selection=[0, 3])
mdl.add_set(name='nset_1_2', type='node', selection=[1, 2])
mdl.add_set(name='elset_beams', type='element', selection=[0, 1, 2])
mdl.add_set(name='elset_1', type='element', selection=[1])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=200*10**9, v=0.3, p=7850))

# Add sections

mdl.add_section(CircularSection(name='sec_circular', r=0.050))

# Add element properties

ep = Properties(material='mat_elastic', section='sec_circular', elsets='elset_beams')
mdl.add_element_properties(ep, name='ep')

# Add displacements

mdl.add_displacement(GeneralDisplacement(name='disp_pins', nodes='nset_pins', x=0, y=0, z=0))
mdl.add_displacement(GeneralDisplacement(name='disp_rollers', nodes='nset_1_2', z=0))

# Add loads

mdl.add_load(PointLoad(name='load_x', nodes='nset_1_2', x=70))
mdl.add_load(LineLoad(name='load_y', elements='elset_1', y=0, axes='local'))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_x', 'load_y'], iterations=50)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Generate input files

mdl.write_input_file(software='opensees', fields=['u'])
