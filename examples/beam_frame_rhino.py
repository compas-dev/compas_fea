
from compas_fea.cad import rhino
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
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


# Structure

mdl = Structure(name='beam_frame', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_beams')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_pins', 'nset_load_v', 'nset_load_h', 'nset_rollers'])

# Materials

mdl.add_material(Steel(name='mat_steel'))

# Sections

mdl.add_section(PipeSection(name='sec_pipe', r=0.100, t=0.005))

# Properties

ep = Properties(name='ep_beams', material='mat_steel', section='sec_pipe', elsets='elset_beams')
mdl.add_element_properties(ep)

# Displacements

mdl.add_displacements([
    PinnedDisplacement(name='disp_pins', nodes='nset_pins'),
    RollerDisplacementXZ(name='disp_rollers', nodes='nset_rollers')])

# Loads

mdl.add_loads([
    PointLoad(name='load_h', nodes='nset_load_h', x=+4000),
    PointLoad(name='load_v', nodes='nset_load_v', z=-6000)])

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_h', 'load_v'], iterations=50)])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run (Sofistik)

mdl.write_input_file(software='sofistik')

# Run (Abaqus/OpenSees)

mdl.analyse_and_extract(software='abaqus', fields=['u', 'rf'], license='research')
mdl.analyse_and_extract(software='opensees', fields=['u', 'rf'])

rhino.plot_data(mdl, step='step_loads', field='um', scale=50)

print(mdl.get_nodal_results(step='step_loads', field='rfm', nodes='nset_pins'))
