
from compas_fea.cad import rhino

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='truss_frame', path='C:/Temp/')

# Add truss elements

layers = ['elset_main', 'elset_diag', 'elset_stays']
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers=layers)

# Add node and element sets

layers.extend(['nset_pins', 'nset_load_v', 'nset_load_h'])
rhino.add_sets_from_layers(mdl, layers=layers)

# Add materials

mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_sections([
    TrussSection(name='sec_main', A=0.020),
    TrussSection(name='sec_diag', A=0.005),
    TrussSection(name='sec_stays', A=0.001)])

# Add element properties

ep1 = Properties(name='ep_main', material='mat_steel', section='sec_main', elsets='elset_main')
ep2 = Properties(name='ep_diag', material='mat_steel', section='sec_diag', elsets='elset_diag')
ep3 = Properties(name='ep_stays', material='mat_steel', section='sec_stays', elsets='elset_stays')
mdl.add_element_properties(ep1)
mdl.add_element_properties(ep2)
mdl.add_element_properties(ep3)

# Add loads

mdl.add_loads([
    PointLoad(name='load_pl_v', nodes='nset_load_v', z=-250000),
    PointLoad(name='load_pl_h', nodes='nset_load_h', x=500000),
    GravityLoad(name='load_gravity_main', elements='elset_main'),
    GravityLoad(name='load_gravity_diag', elements='elset_diag'),
])

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_loads', loads=['load_pl_v', 'load_pl_h', 'load_gravity_main', 'load_gravity_diag'], factor=1.5)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot displacements

rhino.plot_data(mdl, step='step_loads', field='um', radius=0.1, scale=10, colorbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='ux', radius=0.1, colorbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='uz', radius=0.1, colorbar_size=0.5)

# Plot stress

rhino.plot_data(mdl, step='step_loads', field='smises', iptype='max', nodal='max', radius=0.1, colorbar_size=0.5)
