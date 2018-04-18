
from compas_fea.cad import blender
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import PointLoad
from compas_fea.structure import Structure
from compas_fea.structure import TrussSection


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


# Structure

mdl = Structure(name='truss_tower', path='/home/al/temp/')

# Elements

blender.add_nodes_elements_from_layers(mdl, line_type='TrussElement', layers=[0])

# Sets

blender.add_elset_from_bmeshes(mdl, layer=0, name='elset_struts')
blender.add_nset_from_objects(mdl, layer=1, name='nset_pins')
blender.add_nset_from_objects(mdl, layer=2, name='nset_top')

# Materials

mdl.add_material(ElasticIsotropic(name='mat_elastic', E=200*10**9, v=0.3, p=7850))

# Sections

mdl.add_section(TrussSection(name='sec_truss', A=0.00010))

# Properties

ep = Properties(name='ep_strut', material='mat_elastic', section='sec_truss', elsets='elset_struts')
mdl.add_element_properties(ep)

# Displacements

mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Loads

mdl.add_load(PointLoad(name='load_top', nodes='nset_top', z=-100000))

# Steps

mdl.add_steps([
    GeneralStep(name='step_bc', displacements='disp_pinned'),
    GeneralStep(name='step_load', loads='load_top', nlmat=False)])
mdl.steps_order = ['step_bc', 'step_load']

# Summary

mdl.summary()

# Run (Abaqus)

exe = '/home/al/abaqus/Commands/abaqus cae '
mdl.analyse_and_extract(software='abaqus', exe=exe, fields=['u', 'rf', 's'])

blender.plot_data(mdl, step='step_load', field='um', layer=3)
print(mdl.get_nodal_results(step='step_load', field='um', nodes='nset_top'))

blender.plot_data(mdl, step='step_load', field='sxx', layer=4)
print(mdl.get_element_results(step='step_load', field='sxx', elements=[10]))

blender.plot_data(mdl, step='step_load', field='rfm', layer=5)
print(mdl.get_nodal_results(step='step_load', field='rfm', nodes='nset_pins'))
