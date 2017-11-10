"""An example compas_fea package use for meshes."""

from compas.datastructures.mesh.mesh import Mesh
from compas_rhino.helpers.mesh import mesh_from_guid

from compas_fea.cad import rhino

from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RollerDisplacementXY
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure
from compas_fea.structure import TributaryLoad
from compas_fea.structure import TrussSection

import rhinoscriptsyntax as rs


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Create empty Structure object

mdl = Structure(name='mesh_floor', path='C:/Temp/')

# Add truss and shell elements

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers=['elset_concrete'])
rhino.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers=['elset_ties'])

# Add node and element sets

layers = ['nset_corners', 'nset_corner1', 'nset_corner2', 'elset_ties', 'elset_concrete']
rhino.add_sets_from_layers(mdl, layers=layers)

# Add materials

mdl.add_materials([
    Concrete(name='mat_concrete', fck=90),
    Steel(name='mat_steel', fy=355)])

# Add sections

mdl.add_sections([
    ShellSection(name='sec_concrete', t=0.020),
    TrussSection(name='sec_ties', A=0.0004)])

# Add element properties

epc = Properties(material='mat_concrete', section='sec_concrete', elsets='elset_concrete')
eps = Properties(material='mat_steel', section='sec_ties', elsets='elset_ties')
mdl.add_element_properties(epc, name='ep_concrete')
mdl.add_element_properties(eps, name='ep_steel')

# Add loads

mdl.add_load(GravityLoad(name='load_gravity', elements='elset_concrete'))

# Add tributary loads from mesh

mesh = mesh_from_guid(Mesh(), rs.ObjectsByLayer('load_mesh')[0])
mdl.add_load(TributaryLoad(mdl, name='load_tributary', mesh=mesh, z=-2000))

# Add displacements

mdl.add_displacements([
    RollerDisplacementXY(name='disp_roller', nodes='nset_corners'),
    PinnedDisplacement(name='disp_pinned', nodes='nset_corner1'),
    GeneralDisplacement(name='disp_xdof', nodes='nset_corner2', x=0)])

# Add steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements=['disp_roller', 'disp_pinned', 'disp_xdof']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_tributary'], factor=1.5)])
mdl.steps_order = ['step_bc', 'step_loads']

# Structure summary

mdl.summary()

# Run and extract data

mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])

# Plot displacements

rhino.plot_data(mdl, step='step_loads', field='um', radius=0.02)

# Plot stress

rhino.plot_data(mdl, step='step_loads', field='smises', radius=0.02, cbar=[0, 4*10**6], nodal='max')
