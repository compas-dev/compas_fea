
from compas_fea.cad import blender
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

from compas_blender.utilities import get_objects


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='block_tets', path='/home/al/temp/')

# Tetrahedrons

blender.add_tets_from_bmesh(mdl, name='elset_tets', bmesh=get_objects(layer=0)[0])

# Sets

blender.add_nset_from_bmeshes(mdl, layer=1, name='base')
blender.add_nset_from_bmeshes(mdl, layer=2, name='top')

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=100*10**9, v=0.3, p=1))

# Sections

mdl.add_section(SolidSection(name='sec_solid'))

# Properties

mdl.add_element_properties(
    Properties(name='ep_tets', material='mat_elastic', section='sec_solid', elsets='elset_tets'))

# Displacementss

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='base'))

# Loads

mdl.add_load(PointLoad(name='load_top', nodes='top', y=1000, z=1000))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_top'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u'])
blender.plot_voxels(mdl, step='step_load', field='ux', vdx=0.01)
