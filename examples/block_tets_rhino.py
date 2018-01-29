"""An example compas_fea package use for tetrahedron elements."""

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


# Create empty Structure object

mdl = Structure(name='block_tets', path='C:/Temp/')

# Add tetrahedrons

vol = 5 * 10**(-7)
mesh = rs.ObjectsByLayer('mesh')[0]
rhino.add_tets_from_mesh(mdl, name='elset_tets', mesh=mesh, draw_tets=True, layer='tets', volume=vol)

# Add node sets

rhino.add_sets_from_layers(mdl, layers=['nset_bot', 'nset_top'])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=100*10**9, v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = Properties(name='ep_tets', material='mat_elastic', section='sec_solid', elsets='elset_tets')
mdl.add_element_properties(ep)

# Add loads

mdl.add_load(PointLoad(name='load_top', nodes='nset_top', y=100, z=100))

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

# Plot stresses

rhino.plot_data(mdl, step='step_load', field='smises', cbar=[None, None])
#rhino.plot_voxels(mdl, step='step_load', field='smises', cbar=[None, None], vmin=0.3, vdx=0.01)
