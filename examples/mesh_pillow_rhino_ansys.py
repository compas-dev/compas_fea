
from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


# Structure

mdl = Structure(name='meshpillow_from_rhino', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers=['mesh'])

# Sets

rhino.add_sets_from_layers(mdl, layers=['supports', 'lpts1', 'lpts2'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Sections

mdl.add(ShellSection(name='sec_shell', t=0.050))

# Properties

mdl.add(Properties(name='ep_shell', material='mat_elastic', section='sec_shell', elset='mesh'))

# Displacements

mdl.add(PinnedDisplacement(name='disp_pin', nodes='supports'))

# Loads

mdl.add(GravityLoad(name='gravity', elements='all'))
mdl.add(PointLoad(name='load_points', nodes='lpts1', x=0, y=0, z=-1000))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pin']),
    GeneralStep(name='step_load', loads=['gravity', 'load_points']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='ansys',
                        fields=['u', 's', 'sp', 'e', 'ss', 'rf'],
                        license='introductory')


rhino.plot_data(mdl, step='step_load', field='um', scale=1e4)
rhino.plot_data(mdl, step='step_load', field='szt')
rhino.plot_data(mdl, step='step_load', field='ps1t')
rhino.plot_data(mdl, step='step_load', field='sxzt')
rhino.plot_data(mdl, step='step_load', field='e1t')
rhino.plot_reaction_forces(mdl, step='step_load', layer=None, scale=1)
