
from compas_fea.cad import rhino
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementXZ
from compas_fea.structure import SpringSection
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='spring_simple', path='C:/Temp/')

# Elements

springs = ['spring_bot_left', 'spring_bot_right', 'spring_top_left', 'spring_top_right']
rhino.add_nodes_elements_from_layers(mdl, line_type='SpringElement', layers=springs)

# Sets

rhino.add_sets_from_layers(mdl, layers=['pins', 'middle'])

# Sections

mdl.add([
    SpringSection(name='spring_elastic', stiffness={'axial': 10000}),
    SpringSection(name='spring_soft', stiffness={'axial': 1000}),
])

# Properties

mdl.add([
    Properties(name='ep_bl', section='spring_elastic', elset='spring_bot_left'),
    Properties(name='ep_br', section='spring_soft', elset='spring_bot_right'),
    Properties(name='ep_tl', section='spring_elastic', elset='spring_top_left'),
    Properties(name='ep_tr', section='spring_elastic', elset='spring_top_right'),
])

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_pins', nodes='pins'),
    RollerDisplacementXZ(name='disp_roller', nodes='middle'),
])

# Loads

mdl.add(PointLoad(name='load_middle', nodes='middle', z=-500))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_roller']),
    GeneralStep(name='step_load', loads='load_middle'),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary`

mdl.summary()

# Run

mdl.analyse_and_extract(software='opensees', fields=['u', 'spf'], ndof=3)

rhino.plot_data(mdl, step='step_load', field='um', radius=0.02)
rhino.plot_data(mdl, step='step_load', field='spfx', radius=0.02)

print(mdl.get_element_results(step='step_load', field='spfx'))