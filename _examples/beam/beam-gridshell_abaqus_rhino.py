"""An example compas_fea package use for beams in a gridshell."""

# Note: Sliding at the joints is not included.

from compas_fea.fea.abaq import abaq
from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementX
from compas_fea.structure import RollerDisplacementY
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


name = 'beam-gridshell'
path = 'C:/Temp/'

# Create empty Structure object

mdl = Structure()

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
    ep = ElementProperties(material='mat_elastic', section='sec_rectangular', elsets=beam)
    mdl.add_element_properties(ep, 'ep_{0}'.format(beam))

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

# Add displacements

bc = []
for beam in beams:
    sp_nset = '{0}_sp'.format(beam)
    ep_nset = '{0}_ep'.format(beam)
    if 'X' in beam:
        mdl.add_displacement(RollerDisplacementX(name=sp_nset, nodes=sp_nset))
        mdl.add_displacement(RollerDisplacementX(name=ep_nset, nodes=ep_nset))
    if 'Y' in beam:
        mdl.add_displacement(RollerDisplacementY(name=sp_nset, nodes=sp_nset))
        mdl.add_displacement(RollerDisplacementY(name=ep_nset, nodes=ep_nset))
    bc.extend([sp_nset, ep_nset])
mdl.add_displacement(GeneralDisplacement(name='disp_lift', nodes='lift_points', z=0.270))

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=bc))
mdl.add_step(GeneralStep(name='step_lift', displacements=['disp_lift']))
mdl.set_steps_order(['step_bc', 'step_lift'])

# Structure summary

mdl.summary()

# Generate .inp file

abaq.inp_generate(mdl, filename='{0}{1}.inp'.format(path, name))

# Run and extract data

mdl.analyse(path=path, name=name, software='abaqus', fields='U,SF,SM')

# Plot displacements

rhino.plot_data(mdl, path, name, step='step_lift', field='U', component='magnitude', radius=0.005)

# Plot section forces/moments

rhino.plot_data(mdl, path, name, step='step_lift', field='SF', component='SF1', radius=0.005)
rhino.plot_data(mdl, path, name, step='step_lift', field='SF', component='SF3', radius=0.005)
rhino.plot_data(mdl, path, name, step='step_lift', field='SM', component='SM2', radius=0.005)
