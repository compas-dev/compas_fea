"""An example compas_fea package use for meshing."""

# Note: testing for meshing functions.

from compas_fea.cad import blender
from compas_fea.structure import Structure

from compas_blender.geometry import BlenderMesh
from compas_blender.utilities import xdraw_mesh
from compas_blender.utilities import get_objects
from compas_blender.utilities import clear_layer

from compas_fea.utilities import discretise_faces


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


clear_layer(layer=1)

# Create empty Structure object

mdl = Structure(name='mesh_triangle', path='/home/al/Temp/')

# Discretise mesh

blendermesh = BlenderMesh(get_objects(layer=0)[0])
pts = blendermesh.get_vertex_coordinates()
fcs = blendermesh.get_face_vertex_indices()

vertices, faces = discretise_faces(vertices=pts, faces=fcs, target=0.15, min_angle=15, factor=1, iterations=200)
for points, face in zip(vertices, faces):
    bmesh = xdraw_mesh(name='face', vertices=points, faces=face, layer=1, wire=True)
    blender.add_nodes_elements_from_bmesh(mdl, bmesh=bmesh, mesh_type='ShellElement')

# Structure summary

mdl.summary()
