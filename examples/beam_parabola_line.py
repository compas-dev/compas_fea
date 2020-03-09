
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RectangularSection
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='beam_frame', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_lines')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_left', 'nset_right'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=210*10**9, v=0.3, p=7500))

# Sections

mdl.add(RectangularSection(name='sec_beam', b=1, h=1))

# Properties

mdl.add(Properties(name='ep_beam', material='mat_elastic', section='sec_beam', elset='elset_lines'))

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_left', nodes='nset_left'),
    PinnedDisplacement(name='disp_right', nodes='nset_right'),
])

# Loads

mdl.add(GravityLoad(name='load_gravity', elements='elset_lines'))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads='load_gravity'),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 'sf', 'sm', 'rf'])

rhino.plot_data(mdl, step='step_load', field='sf1', radius=0.5, cbar_size=10)
rhino.plot_data(mdl, step='step_load', field='sf3', radius=0.5, cbar_size=10)
rhino.plot_data(mdl, step='step_load', field='sm2', radius=0.5, cbar_size=10)
rhino.plot_reaction_forces(mdl, step='step_load', scale=0.02)
