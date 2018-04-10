
from compas_fea.cad import blender

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
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


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='block_bridge', path='C:/Temp/')

# Add tetrahedrons

blender.add_tets_from_bmesh(mdl, name='elset_tets', bmesh=get_objects(layer=0)[0])

# Add end plates and ties

blender.add_nodes_elements_from_layers(mdl, layers=[1, 2], mesh_type='ShellElement')
blender.add_nodes_elements_from_layers(mdl, layers=[3], line_type='TrussElement')

# Add node sets

blender.add_elset_from_bmeshes(mdl, name='elset_top_plate', layer=1)
blender.add_elset_from_bmeshes(mdl, name='elset_bot_plate', layer=2)
blender.add_elset_from_bmeshes(mdl, name='elset_ties', layer=3)
blender.add_nset_from_bmeshes(mdl, name='nset_supports', layer=4)
blender.add_nset_from_bmeshes(mdl, name='nset_load', layer=5)

# Add materials

mdl.add_materials([
    Steel(name='mat_steel', fy=355),
    Concrete(name='mat_concrete', fck=90)])

# Add sections

mdl.add_sections([
    ShellSection(name='sec_plate', t=0.005),
    TrussSection(name='sec_tie', A=0.25*3.142*0.008**2),
    SolidSection(name='sec_solid')])

# Add element properties

eps = Properties(name='ep_plates', material='mat_steel', section='sec_plate', elsets=['elset_top_plate', 'elset_bot_plate'])
ept = Properties(name='ep_ties', material='mat_steel', section='sec_tie', elsets='elset_ties')
epc = Properties(name='ep_concrete', material='mat_concrete', section='sec_solid', elsets='elset_tets')
mdl.add_element_properties(eps)
mdl.add_element_properties(ept)
mdl.add_element_properties(epc)

# Add loads

mdl.add_loads([
    GravityLoad(name='load_gravity', elements='elset_tets'),
    PointLoad(name='load_point', nodes='nset_load', z=-5)])

# Add displacements

mdl.add_displacement(RollerDisplacementY(name='disp_rollers', nodes='nset_supports'))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_rollers']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_point'], factor=1.35)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])
