
# Note: Sliding at the nodes/joints is not included.

from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import RectangularSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='beam_grid', path='C:/Temp/')

# Beams

beams = [i for i in rs.LayerNames() if i[:2] in ['BX', 'BY']]
for beam in beams:
    network = rhino.network_from_lines(rs.ObjectsByLayer(beam))
    axes = {'ex': [0, 1, 0]} if 'X' in beam else {'ex': [1, 0, 0]}
    mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement', 
                                        elset=beam, axes=axes)
    xyzs = [network.vertex_coordinates(i) for i in network.leaves()]
    ends = [mdl.check_node_exists(i) for i in xyzs]
    mdl.add_set('{0}_ends'.format(beam), type='node', selection=ends)

# Sets

rhino.add_sets_from_layers(mdl, layers=['lift_points'] + beams)

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=5*10**9, v=0.3, p=1000))

# Sections

mdl.add_section(RectangularSection(name='sec_rectangular', h=0.005, b=0.005))

# Properties

ep = Properties(name='ep', material='mat_elastic', section='sec_rectangular', elsets=beams)
mdl.add_element_properties(ep)

# Displacements

bc = []
for beam in beams:
    name = '{0}_ends'.format(beam)
    if 'X' in beam:
        mdl.add_displacement(GeneralDisplacement(name=name, nodes=name, y=0, z=0, xx=0))
    if 'Y' in beam:
        mdl.add_displacement(GeneralDisplacement(name=name, nodes=name, x=0, z=0, yy=0))
    bc.append(name)
mdl.add_displacement(GeneralDisplacement(name='disp_lift', nodes='lift_points', z=0.250))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=bc),
    GeneralStep(name='step_lift', displacements=['disp_lift'])])
mdl.steps_order = ['step_bc', 'step_lift']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 'sf', 'sm'])

rhino.plot_data(mdl, step='step_lift', field='um', radius=0.005, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_lift', field='sfnx', radius=0.005, colorbar_size=0.3)
