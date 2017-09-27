"""An example compas_fea package use for meshes."""

from compas.datastructures.mesh.mesh import Mesh
from compas_rhino.helpers.mesh import mesh_from_guid

from compas_fea.fea.abaq import abaq
from compas_fea.cad import rhino

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import ModalStep
from compas_fea.structure import PointLoad
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection

from compas.geometry import distance_point_point

from math import pi

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'mesh-bridge'
path = 'C:/Temp/'
option = 'v10'

# Create empty Structure object

mdl = Structure()

# Add tie and shell elements

rhino.add_nodes_elements_from_layers(mdl, element_type='TrussElement', layers='{0}::ties'.format(option))
rhino.add_nodes_elements_from_layers(mdl, element_type='ShellElement', layers='{0}::Mesh_bottom'.format(option))

# Add node and element sets

xr, yr, zr = mdl.node_bounds()
nodes_top = [i for i in mdl.nodes if mdl.nodes[i]['y'] > yr[1] - 0.01]
nodes_bot = [i for i in mdl.nodes if mdl.nodes[i]['y'] < yr[0] + 0.01]
mdl.add_set(name='nset_top', type='node', selection=nodes_top)
mdl.add_set(name='nset_bot', type='node', selection=nodes_bot)
rhino.add_sets_from_layers(mdl, layers=['{0}::ties'.format(option)])
rhino.add_sets_from_layers(mdl, layers=['{0}::Mesh_bottom'.format(option)])

# Add materials

mdl.add_material(Concrete(name='mat_concrete', fck=90))
mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_section(ShellSection(name='sec_formwork', t=0.005))
mdl.add_section(TrussSection(name='sec_ties', A=0.25*pi*0.01**2))

# Add element properties

epc = ElementProperties(material='mat_concrete', section='sec_formwork', elsets='Mesh_bottom')
eps = ElementProperties(material='mat_steel', section='sec_ties', elsets='ties')
mdl.add_element_properties(epc, name='ep_concrete')
mdl.add_element_properties(eps, name='ep_steel')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

# Add tributary loads

Gc = 2400 * 9.81
mesh= mesh_from_guid(Mesh(), rs.ObjectsByLayer('{0}::Mesh_bottom'.format(option))[0])
surface = rs.ObjectsByLayer('{0}::surface'.format(option))[0]
loads = ['load_gravity']
for key in mesh.vertices():
    xyz = mesh.vertex_coordinates(key)
    node = mdl.check_node_exists(xyz)
    pt = rs.ProjectPointToSurface([xyz], surface, [0, 0, 1])[0]
    pz = mesh.vertex_area(key) * distance_point_point(xyz, pt) * Gc
    pname = 'load_{0}'.format(node)
    sname = 'nset_{0}'.format(node)
    mdl.add_load(PointLoad(name=pname, nodes=sname, z=-pz))
    mdl.add_set(name=sname, type='node', selection=[node])
    loads.append(pname)

# Add displacements

mdl.add_displacement(RollerDisplacementY(name='disp_top', nodes='nset_top'))
mdl.add_displacement(RollerDisplacementY(name='disp_bot', nodes='nset_bot'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_top', 'disp_bot']))
mdl.add_step(GeneralStep(name='step_loads', loads=loads, increments=300, factor=1.35))
mdl.add_step(ModalStep(name='step_buckle', loads=loads, displacements=['disp_top', 'disp_bot'], modes=1))
mdl.set_steps_order(['step_bc', 'step_loads', 'step_buckle'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

#mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

layer = '{0}::U3'.format(option)
rhino.plot_data(mdl, path, name, step='step_loads', field='U', component='U3', layer=layer, radius=0.01)

# Plot stress

rhino.plot_data(mdl, path, name, step='step_loads', field='S', component='maxPrincipal', 
                layer='{0}::SMAX'.format(option), cbar=[0, 3.5*10**6], radius=0.01)
rhino.plot_data(mdl, path, name, step='step_loads', field='S', component='minPrincipal', 
                layer='{0}::SMIN'.format(option), cbar=[-5*10**6, 0], radius=0.01)

# Plot buckled shape

rhino.plot_data(mdl, path, name, step='step_buckle', field='U', component='magnitude', 
                layer='{0}::BUCKLE'.format(option), scale=0.3, radius=0.01)

# Plot principal stresses

rhino.plot_principal_stresses(mdl, path, name, step='step_loads', ptype='min', scale=0.2, 
                    layer='{0}::COM'.format(option))
rhino.plot_principal_stresses(mdl, path, name, step='step_loads', ptype='max', scale=0.2, 
                    layer='{0}::TEN'.format(option))
