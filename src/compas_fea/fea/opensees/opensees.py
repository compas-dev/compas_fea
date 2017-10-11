"""
compas_fea.fea.opensees : OpenSEES file creator.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Aryan Rezaei Rad <aryan.rezaeirad@epfl.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'inp_generate',
    'inp_write_heading',
    'inp_write_nodes',
    'inp_write_steps'
]


def inp_generate(structure, filename, units='m'):
    """ Creates the OpenSees input file from the Structure object.

    Parameters:
        structure (obj): The Structure object to read from.
        filename (str): Path to save the input file to.
        units (str): Units of the nodal co-ordinates 'm','cm','mm'.

    Returns:
        None
    """
    with open(filename, 'w') as f:

        # constraints = structure.constraints
        displacements = structure.displacements
        elements = structure.elements
        interactions = structure.interactions
        loads = structure.loads
        # materials = structure.materials
        misc = structure.misc
        nodes = structure.nodes
        # properties = structure.element_properties
        # sections = structure.sections
        # sets = structure.sets
        steps = structure.steps

        inp_write_heading(f)
        inp_write_nodes(f, nodes, units)
        # inp_write_elements(f, elements)
        inp_write_steps(f, structure, steps, loads, displacements, interactions, misc)

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))


def inp_write_heading(f):
    """ Creates the input file heading.

    Parameters:
        f (obj): The open file object for the input file.

    Returns:
        None
    """
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## --------------------------------------------------------------------- Heading\n')
    f.write('##\n')
    f.write('##                            OpenSees input file                               \n')
    f.write('##                          SI units: [N, m, kg, s]                             \n')
    f.write('##            compas_fea package: Dr Andrew Liew - liew@arch.ethz.ch            \n')
    f.write('##\n')
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('##\n')
    f.write('wipe;\n')
    f.write('model basic -ndm 3 -ndf 6;;\n')
    f.write('##\n')


def inp_write_nodes(f, nodes, units):
    """ Writes the nodal co-ordinates information to the OpenSees input file.

    Parameters:
        f (obj): The open file object for the input file.
        nodes (dic): Node dictionary from structure.nodes.
        units (str): Units of the nodal co-ordinates.

    Returns:
        None
    """
    cl = {'m': 1., 'cm': 0.01, 'mm': 0.001}
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## ----------------------------------------------------------------------- Nodes\n')
    f.write('##\n')
    f.write('## No., x[m], y[m], z[m]\n')
    f.write('##\n')
    for key in sorted(nodes, key=int):
        xyz = [str(nodes[key][i] * cl[units]) for i in 'xyz']
        f.write('node ' + ' '.join([str(key + 1)] + xyz) + ';\n')
    f.write('##\n')


def inp_write_steps(f, structure, steps, loads, displacements, interactions, misc):
    """ Writes step information to the OpenSees input file.

    Note:
        - Steps are analysed in the order given by structure.steps_order.

    Parameters:
        f (obj): The open file object for the input file.
        structure (obj): Struture object.
        steps (dic): Step objects from structure.steps.
        loads (dic): Load objects from structure.loads.
        displacements (dic): Displacement objects from structure.displacements.
        interactions (dic): Interaction objects from structure.interactions.
        misc (dic): Misc objects from structure.misc.

    Returns:
        None
    """
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## ----------------------------------------------------------------------- Steps\n')

    dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']

    for key in structure.steps_order:
        step = steps[key]
        stype = step.__name__
#         increments = step.increments
#         method = step.type
        f.write('##\n')
        f.write('## {0}\n'.format(key))
        f.write('## ' + '-' * len(key) + '\n')

        # Mechanical

        if stype in ['GeneralStep', 'BucklingStep']:

            # Displacements

            for k in step.displacements:
                displacement = displacements[k]
                com = displacement.components
                nset = displacement.nodes
                f.write('##\n')
                f.write('## {0}\n'.format(k))
                f.write('## ' + '-' * len(k) + '\n')
                f.write('##\n')
                f.write('## Node, x, y, z, xx, yy, zz\n')
                f.write('##\n')

                for node in structure.sets[nset]['selection']:
                    j = []
                    for dof in dofs:
                        if com[dof] is not None:
                            j.append('1')
                        else:
                            j.append('0')
                    f.write('fix {0} {1};\n'.format(node + 1, ' '.join(j)))

# equalDOF rigidDiaphragm rigidLink for tie constraints etc
