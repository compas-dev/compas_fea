
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import Writer

from subprocess import Popen
from subprocess import PIPE

from time import time
from math import sqrt

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


def input_generate(structure, fields, output):

    """ Creates the OpenSees .tcl file from the Structure object.

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

    filename = '{0}{1}.tcl'.format(structure.path, structure.name)

    ndof = 3
    for element in structure.elements.values():
        if element.__name__ not in ['TrussElement', 'TieElement', 'StrutElement', 'SpringElement']:
            ndof = 6
            break

    with Writer(structure=structure, software='opensees', filename=filename, fields=fields, ndof=ndof) as writer:

        writer.write_heading()
        writer.write_nodes()
        writer.write_boundary_conditions()
        writer.write_materials()
        writer.write_elements()
        writer.write_steps()

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))







































def launch_process(structure, exe):

    """ Runs the analysis through OpenSees.

    Parameters
    ----------
    structure : obj
        Structure object.
    exe : str
        OpenSees exe path to bypass defaults.

    Returns
    -------
    None

    """

    try:

        name = structure.name
        path = structure.path
        temp = '{0}{1}/'.format(path, name)
        try:
            os.stat(temp)
        except:
            os.mkdir(temp)

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

    except:

        print('\n***** OpenSees analysis failed')


def extract_data(structure, fields):

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

    step = structure.steps_order[1]
    results = structure.results[step] = {'nodal': {}, 'element': {}}
    nodal   = results['nodal']
    element = results['element']

    for field in fields:
        file = step + '_' + field

        # Nodal data

        if field in ['u', 'ur', 'rf', 'rm']:

            try:
                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                data = [float(i) for i in lines[-1].split(' ')[1:]]

                for dof in 'xyz':
                    nodal['{0}{1}'.format(field, dof)] = {}
                nodal['{0}m'.format(field)] = {}

                for node in structure.nodes:
                    sum2 = 0
                    for c, dof in enumerate('xyz'):
                        val = data[node * 3 + c]
                        nodal['{0}{1}'.format(field, dof)][node] = val
                        sum2 += val**2
                    nodal['{0}m'.format(field)][node] = sqrt(sum2)

                print('***** {0}.out data loaded *****'.format(file))

            except:
                print('***** {0}.out data not loaded/saved'.format(file))

        elif field in ['sf']:

            # Truss data

            try:
                with open('{0}{1}_truss.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                data = [float(i) for i in lines[-1].split(' ')[1:]]

                with open('{0}truss_ekeys.json'.format(temp), 'r') as f:
                    truss_ekeys = json.load(f)['truss_ekeys']

                element['sf1'] = {}
                for ekey, sf1 in zip(truss_ekeys, data):
                    element['sf1'][ekey] = {}
                    element['sf1'][ekey]['ip'] = sf1

                print('***** {0}.out data loaded *****'.format(file))

            except:
                print('***** No truss element data loaded')

    #         try:

    #             file = step + '_element_beam_sf'

    #             with open('{0}{1}.out'.format(temp, file), 'r') as f:
    #                 lines = f.readlines()
    #             beam_data = [float(i) for i in lines[-1].split(' ')[1:]]

    #             with open('{0}beam_numbers.json'.format(temp), 'r') as f:
    #                 beam_numbers = json.load(f)['beam_numbers']

    #             # sort beam data here

    #         except:

    #             print('***** No beam element data loaded *****')

    #         try:

    #             file = step + '_element_spring_sf'

    #             with open('{0}{1}.out'.format(temp, file), 'r') as f:
    #                 lines = f.readlines()
    #             spring_data = [float(i) for i in lines[-1].split(' ')[1:]]

    #             with open('{0}spring_numbers.json'.format(temp), 'r') as f:
    #                 spring_numbers = json.load(f)['spring_numbers']

    #             element['spfx'] = {}
    #             for ekey, spfx in zip(spring_numbers, spring_data):
    #                 element['spfx'][ekey] = {}
    #                 element['spfx'][ekey]['ip'] = spfx

    #         except:

    #             print('***** No spring element data loaded *****')

    print('\n***** Data extracted from OpenSees .out file(s) : {0} s *****\n'.format(time() - tic))
