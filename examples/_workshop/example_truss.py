
from compas_fea.cad import rhino
from compas_fea.structure import Structure
from compas_fea.structure import Steel
from compas_fea.structure import TrussSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import GeneralStep


mdl = Structure(name='example_truss', path='C:/Temp/')

rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='trusses')
#print(mdl.nodes[3])
#print(mdl.node_xyz(3))
#print(mdl.node_count())
#print(mdl.node_index)
#print(mdl.check_node_exists([0, 0, 0]))
#print(mdl.check_node_exists([5, 5, 0]))
#print(mdl.node_bounds())
#print(mdl.elements[3])
#print(mdl.elements[3].nodes)
#print(mdl.element_count())
#print(mdl.element_index)
#print(mdl.check_element_exists([2, 3]))

rhino.add_sets_from_layers(mdl, layers=['supports', 'loads'])
#print(mdl.sets['supports'])
#print(mdl.sets['loads'])

mdl.add(Steel(name='steel', fy=355))
#print(mdl.materials['steel'])

mdl.add(TrussSection(name='section', A=0.001))
#print(mdl.sections['section'])

mdl.add(ElementProperties(name='property', material='steel', section='section', elset='trusses'))
#print(mdl.element_properties['property'])

mdl.add(PinnedDisplacement(name='pinned', nodes='supports'))
#print(mdl.displacements['pinned'])

mdl.add([
    PointLoad(name='pointloads', nodes='loads', y=-50000),
    GravityLoad(name='gravity', elements='trusses', z=0, y=1),
])
#print(mdl.loads['pointloads'])
#print(mdl.loads['gravity'])

mdl.add([
    GeneralStep(name='bc', displacements='pinned'),
    GeneralStep(name='loads', loads=['pointloads', 'gravity'], factor=1.5),
])
mdl.steps_order = ['bc', 'loads']
#print(mdl.steps['bc'])
#print(mdl.steps['loads'])

mdl.summary()

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'cf', 'rf'])
# open .inp and .odb files

rhino.plot_data(mdl, step='loads', field='um', radius=0.1, scale=10, cbar_size=0.3)
rhino.plot_data(mdl, step='loads', field='smises', radius=0.1, cbar_size=0.3)
rhino.plot_reaction_forces(mdl, step='loads', scale=0.1)
rhino.plot_concentrated_forces(mdl, step='loads', scale=0.1)
# edit parameters and geometry

mdl.save_to_obj()
