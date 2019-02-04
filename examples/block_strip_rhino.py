
from compas_fea.cad import rhino
from compas_fea.structure import ElasticPlastic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import ShellSection
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='block_strip', path='C:/Temp/')

# Extrude

rhino.mesh_extrude(mdl, guid=rs.ObjectsByLayer('base_mesh'), layers=5, thickness=0.010,
                   blocks_name='elset_blocks', plot_blocks=0)

# Elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_beams')
rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_membranes')

# Sets

ymin, ymax = mdl.node_bounds()[1]
top = [i for i, node in mdl.nodes.items() if node.y > ymax - 0.001]
bot = [i for i, node in mdl.nodes.items() if node.y < ymin + 0.001]
mdl.add_set(name='nset_top', type='node', selection=top)
mdl.add_set(name='nset_bot', type='node', selection=bot)

# Materials

MPa = 10**6
GPa = 10**9

mdl.add([
    ElasticPlastic(name='mat_1', E=100*GPa, v=0.3, p=1, f=[100*MPa, 100*MPa], e=[0, 1]),
    ElasticPlastic(name='mat_2', E=150*GPa, v=0.3, p=1, f=[150*MPa, 150*MPa], e=[0, 1]),
    ElasticPlastic(name='mat_3', E=200*GPa, v=0.3, p=1, f=[900*MPa, 900*MPa], e=[0, 1]),
])

# Sections

mdl.add([
    SolidSection(name='sec_solid'),
    ShellSection(name='sec_membrane', t=0.002),
    RectangularSection(name='sec_rectangle', b=0.002, h=0.002),
])

# Properties

rebar = {
    'top': {'pos': +0.001, 'spacing': 0.010, 'material': 'mat_3', 'dia': 0.002, 'angle': 0},
    'bot': {'pos': -0.001, 'spacing': 0.010, 'material': 'mat_3', 'dia': 0.002, 'angle': 90},
}

mdl.add([
    Properties(name='ep_solid_4', material='mat_2', section='sec_solid', elset='elset_blocks_layer_4'),
    Properties(name='ep_solid_3', material='mat_1', section='sec_solid', elset='elset_blocks_layer_3'),
    Properties(name='ep_solid_2', material='mat_2', section='sec_solid', elset='elset_blocks_layer_2'),
    Properties(name='ep_solid_1', material='mat_1', section='sec_solid', elset='elset_blocks_layer_1'),
    Properties(name='ep_solid_0', material='mat_2', section='sec_solid', elset='elset_blocks_layer_0'),
    Properties(name='ep_beams', material='mat_3', section='sec_rectangle', elset='elset_beams'),
    Properties(name='ep_membrane', material='mat_2', section='sec_membrane', elset='elset_membranes', rebar=rebar),
])

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_pinned', nodes='nset_bot'),
    RollerDisplacementY(name='disp_roller', nodes='nset_top'),
    GeneralDisplacement(name='disp_move', nodes='nset_top', y=0.010)
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned', 'disp_roller']),
    GeneralStep(name='step_move', displacements=['disp_move']),
])
mdl.steps_order = ['step_bc', 'step_move']

# Structure

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], components=['ux', 'uy', 'uz', 'smises'])

rhino.plot_data(mdl, step='step_move', field='smises', radius=0.002)
