
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_bcs
from compas_fea.fea import write_input_elements
from compas_fea.fea import write_input_heading
from compas_fea.fea import write_input_materials
from compas_fea.fea import write_input_nodes
from compas_fea.fea import write_input_steps

from subprocess import Popen
from subprocess import PIPE

from time import time
from math import sqrt

import json


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'extract_out_data',
    'opensees_launch_process',
    'input_generate',
]


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

    step = structure.steps_order[1]
    structure.results[step] = {'nodal': {}, 'element': {}}
    nodal = structure.results[step]['nodal']
    element = structure.results[step]['element']

    nodal_data = {}

    for field in fields:

        if field in ['u', 'ur', 'rf', 'rm']:

            file = step + '_node_' + field

            try:

                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                nodal_data[file] = [float(i) for i in lines[-1].split(' ')[1:]]

                for dof in 'xyz':
                    nodal['{0}{1}'.format(field, dof)] = {}
                nodal['{0}m'.format(field)] = {}

                for node in structure.nodes:
                    sum2 = 0
                    for c, dof in enumerate('xyz'):
                        val = nodal_data[file][node * 3 + c]
                        nodal['{0}{1}'.format(field, dof)][node] = val
                        sum2 += val**2
                    nodal['{0}m'.format(field)][node] = sqrt(sum2)

                print('***** {0}.out data loaded *****'.format(file))

            except:

                print('***** {0}.out data not loaded *****'.format(file))

        else:

            try:

                file = step + '_element_truss_sf'

                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                truss_data = [float(i) for i in lines[-1].split(' ')[1:]]

                with open('{0}truss_numbers.json'.format(temp), 'r') as f:
                    truss_numbers = json.load(f)['truss_numbers']

                element['sfx'] = {}
                for ekey, sfx in zip(truss_numbers, truss_data):
                    element['sfx'][ekey] = {}
                    element['sfx'][ekey]['ip'] = sfx

            except:

                print('***** No truss element data loaded *****')

            try:

                file = step + '_element_beam_sf'

                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                beam_data = [float(i) for i in lines[-1].split(' ')[1:]]

                with open('{0}beam_numbers.json'.format(temp), 'r') as f:
                    beam_numbers = json.load(f)['beam_numbers']

                # sort beam data here

            except:

                print('***** No beam element data loaded *****')

            try:

                file = step + '_element_spring_sf'

                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                spring_data = [float(i) for i in lines[-1].split(' ')[1:]]

                with open('{0}spring_numbers.json'.format(temp), 'r') as f:
                    spring_numbers = json.load(f)['spring_numbers']

                element['spfx'] = {}
                for ekey, spfx in zip(spring_numbers, spring_data):
                    element['spfx'][ekey] = {}
                    element['spfx'][ekey]['ip'] = spfx

            except:

                print('***** No spring element data loaded *****')

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

    try:

        name = structure.name
        path = structure.path
        temp = '{0}{1}/'.format(path, name)

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


def input_generate(structure, fields):

    """ Creates the OpenSees .tcl file from the Structure object.

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
            if element.__name__ not in ['TrussElement', 'TieElement', 'StrutElement', 'SpringElement']:
                ndof = 6
                break

        write_input_heading(f, 'opensees', ndof)
        write_input_nodes(f, 'opensees', nodes)
        write_input_bcs(f, 'opensees', structure, steps, displacements, sets, ndof)
        write_input_materials(f, 'opensees', materials)
        write_input_elements(f, 'opensees', sections, properties, elements, structure, materials)
        write_input_steps(f, 'opensees', structure, steps, loads, displacements, sets, fields, ndof)

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))
