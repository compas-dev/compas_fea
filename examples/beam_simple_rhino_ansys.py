
from compas_fea.cad import rhino
from compas_fea.structure import GeneralStep
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import GravityLoad
from compas_fea.structure import Structure


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
    FixedDisplacement(name='disp_left', nodes='nset_left'),
    PinnedDisplacement(name='disp_right', nodes='nset_right'),
])

# Loads

mdl.add(GravityLoad(name='gravity', elements='all'))
mdl.add(PointLoad(name='load_weights', nodes='nset_weights', z=-1000))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']),
    GeneralStep(name='step_load', loads=['load_weights', 'gravity']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='ansys',
                        fields=['u', 's', 'sp', 'e', 'ss', 'rf'],
                        license='introductory')

rhino.plot_data(mdl, step='step_load', field='um', scale=1e2)
rhino.plot_data(mdl, step='step_load', field='szt')
rhino.plot_data(mdl, step='step_load', field='ps1t')
rhino.plot_data(mdl, step='step_load', field='sxzt')
rhino.plot_data(mdl, step='step_load', field='e1t')
rhino.plot_reaction_forces(mdl, step='step_load', layer=None, scale=1)