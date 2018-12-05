import compas_fea

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import RectangularSection
from compas_fea.structure import PointLoad
from compas_fea.structure import Steel
from compas_fea.structure import Structure


__author__      = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__   = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__     = 'MIT License'
__email__       = 'mendez@arch.ethz.ch'


# Structure

mdl = Structure(name='beam_bench', path=compas_fea.TEMP)

# Nodes and Elements

xyz = [[0, 0, 0], [1, 0, 0]]
nodes = mdl.add_nodes(xyz)
beam = mdl.add_element(nodes, 'BeamElement', axes={'ex':[0, 1, 0]})

# Sets

elset_beams = mdl.add_set('elset_beams', 'element', [beam])

# Materials

mdl.add(Steel(name='mat_steel'))

# Sections

mdl.add(RectangularSection(name='sec_pipe', b=0.005, h=0.05))

# Properties

mdl.add(Properties(name='ep_beam', material='mat_steel', section='sec_pipe', elsets='elset_beams'))

# Displacements

mdl.add(FixedDisplacement(name='disp_pins', nodes=[0]))

# Loads

mdl.add(PointLoad(name='load_v', nodes=[1], z=-1000))

# Steps

mdl.add(GeneralStep(name='step_bc_loads', displacements=['disp_pins'], loads=['load_v']))
mdl.steps_order = ['step_bc_loads']

# Summary

# mdl.summary()

# Run (Abaqus)

# mdl.analyse_and_extract(software='abaqus', fields=['u', 'rf'], license='research')

# Run (Ansys)

mdl.analyse_and_extract(software='ansys', fields=['sf'], license='research')

# print(mdl.get_nodal_results(step='step_loads', field='rfm', nodes='nset_pins'))
