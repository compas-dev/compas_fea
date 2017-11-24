"""
compas_fea.fea.opensees : OpenSEES file creator.
"""

from __future__ import print_function
from __future__ import absolute_import

from subprocess import Popen
from subprocess import PIPE

from time import time

from math import sqrt

import os


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
    'input_write_heading',
    'input_write_nodes',
    'input_write_bcs',
    'input_write_elements',
    'input_write_recorders',
    'input_write_patterns',
    'opensees_launch_process'
]


def extract_out_data(structure):
    """ Extract data from the OpenSees .out files.

    Parameters:
        structure (obj): Structure object.

    Returns:
        None
    """
    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)

    step = structure.steps_order[1]
    structure.results[step] = {'nodal': {}, 'element': {}}

    # Nodal data

    with open('{0}node_u.out'.format(temp), 'r') as f:
        lines = f.readlines()
    u_out = [float(i) for i in lines[-1].split(' ')[1:]]

    with open('{0}node_ur.out'.format(temp), 'r') as f:
        lines = f.readlines()
    ur_out = [float(i) for i in lines[-1].split(' ')[1:]]

    nodal = structure.results[step]['nodal']
    # elemental = structure.results[step]['element']

    for dof in 'xyz':
        nodal['u{0}'.format(dof)] = {}
        nodal['ur{0}'.format(dof)] = {}
    nodal['um'] = {}
    nodal['urm'] = {}

    for node in structure.nodes:
        u_sum2 = 0
        ur_sum2 = 0
        for c, dof in enumerate('xyz'):
            u_val = u_out[node * 3 + c]
            ur_val = ur_out[node * 3 + c]
            nodal['u{0}'.format(dof)][node] = u_val
            nodal['ur{0}'.format(dof)][node] = ur_val
            u_sum2 += u_val**2
            ur_sum2 += ur_val**2
        nodal['um'][node] = sqrt(u_sum2)
        nodal['urm'][node] = sqrt(ur_sum2)


def opensees_launch_process(structure, exe):
    """ Runs the analysis through OpenSees.

    Parameters:
        structure (obj): Structure object.
        exe (str): Full terminal command to bypass subprocess defaults.

    Returns:
        None
    """
    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)

    # Run sub-process file

    tic = time()

    if not exe:
        exe = 'C:/OpenSees.exe'

    command = '{0} {1}{2}.tcl'.format(exe, path, name)
    print(command)
    p = Popen(command, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        line = str(line.strip())
        print(line)
    stdout, stderr = p.communicate()
    print(stdout)
    print(stderr)

    toc = time() - tic

    print('\n***** OpenSees analysis time : {0} s *****'.format(toc))


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

        displacements = structure.displacements
        elements = structure.elements
        loads = structure.loads
        materials = structure.materials
        nodes = structure.nodes
        properties = structure.element_properties
        sections = structure.sections
        sets = structure.sets
        steps = structure.steps

        input_write_heading(f)
        input_write_nodes(f, nodes, units)
        input_write_bcs(f, structure, steps, displacements)
        input_write_elements(f, sections, properties, elements, sets, materials)
        input_write_recorders(f, structure)
        input_write_patterns(f, structure, steps, loads, sets)

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
    f.write('wipe\n')
    f.write('model basic -ndm 3 -ndf 6\n')
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
        f.write('node ' + ' '.join([str(key + 1)] + xyz) + '\n')

    f.write('##\n')


def input_write_bcs(f, structure, steps, displacements):
    """ Writes boundary condition information to the OpenSees .tcl file.

    Parameters:
        f (obj): The open file object for the .tcl file.
        structure (obj): Struture object.
        steps (dic): Step objects from structure.steps.
        displacements (dic): Displacement objects from structure.displacements.

    Returns:
        None
    """
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## ------------------------------------------------------------------------- BCs\n')

    dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']

    key = structure.steps_order[0]
    step = steps[key]
    stype = step.__name__

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
                f.write('fix {0} {1}\n'.format(node + 1, ' '.join(j)))

    f.write('##\n')


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

    for key, property in properties.items():
        material = property.material
        elsets = property.elsets
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

                    ex = ' '.join([str(k) for k in elements[select].axes['ex']])
                    f.write('##\n')
                    f.write('geomTransf Linear {0} {1}\n'.format(select + 1, ex))
                    f.write('element elasticBeamColumn {0} {1} {2} {3} {4} {5} {6} {7} {8} {9}\n'.format(n, i, j, A, E, G, J, Ixx, Iyy, select + 1))

    f.write('##\n')


def input_write_patterns(f, structure, steps, loads, sets):
    """ Writes the load patterns information to the OpenSees .tcl file.

    Parameters:
        f (obj): The open file object for the .tcl file.
        structure (obj): The Structure object to read from.
        steps (dic): Step objects from structure.steps.
        loads (dic): Load objects from structure.loads.
        sets (dic): Sets from strctures.sets.

    Returns:
        None
    """
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## -------------------------------------------------------------------- Analysis\n')

    dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']

    key = structure.steps_order[1]
    step = steps[key]
    stype = step.__name__
    index = step.index
    factor = step.factor
    # tolerance = step.tolerance
    # iterations = step.iterations
    increments = step.increments

    f.write('##\n')
    f.write('## {0}\n'.format(key))
    f.write('## ' + '-' * len(key) + '\n')
    f.write('##\n')

    f.write('timeSeries Constant {0} -factor 1.0\n'.format(index))
    f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(index, factor, '{'))

    # Mechanical

    if stype in ['GeneralStep', 'BucklingStep']:

        # Loads

        for k in step.loads:
            f.write('##\n')

            load = loads[k]
            ltype = load.__name__
            com = load.components
            axes = load.axes
            nset = load.nodes
            elset = load.elements

            # Point load

            if ltype == 'PointLoad':

                coms = ' '.join([str(com[dof]) for dof in dofs])
                for node in sets[nset]['selection']:
                    f.write('load {0} {1}\n'.format(node + 1, coms))

            # Line load

            elif ltype == 'LineLoad':

                if axes == 'global':
                    raise NotImplementedError

                elif axes == 'local':
                    elements = ' '.join([str(i + 1) for i in sets[elset]['selection']])
                    f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, com['y'], com['x']))

    f.write('##\n')
    f.write('{0}\n'.format('}'))

    f.write('##\n')
    f.write('constraints Plain\n')
    f.write('##\n')
    f.write('numberer RCM\n')
    f.write('##\n')
    f.write('system ProfileSPD\n')
    # f.write('##\n')
    # f.write('test RelativeNormUnbalance {0} {1} 2\n'.format(tolerance, iterations))
    # f.write('##\n')
    # f.write('algorithm Newton\n')
    # f.write('##\n')
    # f.write('integrator LoadControl {0}\n'.format(1./increments))
    # f.write('##\n')
    f.write('analysis Static\n')
    f.write('##\n')
    f.write('analyze {0}\n'.format(increments))
    f.write('##\n')


def input_write_recorders(f, structure):
    """ Writes the recorders information to the OpenSees .tcl file.

    Parameters:
        f (obj): The open file object for the .tcl file.
        structure (obj): The Structure object to read from.

    Returns:
        None
    """
    f.write('## -----------------------------------------------------------------------------\n')
    f.write('## ------------------------------------------------------------------- Recorders\n')
    f.write('##\n')

    # Files and folders

    name = structure.name
    path = structure.path

    temp = '{0}{1}/'.format(path, name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Write nodal

    node_u = '{0}node_u.out'.format(temp)
    node_ur = '{0}node_ur.out'.format(temp)

    nodes = '1 {0}'.format(structure.node_count())
    f.write('recorder Node -file {0} -time -nodeRange {1} -dof 1 2 3 disp\n'.format(node_u, nodes))
    f.write('recorder Node -file {0} -time -nodeRange {1} -dof 4 5 6 disp\n'.format(node_ur, nodes))

    # Write element

    element_sf = '{0}element_sf.out'.format(temp)
    # element_s_e = '{0}element_s_e.out'.format(temp)

    elements = '1 {0}'.format(structure.element_count())
    f.write('recorder Element -file {0} -time -eleRange {1} force\n'.format(element_sf, elements))
    # f.write('recorder Element -file {0} -time -eleRange {1} stressStrain'.format(element_sf, elements))

    f.write('##\n')
