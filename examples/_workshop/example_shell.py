
from compas_fea.cad import rhino
from compas_fea.structure import Structure
from compas_fea.structure import Steel
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import GeneralStep
from compas_fea.structure import BucklingStep


# Author(s): Andrew Liew (github.com/andrewliew)


mdl = Structure(name='example_shell', path='C:/Temp/')

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='mesh')
rhino.add_sets_from_layers(mdl, layers='loads')
# tube, thickness, freeform, remove faces

supports = []
for key, node in mdl.nodes.items():
    if node.z < 0.01:
        supports.append(key)
#print(supports)

mdl.add_set(name='supports', type='node', selection=supports)
#print(mdl.sets['supports'])

mdl.add(Steel(name='material', fy=355))
#print(mdl.materials['material'])

mdl.add(ShellSection(name='section', t=0.050))
#print(mdl.sections['section'])

mdl.add(ElementProperties(name='ep', material='material', section='section', elset='mesh'))
#print(mdl.element_properties['ep'])

mdl.add(PinnedDisplacement(name='pinned', nodes='supports'))
#print(mdl.displacements['pinned'])

mdl.add([
    GravityLoad(name='gravity', elements='mesh'),
    PointLoad(name='loads', nodes='loads', z=-5000),
])
#print(mdl.loads['loads'])
#print(mdl.loads['gravity'])

mdl.add_steps([
    GeneralStep(name='bc', displacements='pinned'),
    GeneralStep(name='loads', loads=['gravity', 'loads'], factor=1.5),
    BucklingStep(name='buckling', modes=5, loads=['gravity', 'loads'], displacements='pinned'),
])
mdl.steps_order = ['bc', 'loads', 'buckling']
#print(mdl.steps['bc'])
#print(mdl.steps['loads'])
#print(mdl.steps['buckling'])

mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'rf', 'cf'])

rhino.plot_data(mdl, step='loads', field='um', scale=1)
rhino.plot_data(mdl, step='loads', field='smaxp')
rhino.plot_data(mdl, step='loads', field='sminp')

rhino.plot_reaction_forces(mdl, step='loads', scale=0.1)
rhino.plot_concentrated_forces(mdl, step='loads', scale=0.1)

rhino.plot_mode_shapes(mdl, step='buckling', layer='buckling-')

mdl.save_to_obj()
