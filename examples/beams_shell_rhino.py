from compas_fea.cad import rhino
from compas_fea.structure import RectangularSection
from compas_fea.structure import ShellSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='beam_shell_rhino', path='C:/Temp/')

# Elements
layers = ['beams', 'shell']
rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', mesh_type='ShellElement', layers=layers)

# Sets

rhino.add_sets_from_layers(mdl, layers=['supports'])

# Materials

mdl.add(ElasticIsotropic(name='mat_1', E=20*10**9, v=0.3, p=1500))
mdl.add(ElasticIsotropic(name='mat_2', E=30*10**9, v=0.3, p=1500))

# Sections

mdl.add(RectangularSection(name='bsec', b=0.1, h=.2))
mdl.add(Properties(name='ep_1', material='mat_1', section='bsec', elsets=['beams']))

mdl.add(ShellSection(name='ssec', t=.1))
mdl.add(Properties(name='ep_2', material='mat_2', section='ssec', elsets=['shell']))

# Displacements

mdl.add([FixedDisplacement(name='supports', nodes='supports')])

# Loads

mdl.add(GravityLoad(name='load_gravity', elements=['beams', 'shell']))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['supports']),
    GeneralStep(name='step_load', loads=['load_gravity']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.analyse_and_extract(software='ansys', fields=['s'])

# rhino.plot_data(mdl, step='step_load', field='um', radius=0.1, colorbar_size=0.3)
