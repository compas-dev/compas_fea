
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='block_tets', path='C:/Temp/')

# Tetrahedrons

mesh = rs.ObjectsByLayer('mesh')[0]
rhino.add_tets_from_mesh(mdl, name='elset_tets', mesh=mesh, draw_tets=0, layer='tets', volume=None)

# Sets

rhino.add_sets_from_layers(mdl, layers=['base', 'top'])

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

mdl.add_load(PointLoad(name='load_top', nodes='top', y=100, z=100))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_top'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u'])
rhino.plot_voxels(mdl, step='step_load', field='um', vdx=0.05)
