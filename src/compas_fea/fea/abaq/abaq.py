"""
compas_fea.fea.abaq : Abaqus specific functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_bcs
from compas_fea.fea import write_input_elements
from compas_fea.fea import write_input_heading
from compas_fea.fea import write_input_materials
from compas_fea.fea import write_input_nodes
from compas_fea.fea import write_input_steps

from compas_fea.fea.abaq import launch_job
from compas_fea.fea.abaq import odb_extract

from subprocess import Popen
from subprocess import PIPE

from math import pi

from time import time

import json
import os


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'abaqus_launch_process',
    'extract_odb_data',
    'input_write_constraints',
    'input_generate',
]


node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def abaqus_launch_process(structure, exe, cpus):

    """ Runs the analysis through Abaqus.

    Parameters
    ----------
    structure : obj
        Structure object.
    exe : str
        Full terminal command to bypass subprocess defaults.
    cpus : int
        Number of CPU cores to use.

    Returns
    -------
    None

    """

    name = structure.name
    path = structure.path

    # Create temp folder

    temp = '{0}{1}/'.format(path, name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Run sub-process file

    loc = launch_job.__file__
    subprocess = 'noGUI={0}'.format(loc.replace('\\', '/'))

    tic = time()

    success = False
    if not exe:

        args = ['abaqus', 'cae', subprocess, '--', str(cpus), path, name]
        p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            line = str(line.strip())
            print(line)
            if 'COMPLETED' in line:
                success = True
        stdout, stderr = p.communicate()
        print(stdout)
        print(stderr)

        if not success:
            print('***** Analysis failed - attempting to read error logs *****')

            try:
                print('\n***** Attempting to read .msg log *****')

                with open('{0}{1}.msg'.format(temp, name)) as f:
                    lines = f.readlines()
                    for c, line in enumerate(lines):
                        if (' ***ERROR' in line) or (' ***WARNING' in line):
                            print(lines[c][:-2])
                            print(lines[c + 1][:-2])
            except:
                print('***** Loading .msg log failed *****')

            try:
                print('\n***** Attempting to read abaqus.rpy log *****')

                with open('{0}abaqus.rpy'.format(temp)) as f:
                    lines = f.readlines()
                    for c, line in enumerate(lines):
                        if '#: ' in line:
                            print(lines[c])
            except:
                print('***** Loading abaqus.rpy log failed *****')

        else:
            print('***** Analysis successful *****')

    else:

        args = '{0} -- {1} {2} {3}'.format(subprocess, cpus, path, name)
        os.chdir(temp)
        os.system('{0}{1}'.format(exe, args))

    toc = time() - tic

    print('\n***** Abaqus analysis time : {0} s *****'.format(toc))


def extract_odb_data(structure, fields, exe):

    """ Extract data from the Abaqus .odb file.

    Parameters
    ----------
    structure : obj
        Structure object.
    fields : list
        Data field requests.
    exe : str
        Full terminal command to bypass subprocess defaults.

    Returns
    -------
    None

    """

    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)
    loc = odb_extract.__file__
    subprocess = 'noGUI={0}'.format(loc.replace('\\', '/'))

    tic = time()

    if isinstance(fields, str):
        fields = [fields]
    fields = ','.join(list(structure.fields_dic_from_list(fields).keys()))

    if not exe:
        args = ['abaqus', 'cae', subprocess, '--', fields, name, temp]
        p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            line = str(line.strip())
            print(line)
        stdout, stderr = p.communicate()
        print(stdout)
        print(stderr)

    else:
        args = '{0} -- {1} {2} {3}'.format(subprocess, fields, name, temp)
        os.chdir(temp)
        os.system('{0}{1}'.format(exe, args))

    toc = time() - tic

    print('\n***** Data extracted from Abaqus .odb file : {0} s *****\n'.format(toc))

    tic = time()

    try:
        with open('{0}{1}-results.json'.format(temp, name), 'r') as f:
            results = json.load(f)
        with open('{0}{1}-info.json'.format(temp, name), 'r') as f:
            info = json.load(f)

        for step in results:
            print('***** Saving step: {0} *****'.format(step))
            for dtype in results[step]:
                for field in results[step][dtype]:
                    results[step][dtype][field] = {int(k): v for k, v in results[step][dtype][field].items()}

        structure.results = results

        for step in info:
            structure.results[step]['info'] = info[step]

        print('***** Saving data to structure.results successful *****')

    except:
        print('***** Saving data to structure.results unsuccessful *****')

    toc = time() - tic

    print('\n***** Data saved to structure.results : {0} s *****\n'.format(toc))


def input_write_constraints(f, constraints):

    """ Writes the constraints information to the Abaqus .inp file.

    Parameters
    ----------
    f : obj
        The open file object for the .inp file.
    constraints : dic
        Constraint dictionary from structure.constraints.

    Returns
    -------
    None

    """

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ----------------------------------------------------------------- Constraints\n')
    f.write('**\n')

    for key, constraint in constraints.items():

        ctype = constraint.__name__

        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')

        # Tie constraint

        if ctype == 'TieConstraint':

            tol = constraint.tol
            slave = constraint.slave
            master = constraint.master

            f.write('*TIE, POSITION TOLERANCE={0}, NAME={1}, ADJUST=NO\n'.format(tol, key))
            f.write('** SLAVE, MASTER\n')
            f.write('{0}, {1}\n'.format(slave, master))

    f.write('**\n')

    # etypes = ['T3D2', 'CONN3D2', 'B31', 'S3', 'S4', 'M3D3', 'M3D4', 'C3D4', 'C3D6', 'C3D8', 'DC3D4', 'DC3D6', 'DC3D8']
    # edic = {i: [] for i in etypes}

    # for ekey in sorted(elements, key=int):

    #     element = elements[ekey]
    #     nodes = [node + 1 for node in element.nodes]
    #     data = [element.number + 1] + nodes
    #     etype = element.__name__

    #     if etype == 'TrussElement':
    #         estr = 'T3D2'

    #     elif etype == 'SpringElement':
    #         estr = 'CONN3D2'

    #     elif etype == 'MembraneElement':
    #         estr = 'M3D{0}'.format(len(nodes))

    #     elif etype == 'TetrahedronElement':
    #         estr = 'C3D4'

    #     elif etype == 'PentahedronElement':
    #         estr = 'C3D6'

    #     elif etype == 'HexahedronElement':
    #         estr = 'C3D8'

    #     if element.thermal and estr in ['C3D4', 'C3D6', 'C3D8']:
    #         estr = 'D{0}'.format(estr)

    #     edic[estr].append(data)

    # f.write('** -----------------------------------------------------------------------------\n')
    # f.write('** ------------------------------------------------------------------------ Sets\n')


def input_generate(structure, fields, units='m'):

    """ Creates the Abaqus .inp file from the Structure object.

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

    filename = '{0}{1}.inp'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

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

        write_input_heading(f, 'abaqus')
        write_input_nodes(f, 'abaqus', nodes)
        write_input_bcs(f, 'abaqus', structure, steps, displacements, sets)
        write_input_materials(f, 'abaqus', materials)
        write_input_elements(f, 'abaqus', sections, properties, elements, structure, materials)
        input_write_sets(f, sets)  # to make general if possible
        write_input_steps(f, 'abaqus', structure, steps, loads, displacements, sets, fields)

    print('***** Abaqus input file generated: {0} *****\n'.format(filename))


def input_write_misc(f, misc):

    """ Writes misc class info to the Abaqus .inp file.

    Parameters
    ----------
    f : obj
        The open file object for the .inp file.
    misc : dic
        Misc objects from structure.misc.

    Returns
    -------
    None

    """

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ------------------------------------------------------------------------ Misc\n')
    f.write('**\n')

    for key, misc in misc.items():

        mtype = misc.__name__

        if mtype in ['Amplitude']:

            f.write('** {0}\n'.format(key))
            f.write('** ' + '-' * len(key) + '\n')
            f.write('**\n')

        # Amplitude

        if mtype == 'Amplitude':

            f.write('*AMPLITUDE, NAME={0}\n'.format(key))
            f.write('**\n')
            for i, j in misc.values:
                f.write('{0}, {1}\n'.format(i, j))

        f.write('**\n')


def input_write_sets(f, sets):

    """ Creates the Abaqus .inp file node sets NSETs and element sets ELSETs.

    Parameters
    ----------
    f : obj
        The open file object for the .inp file.
    sets : dic
        Sets dictionary from structure.sets.

    Returns
    -------
    None

    Notes
    -----
    - Restriction in Abaqus to 10 entries written per line in the .inp file.

    """

    cm = 9
    for key, set in sets.items():

        stype = set['type']

        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')
        f.write('**\n')

        if stype in ['node', 'element', 'surface_node']:

            if stype == 'node':
                f.write('*NSET, NSET={0}\n'.format(key))
                f.write('**\n')

            elif stype == 'element':
                f.write('*ELSET, ELSET={0}\n'.format(key))
                f.write('**\n')

            elif stype == 'surface_node':
                f.write('*SURFACE, TYPE=NODE, NAME={0}\n'.format(key))
                f.write('**\n')

            selection = [i + 1 for i in set['selection']]
            cnt = 0
            for j in selection:
                f.write(str(j))
                if (cnt < cm) and (j != selection[-1]):
                    f.write(',')
                    cnt += 1
                elif cnt >= cm:
                    f.write('\n')
                    cnt = 0
                else:
                    f.write('\n')

        if stype == 'surface_element':

            f.write('*SURFACE, TYPE=ELEMENT, NAME={0}\n'.format(key))
            f.write('** ELEMENT, SIDE\n')

            selection = set['selection']
            for element, sides in selection.items():
                for side in sides:
                    f.write('{0}, {1}'.format(element + 1, side))
                    f.write('\n')

        f.write('**\n')
    f.write('**\n')
