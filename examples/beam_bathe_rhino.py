import json
import rhinoscriptsyntax as rs

from compas.geometry import cross_vectors
from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors

from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas_fea.structure import RectangularSection
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Local ex

for i in rs.ObjectsByLayer('elset_beams'):
    ez = subtract_vectors(rs.CurveEndPoint(i), rs.CurveStartPoint(i))
    ex = normalize_vector(cross_vectors(ez, [0, 0, 1]))
    rs.ObjectName(i, '_{0}'.format(json.dumps({'ex': ex})))

# Structure

mdl = Structure(name='beam_bathe', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_beams')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_support', 'nset_load'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10**7, v=10**(-5), p=1))

# Sections

mdl.add(RectangularSection(name='sec_beam', b=1, h=1))

# Properties

mdl.add(Properties(name='ep_beam', material='mat_elastic', section='sec_beam', elset='elset_beams'))

# Displacements

mdl.add(FixedDisplacement(name='disp_fixed', nodes='nset_support'))

# Loads

mdl.add(PointLoad(name='load_point', nodes='nset_load', z=600))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_fixed']),
    GeneralStep(name='step_load', loads=['load_point']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 'sf', 'sm'])

rhino.plot_data(mdl, step='step_load', field='uz', radius=1)

print(mdl.get_nodal_results(step='step_load', field='uz', nodes='nset_load'))
