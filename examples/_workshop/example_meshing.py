
from compas_fea.cad import rhino
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


mdl = Structure(name='mesh_triangle', path='C:/Temp/')

# Triangles

guid = rs.ObjectsByLayer('mesh_triangle')[0]
rhino.discretise_mesh(mesh=guid, layer='mesh_discretised', target=0.900, min_angle=15)

# Weld

rhino.weld_meshes_from_layer(layer_input='mesh_discretised', layer_output='mesh_tetgen')

# Tetrahedrons

mesh = rs.ObjectsByLayer('mesh_tetgen')[0]
rhino.add_tets_from_mesh(mdl, name='mesh_tets', mesh=mesh, volume=0.10, draw_tets='mesh_tets')