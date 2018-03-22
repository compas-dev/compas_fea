
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


# Structure

mdl = Structure(name='truss_frame', path='C:/Temp/')

# Elements

layers = ['elset_main', 'elset_diag', 'elset_stays']
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers=layers)

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_pins', 'nset_load_v', 'nset_load_h'])

# Materials

mdl.add_material(Steel(name='mat_steel', fy=355))

# Sections

mdl.add_sections([
    TrussSection(name='sec_main', A=0.0008),
    TrussSection(name='sec_diag', A=0.0005),
    TrussSection(name='sec_stays', A=0.0001)])

# Properties

mdl.add_element_properties([
    Properties(name='ep_main', material='mat_steel', section='sec_main', elsets='elset_main'),
    Properties(name='ep_diag', material='mat_steel', section='sec_diag', elsets='elset_diag'),
    Properties(name='ep_stays', material='mat_steel', section='sec_stays', elsets='elset_stays')])

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Loads
# Note: GravityLoad doesnt activate for OpenSees

mdl.add_loads([
    PointLoad(name='load_pl_v', nodes='nset_load_v', z=-15500),
    PointLoad(name='load_pl_h', nodes='nset_load_h', x=5000),
    GravityLoad(name='load_gravity', elements=['elset_diag', 'elset_main'])])

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_loads', loads=['load_pl_v', 'load_pl_h', 'load_gravity'], factor=1.5, increments=200)])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run (Sofistik)

mdl.write_input_file(software='sofistik')

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

rhino.plot_data(mdl, step='step_loads', field='um', radius=0.1, scale=10, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_loads', field='smises', iptype='max', nodal='max', radius=0.1, colorbar_size=0.3)

# Run (OpenSees)

mdl.analyse_and_extract(software='opensees', fields=['u', 'sf'])

rhino.plot_data(mdl, step='step_loads', field='sfx', radius=0.1, colorbar_size=0.3)
