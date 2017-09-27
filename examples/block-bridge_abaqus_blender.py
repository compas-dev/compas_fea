"""An example compas_fea package use for tetrahedron elements."""

from compas_fea.fea.abaq import abaq
from compas_fea.cad import blender

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import ShellSection
from compas_fea.structure import PointLoad
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import SolidSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection

from compas_blender.utilities import get_objects


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'block-bridge'
path = '/home/al/Temp/'

# Create empty Structure object

mdl = Structure()

# Add tetrahedrons

blender.add_tets_from_bmesh(mdl, name='elset_tets', bmesh=get_objects(layer=0)[0])

# Add end plates and ties

blender.add_nodes_elements_from_layers(mdl, layers=[1, 2], face_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers=[3], edge_type='TrussElement')

# Add node sets

blender.add_elset_from_bmeshes(mdl, name='elset_top-plate', layer=1)
blender.add_elset_from_bmeshes(mdl, name='elset_bot-plate', layer=2)
blender.add_elset_from_bmeshes(mdl, name='elset_ties', layer=3)
blender.add_nset_from_bmeshes(mdl, name='nset_supports', layer=4)
blender.add_nset_from_bmeshes(mdl, name='nset_load', layer=5)

# Add materials

mdl.add_material(Steel(name='mat_steel', fy=355))
mdl.add_material(Concrete(name='mat_concrete', fck=90))

# Add sections

A = 0.25 * 3.142 * 0.008**2
mdl.add_section(ShellSection(name='sec_plate', t=0.005))
mdl.add_section(TrussSection(name='sec_tie', A=A))
mdl.add_section(SolidSection(name='sec_solid'))

# Add element properties

eps = ElementProperties(material='mat_steel', section='sec_plate', elsets=['elset_top-plate', 'elset_bot-plate'])
ept = ElementProperties(material='mat_steel', section='sec_tie', elsets='elset_ties')
epc = ElementProperties(material='mat_concrete', section='sec_solid', elsets='elset_tets')
mdl.add_element_properties(eps, name='ep_plates')
mdl.add_element_properties(ept, name='ep_ties')
mdl.add_element_properties(epc, name='ep_concrete')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))
mdl.add_load(PointLoad(name='load_point', nodes='nset_load', z=-5))

# Add displacements

mdl.add_displacement(RollerDisplacementY(name='disp_rollers', nodes='nset_supports'))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_rollers']))
mdl.add_step(GeneralStep(name='step_loads', loads=['load_gravity', 'load_point'], factor=1.35))
mdl.set_steps_order(['step_bc', 'step_loads'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path, name, software='abaqus', fields='U,S')
