
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import ModalStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import MassSection
from compas_fea.structure import Structure


# Author(s): 
# Francesco Ranaudo (github.com/nefelogeta)
# Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_modal_from_mesh', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_concrete', pA=100)
rhino.add_nodes_elements_from_layers(mdl, mesh_type='MassElement', layers='elset_mass',pA=1000)

# Sets

rhino.add_sets_from_layers(mdl, layers='nset_pins')

# Materials

mdl.add(ElasticIsotropic(name='mat_concrete', E=40*10**9, v=0.2, p=2400))

# Sections

mdl.add([ShellSection(name='sec_concrete', t=0.250),
        MassSection(name='sec_mass')])

# Properties

mdl.add([Properties(name='ep_concrete', material='mat_concrete', section='sec_concrete', elset='elset_concrete'),
        Properties(name='ep_mass', section='sec_mass', elset='elset_mass')])

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    ModalStep(name='step_modal', modes=5),
])
mdl.steps_order = ['step_bc', 'step_modal']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u'])

rhino.plot_mode_shapes(mdl, step='step_modal', layer='mode-')

print(mdl.results['step_modal']['frequencies'])
print(mdl.results['step_modal']['masses'])
