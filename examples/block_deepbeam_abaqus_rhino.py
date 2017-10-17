"""An example compas_fea package for block elements."""

# Note: Requires mayavi to visualise the voxels.

from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='block_deepbeam', path='C:/Temp/')

# Extrude mesh

nz = 20
rhino.mesh_extrude(mdl, guid=rs.ObjectsByLayer('base_mesh'), nz=nz, dz=1./nz)

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['nset_load', 'nset_supports'])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**(10), v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = ElementProperties(material='mat_elastic', section='sec_solid', elsets='elset_all')
mdl.add_element_properties(ep, 'ep_solid')

# Add loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Add steps

mdl.add_step(GeneralStep(name='step', displacements=['disp_pinned'], loads=['load_point']))
mdl.set_steps_order(['step'])

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields={'U': 'all', 'S': 'all'})

# Plot displacements

rhino.plot_data(mdl, step='step', field='S', component='mises', cbar=[0, 2], voxel=0.3, vdx=1./nz)
