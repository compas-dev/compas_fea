
from compas_fea.cad import blender
from compas_fea.structure import Concrete
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import ShellSection
from compas_fea.structure import Steel
from compas_fea.structure import Structure


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='mesh_mould', path='C:/Temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, layers=['elset_wall', 'elset_plinth'], mesh_type='ShellElement')

# Sets

blender.add_nsets_from_layers(mdl, layers='nset_loads')
blender.add_nset_from_meshes(mdl, layer='nset_fixed')

# Materials

mdl.add([
    Concrete(name='mat_concrete', fck=40),
    Steel(name='mat_rebar', fy=500),
])

# Sections

mdl.add([
    ShellSection(name='sec_wall', t=0.150),
    ShellSection(name='sec_plinth', t=0.300),
])

# Properties

rplinth = {
    'p_u1': {'pos': +0.130, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 0},
    'p_u2': {'pos': +0.120, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 90},
    'p_l2': {'pos': -0.120, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 90},
    'p_l1': {'pos': -0.130, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 0},
}
rwall = {
    'w_u1': {'pos': +0.055, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 0},
    'w_u2': {'pos': +0.045, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 90},
    'w_l2': {'pos': -0.045, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 90},
    'w_l1': {'pos': -0.055, 'spacing': 0.100, 'material': 'mat_rebar', 'dia': 0.012, 'angle': 0},
}

mdl.add([
    Properties(name='ep_plinth', material='mat_concrete', section='sec_plinth', elset='elset_plinth', rebar=rplinth),
    Properties(name='ep_wall', material='mat_concrete', section='sec_wall', elset='elset_wall', rebar=rwall),
])

# Displacements

mdl.add(FixedDisplacement(name='disp_fixed', nodes='nset_fixed'))

# Loads

mdl.add([
    GravityLoad(name='load_gravity', elements=['elset_wall', 'elset_plinth']),
    PointLoad(name='load_points', nodes='nset_loads', z=-20*10**3),
])

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_fixed']),
    GeneralStep(name='step_loads', loads=['load_gravity', 'load_points']),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'sf', 'rbfor', 'rf', 'cf'])

# blender.plot_data(mdl, step='step_loads', field='um', cbar_size=0.5)
# blender.plot_data(mdl, step='step_loads', field='sf1', cbar_size=0.5)
# blender.plot_data(mdl, step='step_loads', field='sf2', cbar_size=0.5)
# blender.plot_data(mdl, step='step_loads', field='rbfor', iptype='max', nodal='max', cbar_size=0.5)
# blender.plot_reaction_forces(mdl, step='step_loads', scale=0.2)
# blender.plot_concentrated_forces(mdl, step='step_loads', scale=0.2)
