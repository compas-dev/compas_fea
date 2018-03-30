
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_plate', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_load', 'nset_left', 'nset_right'])

# Materials

mdl.add_material(ElasticIsotropic(name='mat_linear', E=75*10**9, v=0.3, p=2700))

# Sections

mdl.add_section(ShellSection(name='sec_plate', t=0.020))

# Properties

ep = Properties(name='ep', material='mat_linear', section='sec_plate', elsets='elset_mesh')
mdl.add_element_properties(ep)

# Displacements

mdl.add_displacements([
    PinnedDisplacement(name='disp_left', nodes='nset_left'),
    RollerDisplacementX(name='disp_right', nodes='nset_right')])

# Loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', y=100, z=-300))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads=['load_point'], tolerance=1, iterations=500)])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Sofistik)

mdl.write_input_file(software='sofistik')

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u'])

# Run (OpenSees)

mdl.analyse_and_extract(software='opensees', fields=['u'])

rhino.plot_data(mdl, step='step_load', field='um')
