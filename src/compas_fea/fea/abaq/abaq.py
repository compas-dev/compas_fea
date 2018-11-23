
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import Writer

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
    'input_generate',
    'extract_data',
    'launch_process',
]


node_fields    = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def input_generate(structure, fields, output):

    """ Creates the Abaqus .inp file from the Structure object.

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.
    output : bool
        Print terminal output.

    Returns
    -------
    None

    """

    filename = '{0}{1}.inp'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

    if 'u' not in fields:
        fields.append('u')

    with Writer(structure=structure, software='abaqus', filename=filename) as writer:

        writer.write_heading()
        writer.write_nodes()
        writer.write_node_sets()
        writer.write_boundary_conditions()
        writer.write_materials()
        writer.write_elements()
        # write_input_misc(f, 'abaqus', misc)
        writer.write_steps()

    if output:
        print('***** Abaqus input file generated: {0} *****\n'.format(filename))
























def launch_process(structure, exe, cpus, output):

    """ Runs the analysis through Abaqus.

    Parameters
    ----------
    structure : obj
        Structure object.
    exe : str
        Abaqus exe path to bypass defaults.
    cpus : int
        Number of CPU cores to use.
    output : bool
        Print terminal output.

    Returns
    -------
    None

    """

    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

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
            if output:
                print(line)
            if 'COMPLETED' in line:
                success = True

        stdout, stderr = p.communicate()

        if output:
            print(stdout)
            print(stderr)

    else:

        args = '{0} -- {1} {2} {3}'.format(subprocess, cpus, path, name)
        os.chdir(temp)
        os.system('{0}{1}'.format(exe, args))
        success = True

    toc = time() - tic

    if success:
        if output:
            print('***** Analysis successful - analysis time : {0} s *****'.format(toc))

    else:
        if output:
            print('***** Analysis failed: attempting to read error logs *****')

        try:
            with open('{0}{1}.msg'.format(temp, name)) as f:
                lines = f.readlines()

                for c, line in enumerate(lines):
                    if (' ***ERROR' in line) or (' ***WARNING' in line):
                        if output:
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


def extract_data(structure, fields, exe, output):

    """ Extract data from the Abaqus .odb file.

    Parameters
    ----------
    structure : obj
        Structure object.
    fields : list
        Data field requests.
    exe : str
        Abaqus exe path to bypass defaults.
    output : bool
        Print terminal output.

    Returns
    -------
    None

    """

    #  Extract

    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)

    if isinstance(fields, str):
        fields = [fields]
    fields = ','.join(list(structure.fields_dict_from_list(fields).keys()))

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

        if output:
            print(stdout)
            print(stderr)

    else:

        args = '{0} -- {1} {2} {3}'.format(subprocess, fields, name, temp)
        os.chdir(temp)
        os.system('{0}{1}'.format(exe, args))

    toc1 = time() - tic1

    if output:
        print('\n***** Data extracted from Abaqus .odb file : {0:.3f} s *****\n'.format(toc1))

    # Save results to Structure

    try:

        tic2 = time()

        with open('{0}{1}-results.json'.format(temp, name), 'r') as f:
            results = json.load(f)

        with open('{0}{1}-info.json'.format(temp, name), 'r') as f:
            info = json.load(f)

        for step in results:
            for dtype in results[step]:
                if dtype in ['nodal', 'element']:
                    for field in results[step][dtype]:
                        data = {}
                        for key in results[step][dtype][field]:
                            data[int(key)] = results[step][dtype][field][key]
                        results[step][dtype][field] = data

        structure.results = results

        for step in info:
            structure.results[step]['info'] = info[step]

        toc2 = time() - tic2

        if output:
            print('***** Saving data to structure.results successful : {0:.3f} s *****\n'.format(toc2))

    except:

        if output:
            print('***** Saving data to structure.results unsuccessful *****')
