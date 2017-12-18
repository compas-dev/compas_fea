"""
compas_fea.fea.sofistik : Sofistik specific functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
    'input_write_heading',
    'input_write_materials',
    'input_write_nodes_elements',
]


def input_generate(structure, fields, units='m'):
    """ Creates the Sofistik .dat file from the Structure object.

    Parameters:
        structure (obj): The Structure object to read from.
        fields (list): Data field requests.
        units (str): Units of the nodal co-ordinates 'm','cm','mm'.

    Returns:
        None
    """
    filename = '{0}{1}.dat'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

    with open(filename, 'w') as f:

        elements = structure.elements
        materials = structure.materials
        nodes = structure.nodes
        properties = structure.element_properties
        sections = structure.sections
        sets = structure.sets

        input_write_heading(f)
        input_write_materials(f, materials)
        input_write_nodes_elements(f, nodes, elements, sections, properties, materials, sets, units)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))


def input_write_heading(f):
    """ Creates the Sofistik .dat file heading.

    Parameters:
        f (obj): The open file object for the .dat file.

    Returns:
        None
    """
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ --------------------------------------------------------------------- Heading\n')
    f.write('$\n')
    f.write('$                           Sofistik input file                                \n')
    f.write('$                          SI units: [kN, m, kg, s]                             \n')
    f.write('$            compas_fea package: Dr Andrew Liew - liew@arch.ethz.ch            \n')
    f.write('$\n')
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('\n')
    f.write('\n')

    f.write('$ UNITS ARE IN kN FOR FORCE!!\n')


def input_write_materials(f, materials):
    """ Writes materials to the Sofistik .dat file.

    Parameters:
        f (obj): The open file object for the .dat file.
        materials (dic): Material objects from structure.materials.

    Returns:
        None
    """
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ------------------------------------------------------------------- Materials\n')
    f.write('\n')
    f.write('+PROG AQUA urs:1\n')
    f.write('\n')
    f.write('HEAD AQUA\n')
    f.write('NORM DC SIA NDC 262\n')
    f.write('\n')

    for key, material in materials.items():

        mtype = material.__name__
        material_index = material.index + 1

        f.write('$ {0}\n'.format(key))
        f.write('$ ' + '-' * len(key) + '\n')
        f.write('\n')

        if mtype == 'Concrete':

            fck = material.fck
            v = material.v['v']
            yc = material.p / 100
            f.write('CONC {0} TYPE C FCN {1} MUE {2} GAM {3} TYPR C\n'.format(material_index, fck, v, yc))

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')


def input_write_nodes_elements(f, nodes, elements, sections, properties, materials, sets, units):
    """ Writes the nodal co-ordinates and element information to the Sofistik .dat file.

    Parameters:
        f (obj): The open file object for the .dat file.
        nodes (dic): Node dictionary from structure.nodes.
        elements (dic): Element dictionary from structure.elements.
        sections (dic): Section objects from structure.sections.
        properties (dic): ElementProperties objects from structure.element_properties.
        materials (dic): Material objects from structure.materials.
        sets (dic): Sets dictionary from structure.sets.
        units (str): Units of the nodal co-ordinates.

    Returns:
        None
    """
    cl = {'m': 1., 'cm': 0.01, 'mm': 0.001}

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ---------------------------------------------------------- Nodes and elements\n')
    f.write('\n')
    f.write('+PROG SOFIMSHA urs:2\n')
    f.write('\n')
    f.write('HEAD SOFIMSHA\n')
    f.write('UNIT 0\n')
    f.write('SYST 3D GDIR POSX,POSY,NEGZ\n')
    f.write('\n')

    # Nodes
    # -----

    f.write('NODE NO X Y Z\n')
    f.write('$ No., x[m], y[m], z[m]\n')
    f.write('\n')

    for key in sorted(nodes, key=int):

        xyz = [str(nodes[key][i] * cl[units]) for i in 'xyz']
        f.write(' '.join([str(key + 1)] + xyz) + '\n')

    # Properties
    # ----------

    for key, property in properties.items():

        if isinstance(property.elsets, str):
            elsets = [property.elsets]

        material_index = materials[property.material].index + 1
        geometry = sections[property.section].geometry

        for elset in elsets:
            for select in sets[elset]['selection']:
                elements[select].material_index = material_index
                elements[select].geometry = geometry

    # Elements
    # --------

    etypes = ['QUAD']
    edic = {i: [] for i in etypes}

    for ekey in sorted(elements, key=int):

        element = elements[ekey]
        nodes = [node + 1 for node in element.nodes]
        data = [element.number + 1] + nodes + [element.material_index]
        geometry = element.geometry
        etype = element.__name__

        if etype == 'ShellElement':
            if len(nodes) == 4:
                estr = 'QUAD'
                data.extend([geometry['t']] * 4)

        edic[estr].append(data)

    for key, edata in edic.items():

        if edata:
            f.write('\n')
            f.write('$ {0}\n'.format(key))
            f.write('$ ' + '-' * len(key) + '\n')
            f.write('\n')

            if key == 'QUAD':
                # f.write('MRF POSI KR\n')
                f.write('QUAD NO N1 N2 N3 N4 MNO T1 T2 T3 T4\n')
                f.write('\n')

            for j in edata:
                f.write('{0}\n'.format(' '.join([str(i) for i in j])))

    # Boundary conditions
    # -------------------

    # f.write('NODE NO FIX\n')

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')

#     GRP 1 BASE 10000
# ABOV  POSX        0.060000        0.080000

