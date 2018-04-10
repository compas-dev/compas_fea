
from compas_fea.cad import rhino
from compas_fea.structure import CircularSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure

from compas_rhino.utilities import clear_layers

from math import pi

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='beam_simple', path='C:/Temp/')

# Clear

clear_layers(['elset_lines', 'nset_left', 'nset_right', 'nset_weights'])
rs.EnableRedraw(False)

# Lines

L = 1.0
m = 100
x = [i * L / m for i in range(m + 1)]
rs.CurrentLayer('elset_lines')
[rs.AddLine([x[i], 0, 0], [x[i + 1], 0, 0]) for i in range(m)]

# Points

n = 5
rs.CurrentLayer('nset_left')
rs.AddPoint([0, 0, 0])
rs.CurrentLayer('nset_right')
rs.AddPoint([L, 0, 0])
rs.CurrentLayer('nset_weights')
for xi in x[n::n]:
    rs.AddPoint([xi, 0, 0])

rs.EnableRedraw(True)

# Elements

network = rhino.network_from_lines(layer='elset_lines')
mdl.add_nodes_elements_from_network(network=network, element_type='BeamElement', 
                                    elset='elset_lines', axes={'ex': [0, -1, 0]})

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_left', 'nset_right', 'nset_weights'])

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=20*10**9, v=0.3, p=1500))

# Sections

_, ekeys, L, Lt = rhino.ordered_network(mdl, network=network, layer='nset_left')
for ekey, Li in zip(ekeys, L):
    ri = (1 + Li / Lt) * 0.020
    sname = 'sec_{0}'.format(ekey)
    pname = 'ep_{0}'.format(ekey)
    ename = 'element_{0}'.format(ekey)
    mdl.add_section(CircularSection(name=sname, r=ri))
    ep = Properties(name=pname, material='mat_elastic', section=sname, elsets=ename)
    mdl.add_element_properties(ep)

# Displacements

deg = pi / 180
mdl.add_displacements([
    PinnedDisplacement(name='disp_bc_left', nodes='nset_left'),
    GeneralDisplacement(name='disp_bc_right', nodes='nset_right', y=0, z=0, xx=0),
    GeneralDisplacement(name='disp_left', nodes='nset_left', yy=30*deg),
])

# Loads

mdl.add_load(PointLoad(name='load_weights', nodes='nset_weights', z=-200.0))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_bc_left', 'disp_bc_right']),
    GeneralStep(name='step_load', loads=['load_weights'], displacements=['disp_left'])])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Sofistik)

mdl.write_input_file(software='sofistik')

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 'ur', 'sf', 'sm'])

rhino.plot_data(mdl, step='step_load', field='um', radius=0.01, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_load', field='ury', radius=0.01, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_load', field='sfnx', radius=0.01, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_load', field='sfvy', radius=0.01, colorbar_size=0.3)
rhino.plot_data(mdl, step='step_load', field='smx', radius=0.01, colorbar_size=0.3)

# Run (OpenSees)
# Note: 'u' and 'ur' fields are returned and plotable, 'sf' currently is not.

mdl.analyse_and_extract(software='opensees', fields=['u', 'ur', 'sf'])
