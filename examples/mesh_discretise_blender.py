
from compas_fea.cad import blender
from compas_fea.structure import Structure

from compas_blender.utilities import get_object_by_name


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='mesh_discretise', path='C:/Temp/')

# Discretise

mesh = get_object_by_name(name='mesh_input')
blender.discretise_mesh(mdl, mesh=mesh, layer='elset_mesh', target=0.100, min_angle=15)

# Summary

mdl.summary()
