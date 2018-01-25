"""An example compas_fea package use for beams in a grid."""

# Note: Sliding at the nodes/joints is not included.

from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='beam_grid', path='C:/Temp/')

# Add beam elements

beams = [i for i in rs.LayerNames() if i[:2] in ['BX', 'BY']]
for beam in beams:
    network = rhino.network_from_lines(rs.ObjectsByLayer(beam))
    mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement')
    sp, ep = network.leaves()
    sp_xyz = network.vertex_coordinates(sp)
    ep_xyz = network.vertex_coordinates(ep)
    mdl.add_set('{0}_sp'.format(beam), 'node', [mdl.check_node_exists(sp_xyz)])
    mdl.add_set('{0}_ep'.format(beam), 'node', [mdl.check_node_exists(ep_xyz)])

# Add node and element sets

rhino.add_sets_from_layers(mdl, layers=['lift_points'] + beams)

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=5*10**9, v=0.3, p=1000))

# Add sections

mdl.add_section(RectangularSection(name='sec_rectangular', h=0.005, b=0.005))
for beam in beams:
    name = 'ep_{0}'.format(beam)
    ep = Properties(name=name, material='mat_elastic', section='sec_rectangular', elsets=beam)
    mdl.add_element_properties(ep)

# Add displacements

bc = []
for beam in beams:
    sp = '{0}_sp'.format(beam)
    ep = '{0}_ep'.format(beam)
    if 'X' in beam:
        mdl.add_displacements([
            RollerDisplacementX(name=sp, nodes=sp),
            RollerDisplacementX(name=ep, nodes=ep)])
    if 'Y' in beam:
        mdl.add_displacements([
            RollerDisplacementY(name=sp, nodes=sp),
            RollerDisplacementY(name=ep, nodes=ep)])
    bc.extend([sp, ep])
mdl.add_displacement(GeneralDisplacement(name='disp_lift', nodes='lift_points', z=0.250))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=bc),
    GeneralStep(name='step_lift', displacements=['disp_lift'])])
mdl.steps_order = ['step_bc', 'step_lift']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 'sf', 'sm'])

# Plot displacements

rhino.plot_data(mdl, step='step_lift', field='um', radius=0.005, colorbar_size=0.3)

# Plot section forces/moments

rhino.plot_data(mdl, step='step_lift', field='sfnx', radius=0.005, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_lift', field='sfvy', radius=0.005, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_lift', field='smy', radius=0.005, colorbar_size=0.3)
