
from compas_fea.cad import blender
from compas_fea.structure import Structure

from compas_blender.utilities import get_object_by_name


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_discretise', path='C:/Temp/')

# Discretise

mesh = get_object_by_name(name='mesh_input')
blender.discretise_mesh(mdl, mesh=mesh, layer='elset_mesh', target=0.100, min_angle=15)

# Weld

blender.weld_meshes_from_layer(layer_input='elset_mesh', layer_output='elset_welded')

# Summary

mdl.summary()
