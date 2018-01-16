
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_bcs
from compas_fea.fea import write_input_heading
from compas_fea.fea import write_input_nodes

from subprocess import Popen
from subprocess import PIPE

from time import time

from math import sqrt

import os


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'extract_out_data',
    'opensees_launch_process',
    'input_generate',
    'input_write_elements',
    'input_write_recorders',
    'input_write_patterns',
]


dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']


def extract_out_data(structure, fields):

    """ Extract data from the OpenSees .out files.

    Parameters
    ----------
    structure : obj
        Structure object.
    fields : list
        Requested fields output.

    Returns
    -------
    None

    """

    tic = time()

    temp = '{0}{1}/'.format(structure.path, structure.name)

    step = structure.steps_order[1]  # expand to other steps later
    structure.results[step] = {'nodal': {}, 'element': {}}

    # Data

    nodal_data = {}
    nodal = structure.results[step]['nodal']
    element_data = {}
    element = structure.results[step]['element']
    # ! element data only working for trusses

    for field in fields:

        if field in ['u', 'ur', 'rf', 'rm']:

            file = 'node_' + field
            try:
                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                nodal_data[file] = [float(i) for i in lines[-1].split(' ')[1:]]
            except:
                print('***** {0}.out data not loaded *****'.format(file))

            for dof in 'xyz':
                nodal['{0}{1}'.format(field, dof)] = {}
            nodal['{0}m'.format(field)] = {}

            for node in structure.nodes:
                try:
                    sum2 = 0
                    for c, dof in enumerate('xyz'):
                        val = nodal_data[file][node * 3 + c]
                        nodal['{0}{1}'.format(field, dof)][node] = val
                        sum2 += val**2
                    nodal['{0}m'.format(field)][node] = sqrt(sum2)
                except:
                    pass

        elif field in ['sf']:

            file = 'element_' + field
            try:
                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                element_data[file] = [float(i) for i in lines[-1].split(' ')[1:]]
            except:
                print('***** {0}.out data not loaded *****'.format(file))

            for dof in ['x']:  # needs updating for more than axial force
                element['{0}{1}'.format(field, dof)] = {}

            for i in structure.elements:
                try:
                    for c, dof in enumerate('x'):
                        val = element_data[file][i + c]
                        element['{0}{1}'.format(field, dof)][i] = {}
                        element['{0}{1}'.format(field, dof)][i]['ip'] = val
                except:
                    pass

    toc = time() - tic

    print('\n***** Data extracted from OpenSees .out file(s) : {0} s *****\n'.format(toc))


def opensees_launch_process(structure, exe):

    """ Runs the analysis through OpenSees.

    Parameters
    ----------
    structure : obj
        Structure object.
    exe : str
        Full terminal command to bypass subprocess defaults.

    Returns
    -------
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

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.
    units : str
        Units of the nodal co-ordinates 'm','cm','mm'.

    Returns
    -------
    None

    """

    filename = '{0}{1}.tcl'.format(structure.path, structure.name)

    with open(filename, 'w') as f:

        constraints   = structure.constraints
        displacements = structure.displacements
        elements      = structure.elements
        interactions  = structure.interactions
        loads         = structure.loads
        materials     = structure.materials
        misc          = structure.misc
        nodes         = structure.nodes
        properties    = structure.element_properties
        sections      = structure.sections
        sets          = structure.sets
        steps         = structure.steps

        ndof = 3
        for element in elements.values():
            if element.__name__ not in ['TrussElement', 'TieElement', 'StrutElement']:
                ndof = 6
                break

        write_input_heading(f, 'opensees', ndof)
        write_input_nodes(f, 'opensees', nodes)
        write_input_bcs(f, 'opensees', structure, steps, displacements, ndof)

        input_write_elements(f, sections, properties, elements, structure, materials)
        input_write_recorders(f, structure, ndof, fields)
        input_write_patterns(f, structure, steps, loads, sets, ndof)

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))


def input_write_elements(f, sections, properties, elements, structure, materials):

    """ Writes the element and section information to the OpenSees .tcl file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    sections : dic
        Section objects from structure.sections.
    properties : dic
        ElementProperties objects from structure.element_properties.
    elements : dic
        Element objects from structure.elements.
    structure : obj
        The Structure object.
    materials : dic
        Material objects from structure.materials.

    Returns
    -------
    None

    """

    # Sections:

    shells = ['ShellSection']
    solids = ['SolidSection', 'TrussSection']

    # Write data

    f.write('# -----------------------------------------------------------------------------\n')
    f.write('# -------------------------------------------------------------------- Elements\n')

    for key, property in properties.items():

        section = sections[property.section]
        material = materials[property.material]

        if property.elements:
            elset_name = 'elset_{0}'.format(key)
            structure.add_set(name=elset_name, type='element', selection=property.elements)
            elsets = [elset_name]
        else:
            elsets = property.elsets

        sets = structure.sets

        material_index = material.index + 1
        stype = section.__name__
        geometry = section.geometry

        f.write('#\n')
        f.write('# Section: {0}\n'.format(key))
        f.write('# ---------' + '-' * (len(key)) + '\n')
        f.write('#\n')

        if isinstance(elsets, str):
            elsets = [elsets]

        for elset in elsets:
            selection = sets[elset]['selection']

            # Beam sections

            if (stype not in shells) and (stype not in solids):

                # f.write('# eType No. node.start node.end E[Pa] G[Pa] A[m2] J[m^4] Ixx[m^4] Iyy[m^4] Avy[m2] Avx[m2] trans\n')
                f.write('# eType, No., node.start, node.end, A[m2], E[Pa], G[Pa], J[m^4], Iyy[m^4], Ixx[m^4], trans\n')
                f.write('#\n')
                for select in selection:
                    sp, ep = elements[select].nodes
                    n = select + 1
                    i = sp + 1
                    j = ep + 1
                    A = geometry['A']
                    E = material.E['E']
                    G = material.G['G']
                    J = geometry['J']
                    Ixx = geometry['Ixx']
                    Iyy = geometry['Iyy']
                    Avy = geometry['Avy']
                    Avx = geometry['Avx']
                    ex = ' '.join([str(k) for k in elements[select].axes['ex']])
                    f.write('#\n')
                    # f.write('geomTransf PDelta {0} {1}\n'.format(n, ex))
                    # f.write('element ElasticTimoshenkoBeam {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}\n'.format(n, i, j, E, G, A, J, Ixx, Iyy, Avy, Avx, n))
                    f.write('geomTransf Corotational {0} {1}\n'.format(select + 1, ex))
                    f.write('element elasticBeamColumn {0} {1} {2} {3} {4} {5} {6} {7} {8} {9}\n'.format(
                            n, i, j, A, E, G, J, Ixx, Iyy, n))

            # Truss sections

            elif stype == 'TrussSection':

                if material.__name__ == 'ElasticIsotropic':
                    E = material.E['E']
                    f.write('# No., E[Pa]\n')
                    f.write('#\n')
                    f.write('uniaxialMaterial Elastic {0} {1}\n'.format(material_index, E))
                    f.write('#\n')

                f.write('# eType, No., node.start, node.end, A[m2], material\n')
                f.write('#\n')
                for select in selection:
                    sp, ep = elements[select].nodes
                    n = select + 1
                    i = sp + 1
                    j = ep + 1
                    A = geometry['A']
                    f.write('element corotTruss {0} {1} {2} {3} {4}\n'.format(n, i, j, A, material_index))

    f.write('#\n')


def input_write_patterns(f, structure, steps, loads, sets, ndof):

    """ Writes the load patterns information to the OpenSees .tcl file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    structure : obj
        The Structure object to read from.
    steps : dic
        Step objects from structure.steps.
    loads : dic
        Load objects from structure.loads.
    sets : dic
        Sets from strctures.sets.
    ndof : int
        Number of degrees-of-freedom per node.

    Returns
    -------
    None

    """

    f.write('# -----------------------------------------------------------------------------\n')
    f.write('# -------------------------------------------------------------------- Analysis\n')

    keys = [structure.steps_order[1]]  # currently only the 2nd step, should be 2nd onwards

    for key in keys:

        step = steps[key]
        stype = step.__name__
        step_index = step.index
        factor = step.factor
        increments = step.increments
        tolerance = step.tolerance
        iterations = step.iterations

        f.write('#\n')
        f.write('# {0}\n'.format(key))
        f.write('# ' + '-' * len(key) + '\n')
        f.write('#\n')

        f.write('timeSeries Constant {0} -factor 1.0\n'.format(step_index))
        f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'))

        # Mechanical

        if stype in ['GeneralStep', 'BucklingStep']:

            # Loads

            for k in step.loads:

                load = loads[k]
                ltype = load.__name__
                com = load.components
                axes = load.axes
                nset = load.nodes
                elset = load.elements

                # Point load

                if ltype == 'PointLoad':

                    coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])
                    for node in sets[nset]['selection']:
                        f.write('load {0} {1}\n'.format(node + 1, coms))

                # Line load

                elif ltype == 'LineLoad':

                    if axes == 'global':
                        raise NotImplementedError

                    elif axes == 'local':
                        elements = ' '.join([str(i + 1) for i in sets[elset]['selection']])
                        f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, -com['y'], -com['x']))

    f.write('{0}\n'.format('}'))

    f.write('#\n')
    f.write('constraints Plain\n')
    f.write('numberer RCM\n')
    f.write('system ProfileSPD\n')
    f.write('test NormUnbalance {0} {1} 5\n'.format(tolerance, iterations))
    f.write('algorithm NewtonLineSearch\n')
    f.write('integrator LoadControl {0}\n'.format(1./increments))
    f.write('analysis Static\n')
    f.write('analyze {0}\n'.format(increments))
    f.write('#\n')


def input_write_recorders(f, structure, ndof, fields):

    """ Writes the recorders information to the OpenSees .tcl file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    structure : obj
        The Structure object to read from.
    ndof : int
        Number of degrees-of-freedom per node.
    fields : list
        Requested fields output.

    Returns
    -------
    None

    """

    f.write('# -----------------------------------------------------------------------------\n')
    f.write('# ------------------------------------------------------------------- Recorders\n')
    f.write('#\n')

    # Temp folder

    temp = '{0}{1}/'.format(structure.path, structure.name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Nodal files

    f.write('# Node\n')
    f.write('# ----\n')
    f.write('#\n')

    nodes = '1 {0}'.format(structure.node_count())
    nodal = {}

    if 'u' in fields:
        nodal['node_u.out'] = '1 2 3 disp'
    if 'rf' in fields:
        nodal['node_rf.out'] = '1 2 3 reaction'

    if ndof == 6:
        if 'ur' in fields:
            nodal['node_ur.out'] = '4 5 6 disp'
        if 'rm' in fields:
            nodal['node_rm.out'] = '4 5 6 reaction'

    for key, item in nodal.items():
        f.write('recorder Node -file {0}{1} -time -nodeRange {2} -dof {3}\n'.format(temp, key, nodes, item))

    # Element files

    f.write('#\n')
    f.write('# Element\n')
    f.write('# -------\n')
    f.write('#\n')

    elements = '1 {0}'.format(structure.element_count())
    elemental = {}

    if 'sf' in fields:
        elemental['element_sf.out'] = 'basicForces'
        # 'element_s-e': 'stressStrain',
    # Truss is 'axialForce,' 'forces,' 'localForce', deformations,'

    for key, item in elemental.items():
        f.write('recorder Element -file {0}{1} -time -eleRange {2} {3}\n'.format(temp, key, elements, item))

    f.write('#\n')
