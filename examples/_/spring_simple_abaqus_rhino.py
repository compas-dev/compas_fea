"""A compas_fea package example for spring elements."""

from compas_fea.cad import rhino

from compas_fea.structure import Structure
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import SpringSection
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import GeneralStep


# Create empty Structure object

mdl = Structure(name='spring_simple', path='C:/Temp/')

# Add truss elements

springs = ['spring_bl', 'spring_br', 'spring_tl', 'spring_tr']
rhino.add_nodes_elements_from_layers(mdl, line_type='SpringElement', layers=springs)

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=springs, explode=True)
rhino.add_sets_from_layers(mdl, layers=['pins', 'middle'])

# Add sections

mdl.add_section(SpringSection(name='spring_elastic', stiffness=10000))
mdl.add_section(SpringSection(name='spring_soft', stiffness=1000))
mdl.add_section(SpringSection(name='spring_nonlinear', 
    forces=[-100, 0, 100], displacements=[-0.01, 0, 0.01]))

# Add element properties

ep_bl = Properties(material=None, section='spring_soft', elsets='spring_bl')
ep_br = Properties(material=None, section='spring_elastic', elsets='spring_br')
ep_tl = Properties(material=None, section='spring_nonlinear', elsets='spring_tl')
ep_tr = Properties(material=None, section='spring_elastic', elsets='spring_tr')
mdl.add_element_properties(ep_bl, name='ep_bl')
mdl.add_element_properties(ep_br, name='ep_br')
mdl.add_element_properties(ep_tl, name='ep_tl')
mdl.add_element_properties(ep_tr, name='ep_tr')

# Add loads

mdl.add_load(PointLoad(name='load_middle', nodes='middle', z=-500))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pins', nodes='pins'))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pins']),
    GeneralStep(name='step_load', loads=['load_middle'])])
mdl.steps_order = ['step_bc', 'step_load']

# Structure summary`

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 'spf'])

# Plot displacements

rhino.plot_data(mdl, step='step_load', field='um', radius=0.2)

# Pring forces

for i in range(4):
    print(mdl.results['step_load']['element']['spfx'][i].values())
