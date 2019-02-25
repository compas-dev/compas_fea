
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

mdl = Structure(name='block_deepbeam', path='C:/Temp/')

# Extrude

nz = 20
rhino.mesh_extrude(mdl, guid=rs.ObjectsByLayer('base_mesh'), layers=nz, thickness=1./nz,
                   blocks_name='elset_blocks')

# Sets

rhino.add_sets_from_layers(mdl, layers=['nset_load', 'nset_supports'])

# Materials

mdl.add(ElasticIsotropic(name='mat_elastic', E=10**(10), v=0.3, p=1))

# Sections

mdl.add(SolidSection(name='sec_solid'))

# Properties

mdl.add(Properties(name='ep_solid', material='mat_elastic', section='sec_solid', elset='elset_blocks'))

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_supports'))

# Loads

mdl.add(PointLoad(name='load_point', nodes='nset_load', z=-1))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_load', loads=['load_point']),
])
mdl.steps_order = ['step_bc', 'step_load']

# Structure

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], components=['ux', 'uy', 'uz', 'smises'])

rhino.plot_data(mdl, step='step_load', field='smises', cbar=[0, 2])
rhino.plot_voxels(mdl, step='step_load', field='smises', cbar=[0, 2], vdx=1./nz)
