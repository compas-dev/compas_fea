"""An example compas_fea package use for beam elements."""

from compas_fea.cad import rhino

from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from math import pi

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


rs.EnableRedraw(False)

# Create empty Structure object

mdl = Structure(name='beam_simple', path='C:/Temp/')

# Clear layers

for layer in ['elset_lines', 'nset_left', 'nset_right', 'nset_weights']:
    rs.DeleteObjects(rs.ObjectsByLayer(layer))

# Create beam

L = 1.0
nx = 100
x = [i * L / nx for i in range(nx + 1)]
rs.CurrentLayer('elset_lines')
[rs.AddLine([x[i], 0, 0], [x[i + 1], 0, 0]) for i in range(nx)]
network = rhino.network_from_lines(rs.ObjectsByLayer('elset_lines'))

# Create end-points

rs.CurrentLayer('nset_left')
rs.AddPoint([0, 0, 0])
rs.CurrentLayer('nset_right')
rs.AddPoint([L, 0, 0])

# Create weights

spacing = 5
weight = -1.0
rs.CurrentLayer('nset_weights')
for xi in x[spacing::spacing]:
    rs.AddPoint([xi, 0, 0])

rs.EnableRedraw(True)

# Add beam elements from Network

mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement')

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['nset_left', 'nset_right', 'nset_weights'])
rhino.add_sets_from_layers(mdl, layers=['elset_lines'], explode=True)

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Add sections

nodes, elements, arclengths, L = rhino.ordered_lines(mdl, network=network, layer='nset_left')
for c, i in enumerate(arclengths):
    ri = (((i / L) - 0.5)**2 + 0.4) * 0.01
    sname = 'sec_rod_{0}'.format(elements[c])
    ename = 'element_{0}'.format(elements[c])
    pname = 'ep_{0}'.format(elements[c])
    mdl.add_section(CircularSection(name=sname, r=ri))
    ep = ElementProperties(material='mat_elastic', section=sname, elsets=ename)
    mdl.add_element_properties(ep, name=pname)

# Add loads

mdl.add_load(PointLoad(name='load_weights', nodes='nset_weights', z=weight))

# Add displacements

deg = pi / 180
mdl.add_displacement(GeneralDisplacement(name='disp_left', nodes='nset_left', x=0, y=0, z=0, xx=0, zz=0, yy=30*deg))
mdl.add_displacement(GeneralDisplacement(name='disp_right', nodes='nset_right', y=0, z=-0.2, xx=0, zz=0, yy=30*deg))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_weights']))
mdl.set_steps_order(['step_bc', 'step_load'])

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields='all')

# Plot displacements

rhino.plot_data(mdl, step='step_load', field='U', component='magnitude', radius=0.01)
rhino.plot_data(mdl, step='step_load', field='UR', component='UR2', radius=0.01)

# Plot section forces/moments

rhino.plot_data(mdl, step='step_load', field='SF', component='SF1', radius=0.01)
rhino.plot_data(mdl, step='step_load', field='SF', component='SF3', radius=0.01)
rhino.plot_data(mdl, step='step_load', field='SM', component='SM2', radius=0.01)
