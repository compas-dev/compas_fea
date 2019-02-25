
from compas_fea.cad import blender
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import ShellSection
from compas_fea.structure import SolidSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection

from compas_blender.utilities import get_object_by_name


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='block_bridge', path='C:/Temp/')

# Tetrahedrons

blender.add_tets_from_mesh(mdl, name='elset_tets', mesh=get_object_by_name('elset_tets'))

# Elements

blender.add_nodes_elements_from_layers(mdl, layers=['elset_top_plate', 'elset_bot_plate'], mesh_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers='elset_ties', line_type='TrussElement')

# Sets

blender.add_nsets_from_layers(mdl, layers=['nset_supports', 'nset_load'])

# Materials

mdl.add([
    Steel(name='mat_steel', fy=355),
    Concrete(name='mat_concrete', fck=90),
])

# Sections

mdl.add([
    ShellSection(name='sec_plate', t=0.005),
    TrussSection(name='sec_tie', A=0.25*3.142*0.008**2),
    SolidSection(name='sec_solid'),
])

# Properties

mdl.add([
    Properties(name='ep_plate1', material='mat_steel', section='sec_plate', elset='elset_top_plate'),
    Properties(name='ep_plate2', material='mat_steel', section='sec_plate', elset='elset_bot_plate'),
    Properties(name='ep_ties', material='mat_steel', section='sec_tie', elset='elset_ties'),
    Properties(name='ep_concrete', material='mat_concrete', section='sec_solid', elset='elset_tets'),
])

# Displacements

mdl.add(RollerDisplacementY(name='disp_rollers', nodes='nset_supports'))

# Loads

mdl.add([
    GravityLoad(name='load_gravity', elements='elset_tets'),
    PointLoad(name='load_point', nodes='nset_load', z=-5),
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_point'], factor=1.35),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# blender.plot_data(mdl, step='step_loads', field='um', radius=0.01)
# blender.plot_data(mdl, step='step_loads', field='smaxp', radius=0.01, cbar=[0, 3*10**6])
