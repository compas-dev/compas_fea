
# Note: testing script for meshing functions.

from compas_fea.cad import blender
from compas_fea.structure import Structure

from compas_blender.geometry import BlenderMesh
from compas_blender.utilities import clear_layer
from compas_blender.utilities import get_objects
from compas_blender.utilities import xdraw_mesh

import compas_fea.utilities.functions as functions
import imp
imp.reload(functions)


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


clear_layer(layer=1)

# Structure

mdl = Structure(name='mesh_tris', path='/home/al/temp/')

# Discretise

blendermesh = BlenderMesh(get_objects(layer=0)[0])
pts = blendermesh.get_vertex_coordinates()
fcs = blendermesh.get_face_vertex_indices()

vertices, faces = functions.discretise_faces(vertices=pts, faces=fcs, target=0.1, min_angle=15, factor=1, iterations=50)
for pts, fc in zip(vertices, faces):
    bmesh = xdraw_mesh(name='face', vertices=pts, faces=fc, layer=1, wire=True)
    blender.add_nodes_elements_from_bmesh(mdl, bmesh=bmesh, mesh_type='ShellElement')

# Summary

mdl.summary()
