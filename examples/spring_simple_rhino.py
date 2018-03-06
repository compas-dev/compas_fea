
# Note: Abaqus and OpenSees results dont yet match.

from compas_fea.cad import rhino

from compas_fea.structure import Structure
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import SpringSection
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementXZ
from compas_fea.structure import PointLoad
from compas_fea.structure import GeneralStep


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='spring_simple', path='C:/Temp/')

# Add truss elements

springs = ['spring_bot_left', 'spring_bot_right', 'spring_top_left', 'spring_top_right']
rhino.add_nodes_elements_from_layers(mdl, line_type='SpringElement', layers=springs)

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=springs)
rhino.add_sets_from_layers(mdl, layers=['pins', 'middle'])

# Add sections

mdl.add_section(SpringSection(name='spring_elastic', stiffness={'axial': 10000}))
mdl.add_section(SpringSection(name='spring_soft', stiffness={'axial': 1000}))
mdl.add_section(SpringSection(name='spring_nonlinear',
    forces={'axial': [-100, -100, 0, 100, 100]}, displacements={'axial': [-1, -0.01, 0, 0.01, 1]}))

# Add element properties

ep_bl = Properties(name='ep_bl', material=None, section='spring_nonlinear', elsets='spring_bot_left')
ep_br = Properties(name='ep_br', material=None, section='spring_elastic', elsets='spring_bot_right')
ep_tl = Properties(name='ep_tl', material=None, section='spring_elastic', elsets='spring_top_left')
ep_tr = Properties(name='ep_tr', material=None, section='spring_soft', elsets='spring_top_right')
mdl.add_element_properties(ep_bl)
mdl.add_element_properties(ep_br)
mdl.add_element_properties(ep_tl)
mdl.add_element_properties(ep_tr)

# Add loads

mdl.add_load(PointLoad(name='load_middle', nodes='middle', z=-500))

# Add displacements

mdl.add_displacements([
    PinnedDisplacement(name='disp_pins', nodes='pins'),
    RollerDisplacementXZ(name='disp_roller', nodes='middle')])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pins', 'disp_roller']),
    GeneralStep(name='step_load', loads=['load_middle'])])
mdl.steps_order = ['step_bc', 'step_load']

# Structure summary`

mdl.summary()

# Run and extract data

#mdl.analyse_and_extract(software='abaqus', fields=['u', 'spf'])
mdl.analyse_and_extract(software='opensees', fields=['u', 'spf'])

# Plot displacements

rhino.plot_data(mdl, step='step_load', field='um', radius=0.02)

# Spring forces

rhino.plot_data(mdl, step='step_load', field='spfx', radius=0.02)
