
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
    'input_generate',
]


node_fields    = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
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

    # Create temp folder

    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Run subprocess file

    tic = time()

    subprocess = 'noGUI={0}'.format(launch_job.__file__.replace('\\', '/'))
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

    else:

        try:
            args = '{0} -- {1} {2} {3}'.format(subprocess, cpus, path, name)
            os.chdir(temp)
            os.system('{0}{1}'.format(exe, args))
            success = True
        except:
            pass

    if success:
        print('***** Analysis successful: analysis time : {0} s *****'.format(time() - tic))

    else:
        print('***** Analysis failed: attempting to read error logs *****')

        try:
            with open('{0}{1}.msg'.format(temp, name)) as f:
                lines = f.readlines()
                for c, line in enumerate(lines):
                    if (' ***ERROR' in line) or (' ***WARNING' in line):
                        print(lines[c][:-2])
                        print(lines[c + 1][:-2])
        except:
            pass

        try:
            with open('{0}abaqus.rpy'.format(temp)) as f:
                lines = f.readlines()
                for c, line in enumerate(lines):
                    if '#: ' in line:
                        print(lines[c])
        except:
            pass


def input_generate(structure, fields):

    """ Creates the Abaqus .inp file from the Structure object.

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.

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
        write_input_nodes(f, 'abaqus', nodes, sets)
        write_input_bcs(f, 'abaqus', structure, steps, displacements, sets)
        write_input_materials(f, 'abaqus', materials)
        write_input_elements(f, 'abaqus', sections, properties, elements, structure, materials)
        write_input_steps(f, 'abaqus', structure, steps, loads, displacements, sets, fields)

    print('***** Abaqus input file generated: {0} *****\n'.format(filename))


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

    if isinstance(fields, str):
        fields = [fields]
    fields = ','.join(list(structure.fields_dic_from_list(fields).keys()))

    tic1 = time()

    subprocess = 'noGUI={0}'.format(odb_extract.__file__.replace('\\', '/'))

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

    print('\n***** Data extracted from Abaqus .odb file : {0:.3f} s *****\n'.format(time() - tic1))

    tic2 = time()

    try:
        with open('{0}{1}-results.json'.format(temp, name), 'r') as f:
            results = json.load(f)

        with open('{0}{1}-info.json'.format(temp, name), 'r') as f:
            info = json.load(f)

        for step in results:
            print('***** Saving step: {0} *****'.format(step))
            for dtype in results[step]:
                for field in results[step][dtype]:
                    data = {}
                    for key in results[step][dtype][field]:
                        data[int(key)] = results[step][dtype][field][key]
                    results[step][dtype][field] = data

        structure.results = results

        for step in info:
            structure.results[step]['info'] = info[step]

        # structure.save_to_obj()

        print('***** Saving data to structure.results successful : {0:.3f} s *****\n'.format(time() - tic2))

    except:
        print('***** Saving data to structure.results unsuccessful *****')
