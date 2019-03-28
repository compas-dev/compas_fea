
from compas_fea.cad import rhino
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElasticPlastic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import RectangularSection
from compas_fea.structure import RollerDisplacementZ
from compas_fea.structure import Structure
from compas_fea.structure import TrapezoidalSection


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(name='beam_tree', path='C:/Temp/')

# Elements

layers = ['struts_mushroom', 'struts_bamboo', 'joints_mushroom', 'joints_bamboo', 'joints_grid']
rhino.add_nodes_elements_from_layers(mdl, line_type='BeamElement', layers=layers)

# Sets

rhino.add_sets_from_layers(mdl, layers=['supports_bot', 'supports_top'])

# Sections

mdl.add([
    TrapezoidalSection(name='sec_mushroom', b1=0.001, b2=0.150, h=0.225),
    RectangularSection(name='sec_bamboo', b=0.020, h=0.100),
    RectangularSection(name='sec_joints', b=0.020, h=0.075),
])

# Materials

fm = [i * 1000000 for i in [5, 9, 12, 14, 16, 18, 19, 20, 21, 22]]
em = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

mdl.add([
    ElasticIsotropic(name='mat_bamboo', E=20*10**9, v=0.35, p=1100),
    ElasticPlastic(name='mat_mushroom', E=5*10**6, v=0.30, p=350, f=fm, e=em),
])

# Properties

mdl.add([
    Properties(name='ep_mush_1', material='mat_mushroom', section='sec_mushroom', elset='struts_mushroom'),
    Properties(name='ep_mush_2', material='mat_mushroom', section='sec_mushroom', elset='joints_mushroom'),
    Properties(name='ep_bamb_1', material='mat_bamboo', section='sec_bamboo', elset='struts_bamboo'),
    Properties(name='ep_bamb_2', material='mat_bamboo', section='sec_bamboo', elset='joints_bamboo'),
    Properties(name='ep_joints', material='mat_bamboo', section='sec_joints', elset='joints_grid'),
])

# Displacements

mdl.add([
    PinnedDisplacement(name='disp_bot', nodes='supports_bot'),
    RollerDisplacementZ(name='disp_top', nodes='supports_top'),
])

# Loads

mdl.add(GravityLoad(name='load_gravity', elements=layers))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_bot', 'disp_top']),
    GeneralStep(name='step_loads', loads=['load_gravity']),
])
mdl.steps_order = ['step_bc', 'step_loads']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 'sf', 'rf'])

rhino.plot_data(mdl, step='step_loads', field='um', radius=0.05, cbar_size=0.5)
rhino.plot_data(mdl, step='step_loads', field='sf1', radius=0.05, cbar_size=0.5)
rhino.plot_reaction_forces(mdl, step='step_loads')
