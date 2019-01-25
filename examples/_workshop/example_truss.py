
from compas_fea.structure import Structure
from compas_fea.cad import rhino
#from compas_fea.structure import ElementProperties as Properties
#from compas_fea.structure import GeneralStep
#from compas_fea.structure import GravityLoad
#from compas_fea.structure import PinnedDisplacement
#from compas_fea.structure import PointLoad
#from compas_fea.structure import Steel
#from compas_fea.structure import TrussSection

mdl = Structure(name='example_truss', path='C:/Temp/')

rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='trusses')

#print(mdl.nodes[3])
#print(mdl.node_xyz(3))
#print(mdl.node_count())
#print(mdl.node_index)
#print(mdl.check_node_exists([0, 0, 0]))
#print(mdl.check_node_exists([5, 5, 0]))
#print(mdl.node_bounds())
#
#print(mdl.elements[3])
#print(mdl.elements[3].nodes)
#print(mdl.element_count())
#print(mdl.element_index)
#print(mdl.check_element_exists([2, 3]))

rhino.add_sets_from_layers(mdl, layers=['supports', 'loads'])

#print(mdl.sets['supports'])
#print(mdl.sets['loads'])

#mdl.summary()












#
#
## Materials
#
#mdl.add(Steel(name='mat_steel', fy=355, p=p))
#
## Sections
#
#mdl.add([
#    TrussSection(name='sec_main', A=A1),
#    TrussSection(name='sec_diag', A=A2),
#    TrussSection(name='sec_stays', A=A3),
#])
#
## Properties
#
#mdl.add([
#    Properties(name='ep_main', material='mat_steel', section='sec_main', elset='elset_main'),
#    Properties(name='ep_diag', material='mat_steel', section='sec_diag', elset='elset_diag'),
#    Properties(name='ep_stays', material='mat_steel', section='sec_stays', elset='elset_stays'),
#])
#
## Displacements
#
#mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))
#
## Loads
#
#mdl.add([
#    PointLoad(name='load_v', nodes='nset_load_v', z=-15500),
#    PointLoad(name='load_h', nodes='nset_load_h', x=5000),
#    GravityLoad(name='load_gravity', elements=['elset_diag', 'elset_main']),
#])
#
## Steps
#
#mdl.add([
#    GeneralStep(name='step_bc', displacements=['disp_pinned']),
#    GeneralStep(name='step_loads', loads=['load_v', 'load_h', 'load_gravity'], factor=1.5, increments=300),
#])
#mdl.steps_order = ['step_bc', 'step_loads']
#



## Run
#
#mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'sf', 'cf', 'rf'])
#
#rhino.plot_data(mdl, step='step_loads', field='um', radius=0.1, scale=10, cbar_size=0.3)
#rhino.plot_data(mdl, step='step_loads', field='smises', radius=0.1, cbar_size=0.3)  # abaqus
##rhino.plot_data(mdl, step='step_loads', field='sf1', radius=0.1, cbar_size=0.3)  # opensees
#rhino.plot_reaction_forces(mdl, step='step_loads', scale=0.05)
#rhino.plot_concentrated_forces(mdl, step='step_loads', scale=0.05)
