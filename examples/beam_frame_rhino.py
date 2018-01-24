"""An example compas_fea package use for beam elements."""

from compas_fea.cad import rhino

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import LineLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PipeSection
from compas_fea.structure import PointLoad
from compas_fea.structure import RollerDisplacementXZ
from compas_fea.structure import Steel
from compas_fea.structure import Structure


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='beam_frame', path='C:/Temp/')

# Add nodes and elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_lines')

# Add sets

layers = ['nset_supports', 'nset_load_v', 'nset_load_h', 'nset_corners', 'elset_top', 'elset_lines']
rhino.add_sets_from_layers(mdl, layers=layers)

# Add materials

mdl.add_material(Steel(name='mat_steel'))

# Add sections

mdl.add_section(PipeSection(name='sec_pipe', r=0.100, t=0.005))

# Add element properties

ep = Properties(name='ep', material='mat_steel', section='sec_pipe', elsets='elset_lines')
mdl.add_element_properties(ep)

# Add displacements

mdl.add_displacements([
    PinnedDisplacement(name='disp_pins', nodes='nset_supports'),
    RollerDisplacementXZ(name='disp_rollers', nodes='nset_corners')])

# Add loads

mdl.add_loads([
    PointLoad(name='load_h', nodes='nset_load_h', x=4000),
    PointLoad(name='load_v', nodes='nset_load_v', z=-6000),
    LineLoad(name='load_udl', elements='elset_top', y=4000)])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_h', 'load_v', 'load_udl'], iterations=50)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

#mdl.analyse_and_extract(software='abaqus', fields=['u', 'ur', 'rf'])
mdl.analyse_and_extract(software='opensees', fields=['u', 'ur', 'rf'])

# Plot deformations

rhino.plot_data(mdl, step='step_loads', field='um', scale=50)
rhino.plot_data(mdl, step='step_loads', field='urm', scale=50)

# Extract data

print(mdl.get_nodal_results(step='step_loads', field='rfx', nodes='nset_supports'))
print(mdl.get_nodal_results(step='step_loads', field='rfz', nodes='nset_supports'))
