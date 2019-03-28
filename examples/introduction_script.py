
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Create empty Structure object

mdl = Structure(name='introduction', path='/home/al/temp/')

# Add nodes

mdl.add_node(xyz=[-5., -5., 0.])
mdl.add_nodes(nodes=[[5., -5., 0.], [5., 5., 0.], [-5., 5., 0.], [0., 0., 5.]])

# print('Node number 3:', mdl.nodes[3])
# print('Node number 3 xyz:', mdl.node_xyz(3))
# print('Node count: ', mdl.node_count())
# print('Node index: ', mdl.node_index)
# print('Check node at [0, 0, 0]: ', mdl.check_node_exists([0, 0, 0]))
# print('Check node at [5, 5, 0]: ', mdl.check_node_exists([5, 5, 0]))
# print('Node bounds: ', mdl.node_bounds())

# Add elements

mdl.add_elements(elements=[[0, 4], [1, 4], [2, 4], [3, 4]], type='BeamElement', axes={'ex': [1, 0, 0]})
mdl.add_element(nodes=[0, 1, 4], type='ShellElement')

# print('Element 3 nodes: ', mdl.elements[3].nodes)
# print('Element count: ', mdl.element_count())
# print('Element index: ', mdl.element_index)
# print('Check element with nodes 1-4: ', mdl.check_element_exists([1, 4]))
# print('Check element with nodes 0-1: ', mdl.check_element_exists([0, 1]))

# Add sets

mdl.add_set(name='nset_base', type='node', selection=[0, 1, 2, 3])
mdl.add_set(name='nset_top', type='node', selection=[4])
mdl.add_set(name='elset_beams', type='element', selection=[0, 1, 2, 3])
mdl.add_set(name='elset_shell', type='element', selection=[4])

# print('Set: nset_base: ', mdl.sets['nset_base'])
# print('Set: elset_shell: ', mdl.sets['elset_shell'])

# Add sections

mdl.add([
    CircularSection(name='sec_circ', r=0.010),
    ShellSection(name='sec_shell', t=0.005),
])

# print('Section geometry: ', mdl.sections['sec_circ'].geometry)

# Add materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1500))

# print('Material E: ', mdl.materials['mat_elastic'].E)

# Add element properties

mdl.add([
    Properties(name='ep_circ', material='mat_elastic', section='sec_circ', elset='elset_beams'),
    Properties(name='ep_shell', material='mat_elastic', section='sec_shell', elset='elset_shell'),
])

# Add loads

mdl.add([
    PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000),
    GravityLoad(name='load_gravity', elements='elset_beams'),
])

# print('load_point components: ', mdl.loads['load_point'].components)

# Add displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))

# print('disp_pinned components: ', mdl.displacements['disp_pinned'].components)

# Add steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_loads', loads=['load_point', 'load_gravity']),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Generate input files

mdl.write_input_file(software='abaqus', fields=['s', 'u'])

# Launch App

mdl.view()
