"""An example compas_fea package use for tetrahedron elements."""

from compas_fea.cad import rhino

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs

__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='block_tets', path='C:/Temp/')

# Add tetrahedrons

mesh = rs.ObjectsByLayer('mesh')[0]
rhino.add_tets_from_mesh(mdl, name='elset_tets', mesh=mesh, draw_tets=True, layer='tets', volume=0.1)

# Add node sets

xr, yr, zr = mdl.node_bounds()
xyz = mdl.nodes_xyz()
nodes_bot = [i for i, c in enumerate(xyz) if c[2] < zr[0] + 0.001]
mdl.add_set(name='nset_bot', type='node', selection=nodes_bot)

# Add materials

mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = Properties(material='mat_steel', section='sec_solid', elsets='elset_tets')
mdl.add_element_properties(ep, name='ep_tets')

# Add loads

mdl.add_load(PointLoad(name='load_top', nodes='nset_all', y=100, z=100))

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

mdl.write_input_file(software='abaqus', fields=['u'])
