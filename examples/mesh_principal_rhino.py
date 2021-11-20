from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure

# Author(s): Andrew Liew (github.com/andrewliew),
#            Francesco Ranaudo (github.com/franaudo)


folder = 'C:/temp/'
name = 'principal_stresses_rhino'

# Structure

mdl = Structure(name=name, path=folder)

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')

# Sets

rhino.add_sets_from_layers(mdl, layers='nset_pins')

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10**12, v=0.3, p=1000))

# Sections

mdl.add(ShellSection(name='sec_plate', t=1))

# Properties

mdl.add(Properties(name='ep_plate', material='mat_elastic', section='sec_plate', elset='elset_mesh'))

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Loads

mdl.add(GravityLoad(name='load_gravity', elements='elset_mesh'))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_gravity']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], save=False)

# Plot
rhino.plot_principal_stresses(mdl, step='step_load', sp='sp1', stype='max', scale=10**6)
rhino.plot_principal_stresses(mdl, step='step_load', sp='sp1', stype='min', scale=10**6)
