
from compas_fea.cad import rhino

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Discretise

guid = rs.ObjectsByLayer('mesh_input')[0]
rhino.discretise_mesh(mesh=guid, layer='elset_mesh', target=0.050, min_angle=15)
