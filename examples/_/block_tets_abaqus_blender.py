"""An example compas_fea package use for tetrahedron elements."""

from compas_fea.cad import blender

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure

from compas_blender.utilities import get_objects


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='block_tets', path='/home/al/Temp/')

# Add tetrahedrons

blender.add_tets_from_bmesh(mdl, name='elset_tets', bmesh=get_objects(layer=0)[0], draw_tets=False, volume=0.002)

# Add node sets

blender.add_nset_from_bmeshes(mdl, layer=1, name='nset_top')
blender.add_nset_from_bmeshes(mdl, layer=2, name='nset_bot')

# Add materials

mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = Properties(material='mat_steel', section='sec_solid', elsets='elset_tets')
mdl.add_element_properties(ep, name='ep_tets')

# Add loads

mdl.add_load(PointLoad(name='load_top', nodes='nset_all', y=0.1, z=0.1))

# Add displacementss

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_bot'))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_top'])])
mdl.steps_order = ['step_bc', 'step_load']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot voxels

blender.plot_voxels(mdl, step='step_load', vdx=0.02, cbar=[0, 200], cube_size=[10, 10, 20], layer=3)
