
from compas_fea.cad import blender
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from compas_blender.helpers import network_from_bmesh
from compas_blender.utilities import clear_layers
from compas_blender.utilities import xdraw_mesh
from compas_blender.utilities import xdraw_spheres

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='beam_simple', path='/home/al/temp/')

# Clear

clear_layers(layers=[0, 1, 2, 3])

# Lines

L = 1.0
m = 100
x = [i * L / m for i in range(m + 1)]
vertices = [[xi, 0, 0] for xi in x]
edges = [[i, i + 1] for i in range(m)]
bmesh = xdraw_mesh(name='beam', vertices=vertices, edges=edges, layer=0)

# Points

n = 5
xdraw_spheres([{'pos': [0, 0, 0], 'layer': 1, 'radius': 0.01},
               {'pos': [L, 0, 0], 'layer': 2, 'radius': 0.01}])
xdraw_spheres([{'pos': [i, 0, 0], 'layer': 3, 'radius': 0.005} for i in x[n::n]])

# Elements

network = network_from_bmesh(bmesh=bmesh)
mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement', 
                                    elset='elset_lines', axes={'ex': [0, -1, 0]})

# Sets

blender.add_nset_from_objects(mdl, layer=1, name='nset_left')
blender.add_nset_from_objects(mdl, layer=2, name='nset_right')
blender.add_nset_from_objects(mdl, layer=3, name='nset_weights')

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Sections

_, ekeys, L, Lt = blender.ordered_network(mdl, network=network, layer=1)
for ekey, Li in zip(ekeys, L):
    ri = (1 + Li / Lt) * 0.020
    sname = 'sec_{0}'.format(ekey)
    pname = 'ep_{0}'.format(ekey)
    ename = 'element_{0}'.format(ekey)
    mdl.add_section(CircularSection(name=sname, r=ri))
    ep = Properties(name=pname, material='mat_elastic', section=sname, elsets=ename)
    mdl.add_element_properties(ep)
    
# Displacements

deg = pi / 180
mdl.add_displacements([
    PinnedDisplacement(name='disp_bc_left', nodes='nset_left'),
    GeneralDisplacement(name='disp_bc_right', nodes='nset_right', y=0, z=0, xx=0),
    GeneralDisplacement(name='disp_left', nodes='nset_left', yy=30*deg),
])

# Loads

mdl.add_load(PointLoad(name='load_weights', nodes='nset_weights', z=-200.0))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_bc_left', 'disp_bc_right']),
    GeneralStep(name='step_load', loads=['load_weights'], displacements=['disp_left'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u', 'ur', 'sf', 'sm'], license='research')

blender.plot_data(mdl, step='step_load', field='um', radius=0.01, colorbar_size=0.3, layer=4)
blender.plot_data(mdl, step='step_load', field='ury', radius=0.01, colorbar_size=0.3, layer=5)
blender.plot_data(mdl, step='step_load', field='sfnx', radius=0.01, colorbar_size=0.3, layer=6)
blender.plot_data(mdl, step='step_load', field='sfvy', radius=0.01, colorbar_size=0.3, layer=7)
blender.plot_data(mdl, step='step_load', field='smx', radius=0.01, colorbar_size=0.3, layer=8)
