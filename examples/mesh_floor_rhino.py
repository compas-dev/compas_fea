
from compas.datastructures.mesh.mesh import Mesh
from compas_rhino.helpers.mesh import mesh_from_guid

from compas_fea.cad import rhino
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PrestressLoad
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection

import rhinoscriptsyntax as rs


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure 

mdl = Structure(name='mesh_floor', path='C:/Temp/')

# Elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='elset_concrete')
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers='elset_ties')

# Sets

layers = ['nset_corners', 'nset_corner1', 'nset_corner2']
rhino.add_sets_from_layers(mdl, layers=layers)

# Materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355)])

# Sections

mdl.add_sections([
    ShellSection(name='sec_concrete', t=0.020),
    TrussSection(name='sec_ties', A=0.0004)])

# Properties

mdl.add_element_properties([
    Properties(name='ep_concrete', material='mat_concrete', section='sec_concrete', elsets='elset_concrete'),
    Properties(name='ep_steel', material='mat_steel', section='sec_ties', elsets='elset_ties')])

# Displacements

mdl.add_displacements([
    RollerDisplacementXY(name='disp_roller', nodes='nset_corners'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'),
    GeneralDisplacement(name='disp_xdof', nodes='nset_corner2', x=0)])
    
# Loads

mesh = mesh_from_guid(Mesh(), rs.ObjectsByLayer('load_mesh')[0])
mdl.add_loads([
    GravityLoad(name='load_gravity', elements='elset_concrete'),
    PrestressLoad(name='load_prestress', elements='elset_ties', sxx=50*10**6),
    TributaryLoad(mdl, name='load_tributary', mesh=mesh, z=-2000)])

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_roller', 'disp_pinned', 'disp_xdof']),
    GeneralStep(name='step_prestress', loads=['load_prestress']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_tributary'], factor=1.1)])
mdl.steps_order = ['step_bc', 'step_prestress', 'step_loads']

# Summary

mdl.summary()

# Run (Abaqus)

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

rhino.plot_data(mdl, step='step_prestress', field='uz', radius=0.02, colorbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='uz', radius=0.02, colorbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='smises', radius=0.02, colorbar_size=0.5,
                cbar=[0, 3*10**6], nodal='max', iptype='max')
