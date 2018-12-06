
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

mdl.add(Steel(name='mat_steel'))

# Sections

mdl.add(PipeSection(name='sec_pipe', r=0.100, t=0.005))

# Properties

mdl.add(Properties(name='ep_beam', material='mat_steel', section='sec_pipe', elset='elset_beams'))

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_pins', nodes='nset_pins'),
    RollerDisplacementXZ(name='disp_rollers', nodes='nset_rollers'),
])

# Loads

mdl.add([
    PointLoad(name='load_h', nodes='nset_load_h', x=+4000),
    PointLoad(name='load_v', nodes='nset_load_v', z=-6000),
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_h', 'load_v'], iterations=50),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 'rf', 'sf', 'sm'])

rhino.plot_data(mdl, step='step_loads', field='um', scale=50)
rhino.plot_data(mdl, step='step_loads', field='sf1', iptype='abs', nodal='max')
rhino.plot_data(mdl, step='step_loads', field='sf2', iptype='abs', nodal='max')
rhino.plot_data(mdl, step='step_loads', field='sm1', iptype='abs', nodal='max')
rhino.plot_reaction_forces(mdl, step='step_loads', scale=0.5)
