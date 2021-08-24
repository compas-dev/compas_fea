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


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'input_generate',
    'extract_data',
    'launch_process',
]


def input_generate(structure, fields, output, ndof):
    """ Creates the OpenSees .tcl file from the Structure object.

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.
    output : bool
        Print terminal output.
    ndof : int
        Number of degrees-of-freedom in the model, 3 or 6.

    Returns
    -------
    None

    """

    filename = '{0}{1}.tcl'.format(structure.path, structure.name)

    with Writer(structure=structure, software='opensees', filename=filename, fields=fields, ndof=ndof) as writer:

        writer.write_heading()
        writer.write_nodes()
        writer.write_boundary_conditions()
        writer.write_materials()
        writer.write_elements()
        writer.write_steps()

    print('***** OpenSees input file generated: {0} *****\n'.format(filename))


def launch_process(structure, exe, output):
    """ Runs the analysis through OpenSees.

    Parameters
    ----------
    structure : obj
        Structure object.
    exe : str
        OpenSees exe path to bypass defaults.
    output : bool
        Print terminal output.

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
        except Exception:
            os.mkdir(temp)

        tic = time()

        if not exe:
            exe = 'C:/OpenSees.exe'

        command = '{0} {1}{2}.tcl'.format(exe, path, name)
        p = Popen(command, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)

        print('Executing command ', command)

        while True:

            line = p.stdout.readline()
            if not line:
                break
            line = str(line.strip())

            if output:
                print(line)

        stdout, stderr = p.communicate()

        if output:
            print(stdout)
            print(stderr)

        toc = time() - tic

        print('\n***** OpenSees analysis time : {0} s *****'.format(toc))

    except Exception:

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

    name = structure.name
    path = structure.path
    temp = '{0}{1}/'.format(path, name)

    step = structure.steps_order[1]
    results = structure.results[step] = {'nodal': {}, 'element': {}}
    nodal = results['nodal']
    element = results['element']

    if structure.steps[step].__name__ != 'ModalStep':

        # Loads

        nodes = range(structure.node_count())

        for i in 'xyz':
            nodal['cf{0}'.format(i)] = {i: 0 for i in nodes}
            nodal['cm{0}'.format(i)] = {i: 0 for i in nodes}

        for k in structure.steps[structure.steps_order[1]].loads:

            load = structure.loads[k]

            if load.__name__ == 'PointLoad':
                com = load.components

                nn = load.nodes
                if isinstance(nn, str):
                    nn = [nn]

                for node in nn:
                    ns = structure.sets[node].selection if isinstance(node, str) else node

                    for ni in ns:
                        for i in 'xyz':
                            nodal['cf{0}'.format(i)][ni] += com[i]
                            nodal['cm{0}'.format(i)][ni] += com[i + i]

        # Fields

        for field in fields:

            file = '{0}_{1}'.format(step, field)

            # Nodal data

            if field in ['u', 'ur', 'rf', 'rm']:

                try:

                    with open('{0}{1}.out'.format(temp, file), 'r') as f:
                        lines = f.readlines()
                    data = [float(i) for i in lines[-1].split(' ')[1:]]

                    dofx = data[0::3]
                    dofy = data[1::3]
                    dofz = data[2::3]
                    dofm = [sqrt(u**2 + v**2 + w**2) for u, v, w in zip(dofx, dofy, dofz)]

                    nodal['{0}x'.format(field)] = {i: dofx[i] for i in nodes}
                    nodal['{0}y'.format(field)] = {i: dofy[i] for i in nodes}
                    nodal['{0}z'.format(field)] = {i: dofz[i] for i in nodes}
                    nodal['{0}m'.format(field)] = {i: dofm[i] for i in nodes}

                    print('***** {0}.out data loaded *****'.format(file))

                except Exception:

                    print('***** {0}.out data not loaded/saved'.format(file))

            # Element data

            elif field in ['sf', 'spf']:

                # Truss data

                try:

                    element['sf1'] = {}

                    with open('{0}{1}_truss.out'.format(temp, file), 'r') as f:
                        lines = f.readlines()
                    data = [float(i) for i in lines[-1].split(' ')[1:]]

                    with open('{0}truss_ekeys.json'.format(temp), 'r') as f:
                        truss_ekeys = json.load(f)['truss_ekeys']

                    for ekey, sf1 in zip(truss_ekeys, data):
                        element['sf1'][ekey] = {'ip': sf1}

                    print('***** {0}.out data loaded *****'.format(file))

                except Exception:

                    print('***** No truss element data loaded')

                # Beam data

                try:

                    with open('{0}{1}_beam.out'.format(temp, file), 'r') as f:
                        lines = f.readlines()
                    data = [float(i) for i in lines[-1].split(' ')[1:]]

                    element['sf1'] = {}
                    element['sf2'] = {}
                    element['sf3'] = {}
                    element['sm1'] = {}
                    element['sm2'] = {}
                    element['sm3'] = {}

                    sf1_a = data[0::12]
                    sf2_a = data[1::12]
                    sf3_a = data[2::12]
                    sm1_a = data[5::12]
                    sm2_a = data[4::12]
                    sm3_a = data[3::12]
                    sf1_b = data[6::12]
                    sf2_b = data[7::12]
                    sf3_b = data[8::12]
                    sm1_b = data[11::12]
                    sm2_b = data[10::12]
                    sm3_b = data[9::12]

                    with open('{0}beam_ekeys.json'.format(temp), 'r') as f:
                        beam_ekeys = json.load(f)['beam_ekeys']

                    for c, ekey in enumerate(beam_ekeys):
                        element['sf1'][ekey] = {'ip1': -sf1_a[c], 'ip2': sf1_b[c]}
                        element['sf2'][ekey] = {'ip1': -sf2_a[c], 'ip2': sf2_b[c]}
                        element['sf3'][ekey] = {'ip1': -sf3_a[c], 'ip2': sf3_b[c]}
                        element['sm1'][ekey] = {'ip1': -sm1_a[c], 'ip2': sm1_b[c]}
                        element['sm2'][ekey] = {'ip1': -sm2_a[c], 'ip2': sm2_b[c]}
                        element['sm3'][ekey] = {'ip1': -sm3_a[c], 'ip2': sm3_b[c]}

                    print('***** {0}.out data loaded *****'.format(file))

                except Exception:

                    print('***** No beam element data loaded *****')

                # Spring data

                try:

                    with open('{0}{1}_spring.out'.format(temp, file), 'r') as f:
                        lines = f.readlines()
                    data = [float(i) for i in lines[-1].split(' ')[1:]]

                    element['spfx'] = {}

                    with open('{0}spring_ekeys.json'.format(temp), 'r') as f:
                        spring_ekeys = json.load(f)['spring_ekeys']

                    for ekey, spfx in zip(spring_ekeys, data):
                        element['spfx'][ekey] = {}
                        element['spfx'][ekey]['ip'] = spfx

                    print('***** {0}.out data loaded *****'.format(file))

                except Exception:

                    print('***** No spring element data loaded *****')

        print('\n***** Data extracted from OpenSees .out file(s) : {0} s *****\n'.format(time() - tic))

    else:

        nodes = range(structure.node_count())

        file = '{0}_frequencies'.format(step)

        with open('{0}{1}.txt'.format(temp, file), 'r') as f:
            lines = f.readlines()
        data = [float(i.rstrip('\n')) for i in lines]

        structure.results[step]['frequencies'] = data
        structure.results[step]['masses'] = [0 for i in data]

        for mode in range(structure.steps[step].modes):

            try:

                file = '{0}_u_mode-{1}'.format(step, mode + 1)

                with open('{0}{1}.out'.format(temp, file), 'r') as f:
                    lines = f.readlines()
                data = [float(i) for i in lines[-1].split(' ')]

                dofx = data[0::3]
                dofy = data[1::3]
                dofz = data[2::3]
                dofm = [sqrt(u**2 + v**2 + w**2) for u, v, w in zip(dofx, dofy, dofz)]

                nodal['ux{0}'.format(mode + 1)] = {i: dofx[i] for i in nodes}
                nodal['uy{0}'.format(mode + 1)] = {i: dofy[i] for i in nodes}
                nodal['uz{0}'.format(mode + 1)] = {i: dofz[i] for i in nodes}
                nodal['um{0}'.format(mode + 1)] = {i: dofm[i] for i in nodes}

                print('***** {0}.out data loaded *****'.format(file))

            except Exception:

                print('***** {0}.out data not loaded/saved'.format(file))
