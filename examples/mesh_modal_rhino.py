
from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import ModalStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_modal', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_concrete')

# Sets

rhino.add_sets_from_layers(mdl, layers='nset_pins')

# Materials

mdl.add_material(Concrete(name='mat_concrete', fck=40))

# Sections

mdl.add_section(ShellSection(name='sec_concrete', t=0.250))

# Properties

mdl.add_element_properties(
    Properties(name='ep_concrete', material='mat_concrete', section='sec_concrete', elsets='elset_concrete'))

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    ModalStep(name='step_modal', modes=5)])
mdl.steps_order = ['step_bc', 'step_modal']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u'])

rhino.plot_mode_shapes(mdl, step='step_modal', layer='mode-')

print(mdl.results['step_modal']['frequencies'])
print(mdl.results['step_modal']['masses'])
