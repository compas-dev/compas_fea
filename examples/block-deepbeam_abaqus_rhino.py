"""An example compas_fea package for block elements."""

# Note: Requires mayavi to visualise the voxels.

from compas_fea.fea.abaq import abaq
from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.system() == 'Windows':
        raise


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Folders and Structure name

name = 'block-deepbeam'
path = 'C:/Temp/'

# Create an empty Structure object named mdl

mdl = Structure()

# Extrude mesh

nz = 20
dz = 1. / nz
rhino.mesh_extrude(mdl, guid=rs.ObjectsByLayer('base_mesh'), nz=nz, dz=dz)

# Add node and element sets to the Structure object

rhino.add_sets_from_layers(mdl, layers=['nset_load', 'nset_supports'])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**(10), v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = ElementProperties(material='mat_elastic', section='sec_solid', elsets='elset_C3D8')
mdl.add_element_properties(ep, 'ep_solid')

# Add loads

mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Add displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Add steps

mdl.add_step(GeneralStep(name='step', nlgeom=False, displacements=['disp_pinned'], loads=['load_point']))
mdl.set_steps_order(['step'])

# Structure summary

mdl.summary()

# Generate .inp file

fnm = '{0}{1}.inp'.format(path, name)
abaq.inp_generate(mdl, filename=fnm)

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

rhino.plot_data(mdl, path, name, step='step', field='S', component='mises', cbar=[0, 2], voxel=0.3, vdx=dz)
