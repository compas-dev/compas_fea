
from compas_fea.cad import rhino
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from math import pi


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


# Structure

mdl = Structure(name='beam_simple', path='C:/Temp/')

# Elements

network = rhino.network_from_lines(layer='elset_lines')
mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement',
                                    elset='elset_lines', axes={'ex': [0, -1, 0]})

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_left', 'nset_right', 'nset_weights'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Sections

_, ekeys, L, Lt = rhino.ordered_network(mdl, network=network, layer='nset_left')

for i, Li in zip(ekeys, L):
    ri = (1 + Li / Lt) * 0.020
    sname = 'sec_{0}'.format(i)
    mdl.add(CircularSection(name=sname, r=ri))
    mdl.add(Properties(name='ep_{0}'.format(i), material='mat_elastic', section=sname, elements=[i]))

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_left', nodes='nset_left'),
    GeneralDisplacement(name='disp_right', nodes='nset_right', y=0, z=0, xx=0),
    GeneralDisplacement(name='disp_rotate', nodes='nset_left', yy=30*pi/180),
])

# Loads

mdl.add(PointLoad(name='load_weights', nodes='nset_weights', z=-100))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads='load_weights', displacements='disp_rotate'),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='ansys', fields=['u', 'rf', 's'])

rhino.plot_data(mdl, step='step_load', field='um', radius=0.01, cbar_size=0.3)
rhino.plot_reaction_forces(mdl, step='step_load', layer=None, scale=.1)
#rhino.plot_data(mdl, step='step_load', field='s', radius=0.01, cbar_size=0.3)
#rhino.plot_data(mdl, step='step_load', field='sf2', radius=0.01, cbar_size=0.3)
#rhino.plot_data(mdl, step='step_load', field='sm1', radius=0.01, cbar_size=0.3)