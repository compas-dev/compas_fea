"""An example compas_fea package for block elements."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import blender

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import SolidSection
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from compas.cad.blender.utilities import draw_plane
from compas.cad.blender.utilities import clear_layers


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


clear_layers([0])

# Folders and Structure name

name = 'block-deepbeam'
path = '/home/al/Temp/'

# Create an empty Structure object named mdl

mdl = Structure()

# Extrude mesh

ds = 0.05
nz = int(1 / ds)
blender.bmesh_extrude(mdl, bmesh=draw_plane(Lx=1.0, Ly=2.0, dx=ds, dy=ds), nz=nz, dz=ds)

# Add node and element sets to the Structure object

keys = [mdl.check_node_exists(i) for i in [[ds, ds, 0], [1 - ds, ds, 0], [1 - ds, 2 - ds, 0], [ds, 2 - ds, 0]]]
mdl.add_set('nset_supports', 'node', keys)
mdl.add_set('nset_load', 'node', [mdl.check_node_exists([0.5, 1.0, 1.0])])

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**(10), v=0.3, p=1))

# Add sections

mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

ep = ElementProperties(material='mat_elastic', section='sec_solid', elsets='elset_C3D8')
mdl.add_element_properties(ep, name='ep_solid')

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

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse(path, name, software='abaqus', exe=exe, fields='U,S')

# Plot voxels

blender.plot_voxels(mdl, path, name, step='step', vdx=ds, cbar=[0, 1.5], cube_size=[10, 20, 10], layer=1)
