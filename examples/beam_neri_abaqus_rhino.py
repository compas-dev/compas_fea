"""An example compas_fea package use for beams elements."""

from compas_fea.cad import rhino

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PipeSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


rs.EnableRedraw(False)

# Discretise curves

ds = 0.05
curves, lines = [], []
for i in range(2, 11):
    cid = 'curves-{0}'.format(i)
    lid = 'lines-{0}'.format(i)
    curves.append(cid)
    lines.append(lid)
    rs.CurrentLayer(lid)
    rs.DeleteObjects(rs.ObjectsByLayer(lid))
    guids = rs.ObjectsByLayer(cid)
    for curve in guids:
        n = int(rs.CurveLength(curve) / ds)
        for i in range(n):
            sp = rs.CurveArcLengthPoint(curve, (i + 0) * ds)
            ep = rs.CurveArcLengthPoint(curve, (i + 1) * ds)
            rs.AddLine(sp, ep)
        rs.AddLine(ep, rs.CurveEndPoint(curve))

# Create empty Structure object

mdl = Structure(name='beam_neri', path='C:/Temp/')

# Add beam elements

rhino.add_nodes_elements_from_layers(mdl, element_type='BeamElement', layers=lines)

# Add element sets

rhino.add_sets_from_layers(mdl, layers=lines)

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_asa', E=1.87*10**9, v=0.35, p=1050))

# Add sections

for i in range(2, 11):
    ri = i / 100.
    sname = 'sec_{0}'.format(i)
    ename = 'lines-{0}'.format(i)
    mdl.add_section(PipeSection(name=sname, r=ri, t=0.005))
    ep = ElementProperties(material='mat_asa', section=sname, elsets=[ename])
    mdl.add_element_properties(ep, name='ep_{0}'.format(i))

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

# Add displacements

rs.CurrentLayer('nset_pins')
rs.DeleteObjects(rs.ObjectsByLayer('nset_pins'))
for nkey, node in mdl.nodes.items():
    if node['z'] < 0.001:
        rs.AddPoint(mdl.node_xyz(nkey))
rhino.add_sets_from_layers(mdl, layers=['nset_pins'])
mdl.add_displacement(PinnedDisplacement(name='disp_pins', nodes='nset_pins'))

rs.EnableRedraw(True)

# Add steps

mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_pins']))
mdl.add_step(GeneralStep(name='step_load', loads=['load_gravity'], factor=1.2))
mdl.set_steps_order(['step_bc', 'step_load'])

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields={'U': 'all', 'S': 'all'})

# Plot displacements

rhino.plot_data(mdl, step='step_load', field='U', component='magnitude', radius=0.02)

# Plot stresses

rhino.plot_data(mdl, step='step_load', field='S', component='mises', radius=0.02, nodal='max')
