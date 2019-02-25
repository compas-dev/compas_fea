
from compas_fea.cad import rhino

import rhinoscriptsyntax as rs


# Author(s): Andrew Liew (github.com/andrewliew)


# Discretise

guid = rs.ObjectsByLayer('mesh_input')[0]
rhino.discretise_mesh(mesh=guid, layer='elset_mesh', target=0.050, min_angle=15)
