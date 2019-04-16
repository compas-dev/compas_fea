import compas_fea

from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import PointLoad
from compas_fea.structure import Steel
from compas_fea.structure import Structure


__author__      = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__   = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__     = 'MIT License'
__email__       = 'mendez@arch.ethz.ch'


# Structure

mdl = Structure(name='shell_bench', path=compas_fea.TEMP)

# Nodes and Elements

xyz = [[0, 0, 0], [1, 0, 0], [2, 0, 0],
       [0, 1, 0], [1, 1, 0], [2, 1, 0],
       [0, 2, 0], [1, 2, 0], [2, 2, 0]]

nodes = mdl.add_nodes(xyz)
shells = [[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]]

shells = [mdl.add_element(shell, 'ShellElement') for shell in shells]

# Sets

elset_shells = mdl.add_set('elset_shells', 'element', shells)

# Materials

mdl.add(Steel(name='mat_steel'))

# Sections

mdl.add(ShellSection(name='sec_shell', t=0.01))

# Properties

mdl.add(Properties(name='ep_shell', material='mat_steel', section='sec_shell', elset='elset_shells'))

# Displacements

mdl.add(FixedDisplacement(name='disp_pins', nodes=[0, 2, 8 , 6]))

# Loads

mdl.add(PointLoad(name='load_v', nodes=[4], z=-1000))

# Steps

mdl.add(GeneralStep(name='step_bc_loads', displacements=['disp_pins'], loads=['load_v'], nlgeom=False))
mdl.steps_order = ['step_bc_loads']

# Summary

# mdl.summary()

# Run (Abaqus)

# mdl.analyse_and_extract(software='abaqus', fields=['u', 'rf'], license='research')

# Run (Ansys)

mdl.analyse_and_extract(software='ansys', fields=['u'], license='research')

print(mdl.get_nodal_results(step='step_bc_loads', field='um', nodes=[3, 4, 5]))
