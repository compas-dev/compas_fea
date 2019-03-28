
from compas.datastructures import Mesh
from compas.geometry import distance_point_point
from compas_rhino.helpers import mesh_from_guid

from compas_fea.cad import rhino
from compas_fea.structure import BucklingStep
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoads
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection

from math import pi

import rhinoscriptsyntax as rs


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_bridge', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_ties')
rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_ends')

# Sets

ymin, ymax = mdl.node_bounds()[1]
nodes_top = [i for i, node in mdl.nodes.items() if node.y > ymax - 0.01]
nodes_bot = [i for i, node in mdl.nodes.items() if node.y < ymin + 0.01]
mdl.add_set(name='nset_top', type='node', selection=nodes_top)
mdl.add_set(name='nset_bot', type='node', selection=nodes_bot)

# Materials

mdl.add([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355),
])

# Sections

mdl.add([
    ShellSection(name='sec_mesh', t=0.004),
    TrussSection(name='sec_ties', A=0.25*pi*0.010**2),
    RectangularSection(name='sec_ends', b=0.030, h=0.030),
])

# Properties

mdl.add([
    Properties(name='ep_mesh', material='mat_concrete', section='sec_mesh', elset='elset_mesh'),
    Properties(name='ep_ties', material='mat_steel', section='sec_ties', elset='elset_ties'),
    Properties(name='ep_ends', material='mat_steel', section='sec_ends', elset='elset_ends'),
])

# Displacements

mdl.add([
    RollerDisplacementY(name='disp_top', nodes='nset_top'),
    RollerDisplacementY(name='disp_bot', nodes='nset_bot'),
])

# Loads

mdl.add(GravityLoad(name='load_gravity', elements='elset_mesh'))

mesh = mesh_from_guid(Mesh(), rs.ObjectsByLayer('elset_mesh')[0])
point_loads = {}
for key in mesh.vertices():
    xyz = mesh.vertex_coordinates(key)
    pt = rs.ProjectPointToSurface([xyz], rs.ObjectsByLayer('surface')[0], [0, 0, 1])[0]
    pz = mesh.vertex_area(key) * distance_point_point(xyz, pt) * 2400 * 9.81
    point_loads[mdl.check_node_exists(xyz)] = {'z': -pz}
mdl.add(PointLoads(name='load_points', components=point_loads))

# Steps

displacements = ['disp_top', 'disp_bot']
loads = ['load_gravity', 'load_points']

mdl.add([
    GeneralStep(name='step_bc', displacements=displacements),
    GeneralStep(name='step_loads', loads=loads, factor=1.35),
    BucklingStep(name='step_buckle', loads=loads, displacements=displacements, modes=5),
])
mdl.steps_order = ['step_bc', 'step_loads', 'step_buckle']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], components=['ux', 'uy', 'uz', 'um', 'smaxp', 'sminp'])

rhino.plot_data(mdl, step='step_loads', field='uz', radius=0.01, cbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='smaxp', cbar=[0, 1.5*10**6], radius=0.01, cbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='sminp', cbar=[-5*10**6, 0], radius=0.01, cbar_size=0.5)

rhino.plot_mode_shapes(mdl, step='step_buckle', scale=0.5, radius=0.001)
