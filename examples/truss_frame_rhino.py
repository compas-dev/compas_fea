
from compas_fea.cad import rhino
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection


# Author(s): Andrew Liew (github.com/andrewliew)


p  = 7850
A1 = 0.0008
A2 = 0.0005
A3 = 0.0001

# Structure

mdl = Structure(name='truss_frame', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_main', pL=A1*p)
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_diag', pL=A2*p)
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_stays', pL=A3*p)

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_pins', 'nset_load_v', 'nset_load_h'])

# Materials

mdl.add(Steel(name='mat_steel', fy=355, p=p))

# Sections

mdl.add([
    TrussSection(name='sec_main', A=A1),
    TrussSection(name='sec_diag', A=A2),
    TrussSection(name='sec_stays', A=A3),
])

# Properties

mdl.add([
    Properties(name='ep_main', material='mat_steel', section='sec_main', elset='elset_main'),
    Properties(name='ep_diag', material='mat_steel', section='sec_diag', elset='elset_diag'),
    Properties(name='ep_stays', material='mat_steel', section='sec_stays', elset='elset_stays'),
])

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Loads

mdl.add([
    PointLoad(name='load_v', nodes='nset_load_v', z=-15500),
    PointLoad(name='load_h', nodes='nset_load_h', x=5000),
    GravityLoad(name='load_gravity', elements=['elset_diag', 'elset_main']),
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_loads', loads=['load_v', 'load_h', 'load_gravity'], factor=1.5, increments=300),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'sf', 'cf', 'rf'], ndof=3)

rhino.plot_data(mdl, step='step_loads', field='um', radius=0.1, scale=10, cbar_size=0.3)
rhino.plot_data(mdl, step='step_loads', field='sxx', radius=0.1, cbar_size=0.3)  # abaqus:sxx opensees:sf1
rhino.plot_reaction_forces(mdl, step='step_loads', scale=0.05)
rhino.plot_concentrated_forces(mdl, step='step_loads', scale=0.2)

print(mdl.get_nodal_results(step='step_loads', field='um', nodes='nset_load_v'))
print(mdl.get_nodal_results(step='step_loads', field='rfm', nodes='nset_pins'))
print(mdl.get_element_results(step='step_loads', field='sxx', elements='elset_main'))