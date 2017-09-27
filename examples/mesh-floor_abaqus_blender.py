"""An example compas_fea package use for meshes."""

from compas_blender.helpers import mesh_from_bmesh
from compas_blender.utilities import get_objects

from compas_fea.fea.abaq import abaq
from compas_fea.cad import blender

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'mesh-floor'
path = '/home/al/Temp/'

# Create empty Structure object

mdl = Structure()

# Add truss and shell elements

blender.add_nodes_elements_from_layers(mdl, layers=0, face_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers=1, edge_type='TrussElement')

# Add node and element sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_concrete')
blender.add_elset_from_bmeshes(mdl, layer=1, name='elset_ties')
blender.add_nset_from_objects(mdl, layer=3, name='nset_corners')
blender.add_nset_from_objects(mdl, layer=4, name='nset_corner1')
blender.add_nset_from_objects(mdl, layer=5, name='nset_corner2')

# Add materials

mdl.add_material(Concrete(name='mat_concrete', fck=90))
mdl.add_material(Steel(name='mat_steel', fy=355))

# Add sections

mdl.add_section(ShellSection(name='sec_concrete', t=0.020))
mdl.add_section(TrussSection(name='sec_ties', A=0.0004))

# Add element properties

epc = ElementProperties(material='mat_concrete', section='sec_concrete', elsets='elset_concrete')
eps = ElementProperties(material='mat_steel', section='sec_ties', elsets='elset_ties')
mdl.add_element_properties(epc, name='ep_concrete')
mdl.add_element_properties(eps, name='ep_steel')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_concrete'))

# Add tributary loads from mesh

mesh = mesh_from_bmesh(get_objects(layer=2)[0])
mdl.add_load(TributaryLoad(mdl, name='load_tributary', mesh=mesh, z=-2000))

# Add displacements

mdl.add_displacement(RollerDisplacementXY(name='disp_roller', nodes='nset_corners'))
mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'))
mdl.add_displacement(GeneralDisplacement(name='disp_x', nodes='nset_corner2', x=0))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_roller', 'disp_pinned', 'disp_x']))
mdl.add_step(GeneralStep(name='step_loads', loads=['load_gravity', 'load_tributary'], factor=1.5))
mdl.set_steps_order(['step_bc', 'step_loads'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,S')

# Plot displacements

blender.plot_data(mdl, path, name, step='step_loads', field='U', component='magnitude', radius=0.02, layer=6)

# Plot stress

blender.plot_data(mdl, path, name, step='step_loads', field='S', component='mises', radius=0.02, cbar=[0, 3*10**6], layer=7)
