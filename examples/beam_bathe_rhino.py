"""An example compas_fea package use for beams."""

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

import rhinoscriptsyntax as rs
import json


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Note: this example is in inches and pounds, ignore any SI unit comments in input files.

# Create empty Structure object

mdl = Structure(name='beam_bathe', path='C:/Temp/')

# Local axis ex

for line in rs.ObjectsByLayer('elset_lines'):
    ez = subtract_vectors(rs.CurveStartPoint(line), rs.CurveEndPoint(line))
    ex = normalize_vector(cross_vectors(ez, [0, 0, 1]))
    rs.ObjectName(line, json.dumps({'ex': ex}))

# Add nodes and elements

rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers='elset_lines')

# Add sets

rhino.add_sets_from_layers(mdl, layers=['nset_support', 'nset_load'])
rhino.add_sets_from_layers(mdl, layers='elset_lines')

# Add materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10**7, v=10**(-5), p=1))

# Add sections

mdl.add_section(RectangularSection(name='sec_rectangular', b=1, h=1))

# Add element properties

ep = Properties(name='ep', material='mat_elastic', section='sec_rectangular', elsets='elset_lines')
mdl.add_element_properties(ep)

# Add displacements

mdl.add_displacement(FixedDisplacement(name='disp_fixed', nodes='nset_support'))

# Add loads

mdl.add_load(PointLoad(name='load_vertical', nodes='nset_load', z=600))

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_fixed']),
    GeneralStep(name='step_load', loads=['load_vertical'])])
mdl.steps_order = ['step_bc', 'step_load']

# Structure summary

mdl.summary()

# Run and extract data

#mdl.analyse_and_extract(software='abaqus', fields=['u'])
mdl.analyse_and_extract(software='opensees', fields=['u'])

# Plot

rhino.plot_data(mdl, step='step_load', field='uz', radius=1)
