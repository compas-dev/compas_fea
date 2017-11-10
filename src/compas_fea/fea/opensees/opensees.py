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
    'input_generate',
    'input_write_heading',
    'input_write_nodes',
    'input_write_steps',
    'input_write_elements'
]


def input_generate(structure, fields, units='m'):
    """ Creates the OpenSees .tcl file from the Structure object.

    Parameters:
        structure (obj): The Structure object to read from.
        fields (list): Data field requests.
        units (str): Units of the nodal co-ordinates 'm','cm','mm'.

    Returns:
        None
    """
    filename = '{0}{1}.tcl'.format(structure.path, structure.name)

    with open(filename, 'w') as f:

        constraints = structure.constraints
        displacements = structure.displacements
        elements = structure.elements
        interactions = structure.interactions
        loads = structure.loads
        materials = structure.materials
        misc = structure.misc
        nodes = structure.nodes
        properties = structure.element_properties
        sections = structure.sections
        sets = structure.sets
        steps = structure.steps

        input_write_heading(f)
        input_write_nodes(f, nodes, units)
        input_write_steps(f, structure, steps, loads, displacements, interactions, misc)
        input_write_elements(f, sections, properties, elements, sets, materials)

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))


def input_write_heading(f):
    """ Creates the OpenSees .tcl file heading.

    Parameters:
        f (obj): The open file object for the .tcl file.

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


def input_write_nodes(f, nodes, units):
    """ Writes the nodal co-ordinates information to the OpenSees .tcl file.

    Parameters:
        f (obj): The open file object for the .tcl file.
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


def input_write_steps(f, structure, steps, loads, displacements, interactions, misc):
    """ Writes step information to the OpenSees .tcl file.

    Note:
        - Steps are analysed in the order given by structure.steps_order.
        - The first Step should be the boundary conditions.

    Parameters:
        f (obj): The open file object for the .tcl file.
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
        # increments = step.increments
        # method = step.type
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


def input_write_elements(f, sections, properties, elements, sets, materials):
    """ Writes the element and section information to the OpenSees .tcl file.

    Parameters:
        f (obj): The open file object for the .tcl file.
        sections (dic): Section objects from structure.sections.
        properties (dic): ElementProperties objects from structure.element_properties.
        elements (dic): Element objects from structure.elements.
        sets (dic): Sets from structure.sets.
        materials (dic): Material objects from structure.materials.

    Returns:
        None
    """

    # Sections:

    shells = ['ShellSection']
    solids = ['SolidSection', 'TrussSection']

    # Write data

    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## -------------------------------------------------------------------- Elements\n')

    f.write('##\n')
    f.write('geomTransf Linear 1\n')

    for key, property in properties.items():
        material = property.material
        elsets = property.elsets
        # reinforcement = property.reinforcement
        section = sections[property.section]
        stype = section.__name__
        geometry = section.geometry

        f.write('##\n')
        f.write('## Section: {0}\n'.format(key))
        f.write('## ---------' + '-' * (len(key)) + '\n')
        f.write('##\n')

        if isinstance(elsets, str):
            elsets = [elsets]

        for elset in elsets:
            selection = sets[elset]['selection']

            # Beam sections

            if (stype not in shells) and (stype not in solids):

                f.write('## eType, No., node.start, node.end, A[m2], E[Pa], G[Pa], J[m^4], Iyy[m^4], Ixx[m^4], trans\n')
                for select in selection:
                    sp, ep = elements[select].nodes
                    n = select + 1
                    i = sp + 1
                    j = ep + 1
                    A = geometry['A']
                    E = materials[material].E['E']
                    G = materials[material].G['G']
                    J = geometry['J']
                    Ixx = geometry['Ixx']
                    Iyy = geometry['Iyy']
                    f.write('element elasticBeamColumn {0} {1} {2} {3} {4} {5} {6} {7} {8} 1\n'.format(n, i, j, A, E, G, J, Ixx, Iyy))
