
from compas_fea.cad import rhino
from compas_fea.structure import Structure
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import GeneralStep
from compas_fea.structure import ModalStep


mdl = Structure(name='example_shell', path='C:/Temp/')

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='mesh')

supports = []
for key, node in mdl.nodes.items():
    if node.z < 0.5:
        supports.append(key)
#print(supports)

mdl.add_set(name='supports', type='node', selection=supports)
#print(mdl.sets['supports'])

mdl.add(ElasticIsotropic(name='material', E=40*10**9, v=0.2, p=2500))

mdl.add(ShellSection(name='section', t=0.100))

mdl.add(ElementProperties(name='ep', material='material', section='section', elset='mesh'))

mdl.add(PinnedDisplacement(name='pinned', nodes='supports'))
    
mdl.add(GravityLoad(name='gravity', elements='mesh'))

mdl.add_steps([
    GeneralStep(name='bc', displacements='pinned'),
    GeneralStep(name='loads', loads='gravity', factor=2.0),
    ModalStep(name='modal', modes=5),
])
mdl.steps_order = ['bc', 'loads']

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'rf'])

rhino.plot_data(mdl, step='loads', field='um', scale=100)
rhino.plot_data(mdl, step='loads', field='smaxp')
rhino.plot_data(mdl, step='loads', field='sminp')
rhino.plot_reaction_forces(mdl, step='loads', scale=0.1)
rhino.plot_mode_shapes(mdl, step='modal', layer='mode-')
#rhino.plot_principal_stresses(mdl, step='loads', ptype='max', scale=3)
#rhino.plot_principal_stresses(mdl, step='loads', ptype='min', scale=3)
