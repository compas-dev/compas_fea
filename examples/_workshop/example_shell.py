
from compas_fea.cad import rhino
from compas_fea.structure import Structure
from compas_fea.structure import Concrete
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import GravityLoad
from compas_fea.structure import PointLoad
from compas_fea.structure import AreaLoad
from compas_fea.structure import GeneralStep
from compas_fea.structure import BucklingStep
from compas_fea.structure import ModalStep


# Author(s): Andrew Liew (github.com/andrewliew)


mdl = Structure(name='example_shell', path='C:/Temp/')

rhino.add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers='mesh')
rhino.add_sets_from_layers(mdl, layers=['loads', 'supports', 'area'])

#print(mdl.sets['loads'])
#print(mdl.sets['supports'])
#print(mdl.sets['area'])

mdl.add(Concrete(name='concrete', fck=50))

#print(mdl.materials['concrete'])

mdl.add(ShellSection(name='shell', t=0.100))

#print(mdl.sections['section'])

mdl.add(ElementProperties(name='ep', material='concrete', section='shell', elset='mesh'))

#print(mdl.element_properties['ep'])

mdl.add(PinnedDisplacement(name='pinned', nodes='supports'))

#print(mdl.displacements['pinned'])

mdl.add([
    GravityLoad(name='gravity', elements='mesh'),
    PointLoad(name='loads', nodes='loads', z=-1000),
    AreaLoad(name='pressure', elements='area', z=7000),
])

#print(mdl.loads['loads'])
#print(mdl.loads['gravity'])
#print(mdl.loads['pressure'])

mdl.add_steps([
    GeneralStep(name='bc', displacements='pinned'),
    GeneralStep(name='loads', loads=['gravity', 'loads', 'pressure'], factor=1.5),
    BucklingStep(name='buckling', modes=5, loads=['gravity', 'loads', 'pressure'], displacements='pinned'),
    ModalStep(name='modal', modes=5),
])
mdl.steps_order = ['bc', 'loads', 'buckling', 'modal']

#print(mdl.steps['bc'])
#print(mdl.steps['loads'])
#print(mdl.steps['buckling'])

#mdl.summary()

# Run

mdl.analyse_and_extract(software='abaqus', fields=['u', 's', 'rf', 'cf'])

rhino.plot_data(mdl, step='loads', field='um')
rhino.plot_data(mdl, step='loads', field='smaxp')
rhino.plot_data(mdl, step='loads', field='sminp')

rhino.plot_reaction_forces(mdl, step='loads', scale=0.1)
rhino.plot_concentrated_forces(mdl, step='loads', scale=0.1)

rhino.plot_mode_shapes(mdl, step='buckling', layer='buckling-')
rhino.plot_mode_shapes(mdl, step='modal', layer='modal-')

print(mdl.results['modal']['frequencies'])
print(mdl.results['modal']['masses'])

print(mdl.results['buckling']['info'])

mdl.save_to_obj()

# edit parameters and geometry
# load / show .inp and .odb files
# show in App
# show Blender example mesh_floor and mesh_discretise
# show example_tets in App
