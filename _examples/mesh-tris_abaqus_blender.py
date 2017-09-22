"""An example compas_fea package use for meshing."""

from compas_fea.fea.abaq import abaq
from compas_fea.structure import Structure
from compas_fea.utilities.functions import discretise_vertices_faces

from compas.cad.blender.geometry import bmesh_data
from compas.cad.blender.utilities import draw_bmesh
from compas.cad.blender.utilities import get_objects
from compas.cad.blender.utilities import clear_layers

# Note: test meshing script/example.


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


clear_layers([1])

# Folders and Structure name

name = 'mesh-triangle'
path = '/home/al/Temp/'

# Create an empty Structure object named mdl

mdl = Structure()

# Discretise mesh

vertices, edges, faces = bmesh_data(get_objects(0)[0])
vertices, faces = discretise_vertices_faces(vertices, faces, target=0.150, min_angle=20, factor=2, iterations=100)
for points, face in zip(vertices, faces):
    draw_bmesh(name='face', vertices=points, faces=face, layer=1, wire=True)
    for tri in face:
        xyz = [points[i] for i in tri]
        nodes = [mdl.add_node(i) for i in xyz]
        mdl.add_element(nodes, type='ShellElement')

# Structure summary

mdl.summary()

# Generate .inp file

fnm = '{0}{1}.inp'.format(path, name)
abaq.inp_generate(mdl, filename=fnm)
