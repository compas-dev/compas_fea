""" Example Meshmould analysed with shell elements and rebar."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import rhino

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'mesh-mould'
path = 'C:/Temp/'

# Create empty Structure object

mdl = Structure()

# Add shell elements

rhino.add_nodes_elements_from_layers(mdl, element_type='ShellElement', layers=['elset_wall', 'elset_plinth'])

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['nset_fixed', 'elset_wall', 'elset_plinth'])

# Add materials

mdl.add_material(Concrete(name='mat_concrete', fck=40))
mdl.add_material(Steel(name='mat_rebar', fy=500))

# Add sections

mdl.add_section(ShellSection(name='sec_wall', t=0.150))
mdl.add_section(ShellSection(name='sec_plinth', t=0.300))

# Add element properties

reb_plinth = {'orientation': None, 'offset': 0.120, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010}
reb_wall = {'orientation': None, 'offset': 0.045, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.010}
epp = ElementProperties(material='mat_concrete', section='sec_plinth', elsets='elset_plinth', reinforcement=reb_plinth)
epw = ElementProperties(material='mat_concrete', section='sec_wall', elsets='elset_wall', reinforcement=reb_wall)
mdl.add_element_properties(epp, name='ep_plinth')
mdl.add_element_properties(epw, name='ep_wall')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))
loads = ['load_gravity']
for guid in rs.ObjectsByLayer('nset_loads'):
    px, py, pz = rs.ObjectName(guid).split(' ')
    node = mdl.check_node_exists(rs.PointCoordinates(guid))
    mdl.add_load(PointLoad(name='load_point_{0}'.format(node), nodes=node, z=float(pz)))
    loads.append('load_point_{0}'.format(node))

# Add displacements

mdl.add_displacement(FixedDisplacement(name='disp_fixed', nodes='nset_fixed'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', nlgeom=False, displacements=['disp_fixed']))
mdl.add_step(GeneralStep(name='step_loads', nlgeom=False, loads=loads))
mdl.set_steps_order(['step_bc', 'step_loads'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

rhino.plot_data(mdl, path, name, step='step_loads', field='U', component='magnitude')

# Plot stress

rhino.plot_data(mdl, path, name, step='step_loads', field='S', component='maxPrincipal')
rhino.plot_data(mdl, path, name, step='step_loads', field='S', component='minPrincipal')

# Plot rebar force

rhino.plot_data(mdl, path, name, step='step_loads', field='RBFOR', component='VALUE',
                iptype='max', nodal='max')
