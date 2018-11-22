
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'BCs',
]

dofs    = ['x',  'y',  'z',  'xx', 'yy', 'zz']
fixitys = ['PX', 'PY', 'PZ', 'MX', 'MY', 'MZ']


class BCs(object):

    def __init__(self):

        pass


    def write_boundary_conditions(self):

        self.write_section('Boundary conditions')
        self.blank_line()

        sets          = self.structure.sets
        steps         = self.structure.steps
        displacements = self.structure.displacements

        try:

            step = steps[self.structure.steps_order[0]]

            if isinstance(step.displacements, str):
                step.displacements = [step.displacements]

            for key in step.displacements:

                nodes      = displacements[key].nodes
                components = displacements[key].components
                nset       = nodes if isinstance(nodes, str) else None
                selection  = sets[nset].selection if isinstance(nodes, str) else nodes

                self.write_subsection(key)

                # ----------------------------------------------------------------------------
                # OpenSees
                # ----------------------------------------------------------------------------

                if self.software == 'opensees':

                    entry = ['1' if components[dof] is not None else '0' for dof in dofs[:self.ndof]]

                    for node in sorted(selection, key=int):
                        self.write_line('fix {0} {1}'.format(node + 1, ' '.join(entry)))

                # ----------------------------------------------------------------------------
                # Sofistik
                # ----------------------------------------------------------------------------

                elif self.software == 'sofistik':

                    self.write_line('NODE NO FIX')
                    self.blank_line()

                    entry = [fixity for dof, fixity in zip(dofs, fixitys) if components[dof] == 0]

                    for node in sorted(selection, key=int):
                        self.write_line('{0} {1}'.format(node + 1, ' '.join(entry)))

                # ----------------------------------------------------------------------------
                # Abaqus
                # ----------------------------------------------------------------------------

                elif self.software == 'abaqus':

                    self.write_line('*BOUNDARY')
                    self.blank_line()

                    for c, dof in enumerate(dofs, 1):
                        if components[dof] is not None:
                            if nset:
                                self.write_line('{0}, {1}, {1}, {2}'.format(nset, c, components[dof]))
                            else:
                                for node in sorted(selection, key=int):
                                    self.write_line('{0}, {1}, {1}, {2}'.format(node + 1, c, components[dof]))

                # ----------------------------------------------------------------------------
                # Ansys
                # ----------------------------------------------------------------------------

                elif self.software == 'ansys':

                    pass

        except:

            print('***** Error writing boundary conditions, check Step exists in structure.steps_order[0] *****')

        self.blank_line()
        self.blank_line()
