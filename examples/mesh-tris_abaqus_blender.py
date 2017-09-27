"""An example compas_fea package use for meshing."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import blender
from compas_fea.structure import Structure

from compas_blender.geometry import bmesh_data
from compas_blender.utilities import draw_bmesh
from compas_blender.utilities import get_objects
from compas_blender.utilities import clear_layers

from compas_fea.utilities.functions import discretise_faces

# Note: test for meshing function.


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


clear_layers(layers=[1])

name = 'mesh-triangle'
path = '/home/al/Temp/'

# Create empty Structure object

mdl = Structure()

# Discretise mesh

pts, _, fcs = bmesh_data(get_objects(layer=0)[0])
vertices, faces = discretise_faces(vertices=pts, faces=fcs, target=0.15, min_angle=15, factor=1, iterations=200)
for points, face in zip(vertices, faces):
    bmesh = draw_bmesh(name='face', vertices=points, faces=face, layer=1, wire=True)
    blender.add_nodes_elements_from_bmesh(mdl, bmesh=bmesh, face_type='ShellElement')

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))
