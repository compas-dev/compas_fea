
from compas.datastructures import Mesh
from compas.geometry import distance_point_point
from compas_rhino.helpers import mesh_from_guid

from compas_fea.cad import rhino

from compas_fea.structure import BucklingStep
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection

from math import pi

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='mesh_bridge', path='C:/Temp/')

# Add tie and shell elements

rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_ties')
rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_mesh')
rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_ends')

# Add node sets

yr = mdl.node_bounds()[1]
xyz = mdl.nodes_xyz()
nodes_top = [i for i, c in enumerate(xyz) if c[1] > yr[1] - 0.01]
nodes_bot = [i for i, c in enumerate(xyz) if c[1] < yr[0] + 0.01]
mdl.add_set(name='nset_top', type='node', selection=nodes_top)
mdl.add_set(name='nset_bot', type='node', selection=nodes_bot)

# Add element sets

rhino.add_sets_from_layers(mdl, layers=['elset_ties', 'elset_mesh', 'elset_ends'])

# Add materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355)])

# Add sections

mdl.add_sections([
    ShellSection(name='sec_mesh', t=0.004),
    TrussSection(name='sec_ties', A=0.25*pi*0.010**2),
    RectangularSection(name='sec_ends', b=0.03, h=0.03)])

# Add element properties

epc = Properties(name='ep_concrete', material='mat_concrete', section='sec_mesh', elsets='elset_mesh')
eps = Properties(name='ep_steel', material='mat_steel', section='sec_ties', elsets='elset_ties')
epe = Properties(name='ep_ends', material='mat_steel', section='sec_ends', elsets='elset_ends')
mdl.add_element_properties(epc)
mdl.add_element_properties(eps)
mdl.add_element_properties(epe)

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_mesh'))

# Add tributary loads

Gc = 2400 * 9.81
mesh = mesh_from_guid(Mesh(), rs.ObjectsByLayer('elset_mesh')[0])
surface = rs.ObjectsByLayer('surface')[0]
loads = ['load_gravity']

for key in mesh.vertices():
    xyz = mesh.vertex_coordinates(key)
    node = mdl.check_node_exists(xyz)
    pt = rs.ProjectPointToSurface([xyz], surface, [0, 0, 1])[0]
    pz = mesh.vertex_area(key) * distance_point_point(xyz, pt) * Gc
    pname = 'load_{0}'.format(node)
    sname = 'nset_{0}'.format(node)
    mdl.add_set(name=sname, type='node', selection=[node])
    mdl.add_load(PointLoad(name=pname, nodes=sname, z=-pz))
    loads.append(pname)

# Add displacements

mdl.add_displacements([
    RollerDisplacementY(name='disp_top', nodes='nset_top'),
    RollerDisplacementY(name='disp_bot', nodes='nset_bot')])
displacements = ['disp_top', 'disp_bot']

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=displacements),
    GeneralStep(name='step_loads', loads=loads, increments=300, factor=1.35),
    BucklingStep(name='step_buckle', loads=loads, displacements=displacements, modes=1)])
mdl.steps_order = ['step_bc', 'step_loads', 'step_buckle']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot displacements

rhino.plot_data(mdl, step='step_loads', field='uz', radius=0.01, colorbar_size=0.5)

# Plot stress

rhino.plot_data(mdl, step='step_loads', field='smaxp', cbar=[0, 1.5*10**6], radius=0.01, colorbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='sminp', cbar=[-5*10**6, 0], radius=0.01, colorbar_size=0.5)

# Plot buckled shape

rhino.plot_data(mdl, step='step_buckle', field='um', scale=0.3, radius=0.01, colorbar_size=0.5)
print(mdl.results['step_buckle']['info']['description'])
