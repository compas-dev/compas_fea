
from compas_fea.cad import blender
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from math import pi
deg = pi / 180


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='beam_simple', path='C:/Temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_beam')

# Sets

blender.add_nsets_from_layers(mdl, layers=['nset_left', 'nset_right', 'nset_weights'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Sections

mdl.add(CircularSection(name='sec_circular', r=0.030))

# Properties

mdl.add(Properties(name='ep_beam', material='mat_elastic', section='sec_circular', elset='elset_beam'))

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_left', nodes='nset_left'),
    GeneralDisplacement(name='disp_right', nodes='nset_right', y=0, z=0, xx=0),
    GeneralDisplacement(name='disp_move', nodes='nset_right', yy=30*deg),
])

# Loads

mdl.add(PointLoad(name='load_weights', nodes='nset_weights', z=-1))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads=['load_weights'], displacements=['disp_move']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 'ur', 'sf', 'sm'])

# blender.plot_data(mdl, step='step_load', field='um', radius=0.01, cbar_size=0.3)
# blender.plot_data(mdl, step='step_load', field='urx', radius=0.01, cbar_size=0.3)
# blender.plot_data(mdl, step='step_load', field='sf1', radius=0.01, cbar_size=0.3)
# blender.plot_data(mdl, step='step_load', field='sm1', radius=0.01, cbar_size=0.3)
