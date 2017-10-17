"""An example compas_fea package use for beam elements."""

from math import pi

from compas_fea.cad import blender

from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from compas_blender.helpers import network_from_bmesh
from compas_blender.utilities import xdraw_mesh
from compas_blender.utilities import xdraw_spheres
from compas_blender.utilities import clear_layers


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='beam_simple', path='/home/al/Temp/')

# Clear layers

clear_layers(layers=[0, 1, 2, 3])

# Create beam

L = 1.0
nx = 100
x = [i * L / nx for i in range(nx + 1)]
vertices = [[xi, 0, 0] for xi in x]
edges = [[i, i + 1] for i in range(nx)]
bmesh = xdraw_mesh(name='beam', vertices=vertices, edges=edges, layer=0)
xdraw_spheres([{'pos': [0, 0, 0], 'layer': 1, 'radius': 0.01},
               {'pos': [L, 0, 0], 'layer': 2, 'radius': 0.01}])

# Weights

spacing = 5
weight = -1.0
xdraw_spheres([{'pos': [xi, 0, 0], 'layer': 3, 'radius': 0.005} for xi in x[spacing::spacing]])

# Add beam elements

blender.add_nodes_elements_from_bmesh(mdl, bmesh=bmesh, edge_type='BeamElement')

# Add node and element sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_lines', explode=True)
blender.add_nset_from_objects(mdl, layer=1, name='nset_left')
blender.add_nset_from_objects(mdl, layer=2, name='nset_right')
blender.add_nset_from_objects(mdl, layer=3, name='nset_weights')

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Add sections

network = network_from_bmesh(bmesh)
nodes, elements, arclengths, L = blender.ordered_lines(mdl, network=network, layer=1)
for c, i in enumerate(arclengths):
    ri = (((i / L) - 0.5)**2 + 0.4) * 0.01
    pname = 'ep_{0}'.format(elements[c])
    sname = 'sec_rod_{0}'.format(elements[c])
    ename = 'element_{0}'.format(elements[c])
    mdl.add_section(CircularSection(name=sname, r=ri))
    ep = ElementProperties(material='mat_elastic', section=sname, elsets=ename)
    mdl.add_element_properties(ep, name=pname)

# Add loads

mdl.add_load(PointLoad(name='load_weights', nodes='nset_weights', z=weight))

# Add displacements

deg = pi / 180
mdl.add_displacement(GeneralDisplacement(name='disp_left', nodes='nset_left', x=0, y=0, z=0, yy=20*deg, xx=0, zz=0))
mdl.add_displacement(GeneralDisplacement(name='disp_right', nodes='nset_right', y=0, z=-0.2, xx=0, yy=20*deg, zz=0))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_left', 'disp_right']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_weights']))
mdl.set_steps_order(['step_bc', 'step_load'])

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields={'U': 'all', 'UR': 'all', 'SF': 'all', 'SM': 'all'})

# Plot displacements

blender.plot_data(mdl, step='step_load', field='U', component='magnitude', radius=0.01, layer=4)
blender.plot_data(mdl, step='step_load', field='UR', component='UR2', radius=0.01, layer=5)

# Plot section forces/moments

blender.plot_data(mdl, step='step_load', field='SF', component='SF1', radius=0.01, layer=6)
blender.plot_data(mdl, step='step_load', field='SF', component='SF3', radius=0.01, layer=7)
blender.plot_data(mdl, step='step_load', field='SM', component='SM2', radius=0.01, layer=8)
