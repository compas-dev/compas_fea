
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='mesh_principal', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_pins'])

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**12, v=0.3, p=1000))

# Sections

mdl.add_section(ShellSection(name='sec_plate', t=1))

# Properties

ep = Properties(name='ep_plate', material='mat_elastic', section='sec_plate', elsets='elset_mesh')
mdl.add_element_properties(ep)

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_mesh'))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_gravity'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

rhino.plot_principal_stresses(mdl, step='step_load', ptype='max', scale=3)
rhino.plot_principal_stresses(mdl, step='step_load', ptype='min', scale=3)
