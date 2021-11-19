from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_plate', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_load', 'nset_left', 'nset_right'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=75*10**9, v=0.3, p=2700))

# Sections

mdl.add(ShellSection(name='sec_plate', t=0.020))

# Properties

mdl.add(Properties(name='ep_plate', material='mat_elastic', section='sec_plate', elset='elset_mesh'))

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_left', nodes='nset_left'),
    RollerDisplacementX(name='disp_right', nodes='nset_right'),
])

# Loads

mdl.add(PointLoad(name='load_point', nodes='nset_load', y=100, z=-300))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads=['load_point'], tolerance=1, iterations=500),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='ansys', fields=['u', 's'], license='introductory')

rhino.plot_data(mdl, step='step_load', field='um')

mdl.save_to_obj()
