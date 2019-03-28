
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import SolidSection
from compas_fea.structure import Structure

import rhinoscriptsyntax as rs


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='block_tets', path='C:/Temp/')

# Tetrahedrons

mesh = rs.ObjectsByLayer('base_mesh')[0]
rhino.add_tets_from_mesh(mdl, name='elset_tets', mesh=mesh, volume=10**(-4))

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_base', 'nset_top'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1))

# Sections

mdl.add(SolidSection(name='sec_solid'))

# Properties

mdl.add(Properties(name='ep_tets', material='mat_elastic', section='sec_solid', elset='elset_tets'))

# Displacementss

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))

# Loads

mdl.add(PointLoad(name='load_top', nodes='nset_top', y=100, z=100))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_top']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u'])

rhino.plot_data(mdl, step='step_load', field='um')
#rhino.plot_voxels(mdl, step='step_load', field='um', vdx=0.05)
