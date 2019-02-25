
from compas_blender.utilities import mesh_from_bmesh
from compas_blender.utilities import get_object_by_name

from compas_fea.cad import blender
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PrestressLoad
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection

from math import pi


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_floor', path='C:/Temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, layers='elset_floor', mesh_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers='elset_ties', line_type='TrussElement')

# Sets

blender.add_nsets_from_layers(mdl, layers=['nset_corner1', 'nset_corner2'])
edges = [i for i in mdl.nodes if mdl.nodes[i].z < 0.001]
mdl.add_set(name='nset_edges', type='node', selection=edges)

# Materials

mdl.add([
    Concrete(name='mat_concrete', fck=90, fr=[1.16, 0.15]),
    Steel(name='mat_steel', fy=355),
])

# Sections

mdl.add([
    ShellSection(name='sec_floor', t=0.050),
    TrussSection(name='sec_ties', A=pi*0.25*0.030**2),
])

# Properties

mdl.add([
    Properties(name='ep_floor', material='mat_concrete', section='sec_floor', elset='elset_floor'),
    Properties(name='ep_ties', material='mat_steel', section='sec_ties', elset='elset_ties'),
])

# Displacements

mdl.add([
    RollerDisplacementXY(name='disp_edges', nodes='nset_edges'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'),
    GeneralDisplacement(name='disp_xdof', nodes='nset_corner2', x=0),
])

# Loads

mdl.add([
    GravityLoad(name='load_gravity', elements='elset_floor'),
    PrestressLoad(name='load_prestress', elements='elset_ties', sxx=10*10**6),
    TributaryLoad(mdl, name='load_area', mesh=mesh_from_bmesh(get_object_by_name('load_mesh')), z=-2000),
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_edges', 'disp_pinned', 'disp_xdof']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_area'], factor={'load_gravity': 1.35, 'load_area': 1.50}),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'cf'], components=['ux', 'uy', 'uz', 'smises', 'cfx', 'cfy', 'cfz'])

# blender.plot_data(mdl, step='step_loads', field='uz', radius=0.02, cbar_size=0.5)
# blender.plot_data(mdl, step='step_loads', field='smises', radius=0.02, cbar_size=0.5, cbar=[0, 5*10**6])
# blender.plot_concentrated_forces(mdl, step='step_loads')
