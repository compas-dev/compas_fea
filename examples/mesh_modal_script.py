
from compas.datastructures import Mesh

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import ModalStep
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure

import compas


# Author(s): Andrew Liew (github.com/andrewliew)


# Structure

mdl = Structure(path='C:/Temp/', name='mesh_modal')

# Elements

mesh = Mesh.from_obj(compas.get('quadmesh.obj'))
mdl.add_nodes_elements_from_mesh(mesh=mesh, element_type='ShellElement', elset='elset_concrete')

# Sets

nodes = [i for i, node in mdl.nodes.items() if node.z < 0.01]
mdl.add_set(name='nset_pins', type='node', selection=nodes)

# Materials

mdl.add(ElasticIsotropic(name='mat_concrete', E=40*10**9, v=0.2, p=2400))

# Sections

mdl.add(ShellSection(name='sec_concrete', t=0.050))

# Properties

mdl.add(Properties(name='ep_concrete', material='mat_concrete', section='sec_concrete', elset='elset_concrete'))

# Displacements

mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_pins'))

# Steps

mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    ModalStep(name='step_modal', modes=5),
])
mdl.steps_order = ['step_bc', 'step_modal']

# Summary

mdl.summary()

# Run

mdl.analyse_and_extract(software='opensees', fields=['u'])

print(mdl.results['step_modal']['frequencies'])

mdl.save_to_obj()

mdl.view(mode='1')  # temp hack
