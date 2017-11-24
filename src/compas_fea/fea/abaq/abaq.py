"""
compas_fea.fea.abaq : Abaqus specific functions.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas_fea.fea.abaq import launch_job
from compas_fea.fea.abaq import odb_extract

from subprocess import Popen
from subprocess import PIPE

from math import pi

from time import time

import json
import os


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'abaqus_launch_process',
    'extract_odb_data',
    'input_write_constraints',
    'input_write_elements',
    'input_generate',
    'input_write_heading',
    'input_write_materials',
    'input_write_misc',
    'input_write_nodes',
    'input_write_properties',
    'input_write_sets',
    'input_write_steps'
]


node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def abaqus_launch_process(structure, exe, cpus):
    """ Runs the analysis through Abaqus.

    Parameters:
        structure (obj): Structure object.
        exe (str): Full terminal command to bypass subprocess defaults.
        cpus (int): Number of CPU cores to use.

    Returns:
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

    Parameters:
        structure (obj): Structure object.
        fields (list): Data field requests.
        exe (str): Full terminal command to bypass subprocess defaults.

    Returns:
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

        for step in results:
            for dtype in results[step]:
                for field in results[step][dtype]:
                    results[step][dtype][field] = {int(k): v for k, v in results[step][dtype][field].items()}

        structure.results = results

        print('***** Saving data to structure.results successful *****')

    except:
        print('***** Saving data to structure.results unsuccessful *****')

    toc = time() - tic

    print('\n***** Data saved to structure.results : {0} s *****\n'.format(toc))


def input_write_constraints(f, constraints):
    """ Writes the constraints information to the Abaqus .inp file.

    Parameters:
        f (obj): The open file object for the .inp file.
        constraints (dic): Constraint dictionary from structure.constraints.

    Returns:
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


def input_write_elements(f, elements):
    """ Writes the element information to the Abaqus .inp file.

    Note:
        - T3D2    truss     2 nodes elset_T3D2.
        - CONN3D2 connector 2 nodes elset_CONN3D2
        - B31     beam      2 nodes elset_B31.
        - S3      shell     3 nodes elset_S3.
        - S4      shell     4 nodes elset_S4.
        - M3D3    membrane  3 nodes elset_M3D3.
        - M3D4    membrane  4 nodes elset_M3D4.
        - C3D4    solid     4 nodes elset_C3D4.
        - C3D6    solid     6 nodes elset_C3D6.
        - C3D8    solid     8 nodes elset_C3D8.
        - DC3D4   solid     4 nodes elset_DC3D4 thermal.
        - DC3D6   solid     6 nodes elset_DC3D6 thermal.
        - DC3D8   solid     8 nodes elset_DC3D8 thermal.

    Parameters:
        f (obj): The open file object for the .inp file.
        elements (dic): Elements from structure.elements.

    Returns:
        None
    """

    # Sort elements

    etypes = ['T3D2', 'CONN3D2', 'B31', 'S3', 'S4', 'M3D3', 'M3D4', 'C3D4', 'C3D6', 'C3D8', 'DC3D4', 'DC3D6', 'DC3D8']
    edic = {i: [] for i in etypes}

    for ekey in sorted(elements, key=int):

        element = elements[ekey]
        nodes = [node + 1 for node in element.nodes]
        data = [element.number + 1] + nodes
        etype = element.__name__

        if etype == 'TrussElement':
            estr = 'T3D2'

        elif etype == 'BeamElement':
            estr = 'B31'

        elif etype == 'SpringElement':
            estr = 'CONN3D2'

        elif etype == 'ShellElement':
            estr = 'S{0}'.format(len(nodes))

        elif etype == 'MembraneElement':
            estr = 'M3D{0}'.format(len(nodes))

        elif etype == 'TetrahedronElement':
            estr = 'C3D4'

        elif etype == 'PentahedronElement':
            estr = 'C3D6'

        elif etype == 'HexahedronElement':
            estr = 'C3D8'

        if element.thermal and estr in ['C3D4', 'C3D6', 'C3D8']:
            estr = 'D{0}'.format(estr)

        edic[estr].append(data)

    # Write element data

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** -------------------------------------------------------------------- Elements\n')

    elset_all = []
    for key, edata in edic.items():

        if edata:
            f.write('**\n')
            f.write('** {0}\n'.format(key))
            f.write('** ' + '-' * len(key) + '\n')
            f.write('**\n')
            f.write('*ELEMENT, TYPE={0}, ELSET=elset_{0}\n'.format(key))
            f.write('** No., nodes\n')
            f.write('**\n')

            for j in edata:
                f.write('{0}, {1}\n'.format(j[0], ','.join([str(i) for i in j[1:]])))
            elset_all.append('elset_{0}'.format(key))

            f.write('**\n')

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ------------------------------------------------------------------------ Sets\n')
    f.write('**\n')
    f.write('** elset_all\n')
    f.write('** ---------\n')
    f.write('**\n')
    f.write('*ELSET, ELSET=elset_all\n')
    f.write('**\n')
    f.write(', '.join(elset_all))
    f.write('\n**\n')


def input_generate(structure, fields, units='m'):
    """ Creates the Abaqus .inp file from the Structure object.

    Parameters:
        structure (obj): The Structure object to read from.
        fields (list): Data field requests.
        units (str): Units of the nodal co-ordinates 'm','cm','mm'.

    Returns:
        None
    """
    filename = '{0}{1}.inp'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

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
        input_write_elements(f, elements)
        input_write_sets(f, sets)
        input_write_materials(f, materials)
        input_write_misc(f, misc)
        input_write_properties(f, sections, properties, elements, sets)
        input_write_constraints(f, constraints)
        input_write_steps(f, structure, steps, loads, displacements, interactions, misc, fields)

    print('***** Abaqus input file generated: {0} *****\n'.format(filename))


def input_write_heading(f):
    """ Creates the Abaqus .inp file heading.

    Parameters:
        f (obj): The open file object for the .inp file.

    Returns:
        None
    """
    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** --------------------------------------------------------------------- Heading\n')
    f.write('**\n')
    f.write('*HEADING\n')
    f.write('                               Abaqus input file                                \n')
    f.write('                            SI units: [N, m, kg, s]                             \n')
    f.write('              compas_fea package: Dr Andrew Liew - liew@arch.ethz.ch            \n')
    f.write('**\n')
    f.write('** -----------------------------------------------------------------------------\n')
    f.write('**\n')
    f.write('**\n')
    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ---------------------------------------------------------- Physical constants\n')
    f.write('**\n')
    f.write('*PHYSICAL CONSTANTS, ABSOLUTE ZERO=-273.15, STEFAN BOLTZMANN=5.67e-8\n')
    f.write('**\n')


def input_write_materials(f, materials):
    """ Writes materials to the Abaqus .inp file.

    Parameters:
        f (obj): The open file object for the .inp file.
        materials (dic): Material objects from structure.materials.

    Returns:
        None
    """
    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ------------------------------------------------------------------- Materials\n')

    for key, material in materials.items():

        mtype = material.__name__

        f.write('**\n')
        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')
        f.write('**\n')
        f.write('*MATERIAL, NAME={0}\n'.format(key))

        # Density

        f.write('**\n')
        f.write('*DENSITY\n')

        if isinstance(material.p, list):
            f.write('** p[kg/m3], T[C]\n')
            f.write('**\n')
            for p, T in material.p:
                f.write('{0}, {1}\n'.format(p, T))

        else:
            f.write('** p[kg/m3]\n')
            f.write('**\n')
            f.write('{0}\n'.format(material.p))

        # Elastic

        if mtype == 'ElasticOrthotropic':
            raise NotImplementedError

        elif mtype == 'ThermalMaterial':
            pass

        else:
            f.write('**\n')
            f.write('*ELASTIC\n')
            E = material.E['E']
            v = material.v['v']

            if isinstance(E, list):
                f.write('** E[Pa], v[-], T[C]\n')
                f.write('**\n')
                for j in range(len(E)):
                    f.write('{0}, {1}, {2}\n'.format(E[j][0], v[j][0], E[j][1]))

            else:
                f.write('** E[Pa], v[-]\n')
                f.write('**\n')
                f.write('{0}, {1}\n'.format(E, v))

            if not material.compression:
                f.write('*NO COMPRESSION\n')

            if not material.tension:
                f.write('*NO TENSION\n')

        # Concrete smeared crack

        if mtype in ['ConcreteSmearedCrack', 'Concrete']:

            f.write('**\n')
            f.write('*CONCRETE\n')
            f.write('** f[Pa], e[-] : COMPRESSION\n')
            f.write('**\n')

            compression = material.compression
            for cf, ce in zip(compression['f'], compression['e']):
                f.write('{0}, {1}\n'.format(cf, ce))
            f.write('**\n')
            f.write('*TENSION STIFFENING\n')
            f.write('** f[Pa], e[-] : TENSION\n')
            f.write('**\n')

            tension = material.tension
            for tf, te in zip(tension['f'], tension['e']):
                f.write('{0}, {1}\n'.format(tf, te))
            f.write('**\n')
            f.write('*FAILURE RATIOS\n')
            a, b = material.fratios
            f.write('{0}, {1}\n'.format(a, b))

        # Concrete damaged plasticity

        elif mtype == 'ConcreteDamagedPlasticity':

            f.write('**\n')
            f.write('*CONCRETE DAMAGED PLASTICITY\n')
            f.write('** psi[deg], e[-], sr[-], Kc[-], mu[-]\n')
            f.write('**\n')
            f.write(', '.join([str(i) for i in material.damage]) + '\n')
            f.write('**\n')

            f.write('*CONCRETE COMPRESSION HARDENING\n')
            f.write('** fy[Pa], eu[-], , T[C]\n')
            f.write('**\n')
            for i in material.hardening:
                f.write(', '.join([str(j) for j in i]) + '\n')
            f.write('**\n')

            f.write('*CONCRETE TENSION STIFFENING, TYPE=GFI\n')
            f.write('** ft[Pa], et[-], etd[1/s], T[C]\n')
            f.write('**\n')
            for i in material.stiffening:
                f.write(', '.join([str(j) for j in i]) + '\n')

        # Plastic

        elif mtype in ['ElasticPlastic', 'Steel']:

            f.write('**\n')
            f.write('*PLASTIC\n')
            f.write('** f[Pa], e[-] : COMPRESSION-TENSION\n')
            f.write('**\n')

            tension = material.tension
            for i, j in zip(tension['f'], tension['e']):
                f.write('{0}, {1}\n'.format(i, j))

        # Thermal

        elif mtype == 'ThermalMaterial':

            f.write('**\n')
            f.write('*CONDUCTIVITY\n')
            f.write('** k[W/mK]\n')
            f.write('**\n')
            for i in material.conductivity:
                f.write(', '.join([str(j) for j in i]) + '\n')

            f.write('**\n')
            f.write('*SPECIFIC HEAT\n')
            f.write('** c[J/kgK]\n')
            f.write('**\n')
            for i in material.sheat:
                f.write(', '.join([str(j) for j in i]) + '\n')

        f.write('**\n')


def input_write_misc(f, misc):
    """ Writes misc class info to the Abaqus .inp file.

    Parameters:
        f (obj): The open file object for the .inp file.
        misc (dic): Misc objects from structure.misc.

    Returns:
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


def input_write_nodes(f, nodes, units):
    """ Writes the nodal co-ordinates information to the Abaqus .inp file.

    Note:
        - Node set 'nset_all' is automatically created containing all nodes.

    Parameters:
        f (obj): The open file object for the .inp file.
        nodes (dic): Node dictionary from structure.nodes.
        units (str): Units of the nodal co-ordinates.

    Returns:
        None
    """
    cl = {'m': 1., 'cm': 0.01, 'mm': 0.001}

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ----------------------------------------------------------------------- Nodes\n')
    f.write('**\n')
    f.write('*NODE, NSET=nset_all\n')
    f.write('** No., x[m], y[m], z[m]\n')
    f.write('**\n')

    for key in sorted(nodes, key=int):

        xyz = [str(nodes[key][i] * cl[units]) for i in 'xyz']
        f.write(', '.join([str(key + 1)] + xyz) + '\n')

    f.write('**\n')


def input_write_properties(f, sections, properties, elements, sets):
    """ Writes the section information to the Abaqus .inp file.

    Parameters:
        f (obj): The open file object for the .inp file.
        sections (dic): Section objects from structure.sections.
        properties (dic): ElementProperties objects from structure.element_properties.
        elements (dic): Element objects from structure.elements.
        sets (dic): Sets from structure.sets.

    Returns:
        None
    """

    # Sections

    sdata = {
        'AngleSection':       {'name': 'L',           'geometry': ['b', 'h', 't', 't']},
        'BoxSection':         {'name': 'BOX',         'geometry': ['b', 'h', 'tw', 'tf', 'tw', 'tf']},
        'CircularSection':    {'name': 'CIRC',        'geometry': ['r']},
        'ISection':           {'name': 'I',           'geometry': ['c', 'h', 'b', 'b', 'tf', 'tf', 'tw']},
        'PipeSection':        {'name': 'PIPE',        'geometry': ['r', 't']},
        'RectangularSection': {'name': 'RECTANGULAR', 'geometry': ['b', 'h']},
        'TrapezoidalSection': {'name': 'TRAPEZOID',   'geometry': ['b1', 'h', 'b2', 'c']},
        'GeneralSection':     {'name': 'GENERAL',     'geometry': ['A', 'I11', 'I12', 'I22', 'J', 'g0', 'gw']},
        'ShellSection':       {'name': None,          'geometry': ['t']},
        'SolidSection':       {'name': None,          'geometry': None},
        'TrussSection':       {'name': None,          'geometry': ['A']}}
    shells = ['ShellSection']
    solids = ['SolidSection', 'TrussSection']

    # Write data

    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** -------------------------------------------------------------------- Sections\n')

    written_springs = []

    for key, property in properties.items():

        material = property.material
        elsets = property.elsets
        reinforcement = property.reinforcement
        section = sections[property.section]
        stype = section.__name__
        geometry = section.geometry
        if geometry:
            sname = sdata[stype]['name']

        f.write('**\n')
        f.write('** Section: {0}\n'.format(key))
        f.write('** ---------' + '-' * (len(key)) + '\n')
        f.write('**\n')

        if isinstance(elsets, str):
            elsets = [elsets]

        for elset in elsets:
            explode = sets[elset]['explode']
            selection = sets[elset]['selection']

            # Springs

            if stype == 'SpringSection':

                if explode:
                    for select in selection:
                        e1 = 'element_{0}'.format(select)
                        behaviour = 'BEH_{0}'.format(section.name)
                        f.write('*CONNECTOR SECTION, ELSET={0}, BEHAVIOR=BEH_{1}\n'.format(e1, section.name))
                        f.write('AXIAL\n')
                        f.write('ORI_{0}_{1}\n'.format(select, section.name))
                        f.write('**\n')
                        f.write('*ORIENTATION, NAME=ORI_{0}_{1}\n'.format(select, section.name))
                        ey = elements[select].axes.get('ey', None)
                        ez = elements[select].axes.get('ez', None)
                        f.write(', '.join([str(j) for j in ez]) + ', ')
                        f.write(', '.join([str(j) for j in ey]) + '\n')
                        f.write('**\n')

                        if behaviour not in written_springs:
                            f.write('*CONNECTOR BEHAVIOR, NAME=BEH_{0}\n'.format(section.name))
                            f.write('**\n')
                            if section.stiffness:
                                f.write('*CONNECTOR ELASTICITY, COMPONENT=1\n')
                                f.write('{0}\n'.format(section.stiffness))
                            else:
                                f.write('*CONNECTOR ELASTICITY, COMPONENT=1, NONLINEAR\n')
                                for i, j in zip(section.forces, section.displacements):
                                    f.write('{0}, {1}\n'.format(i, j))
                            written_springs.append(behaviour)
                else:
                    pass

            # Beam sections

            elif (stype not in shells) and (stype not in solids):

                if explode:
                    for select in selection:
                        if stype == 'GeneralSection':
                            f.write('*BEAM GENERAL SECTION')
                        else:
                            f.write('*BEAM SECTION')
                        e1 = 'element_{0}'.format(select)
                        f.write(', SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(sname, e1, material))
                        f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')

                        ex = elements[select].axes.get('ex', None)
                        if ex:
                            f.write(', '.join([str(j) for j in ex]) + '\n')
                        f.write('**\n')

                else:
                    if stype == 'GeneralSection':
                        f.write('*BEAM GENERAL SECTION')
                    else:
                        f.write('*BEAM SECTION')
                    f.write(', SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(sname, elset, material))
                    f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')

            # Shell sections

            elif stype in shells:

                if explode:
                    for select in selection:
                        e1 = 'element_{0}'.format(select)
                        f.write('*SHELL SECTION, ELSET={0}, MATERIAL={1}\n'.format(e1, material))
                        f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')

                else:
                    f.write('*SHELL SECTION, ELSET={0}, MATERIAL={1}\n'.format(elset, material))
                    f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')

                    # Reinforcement

                    if reinforcement:
                        f.write('**\n')
                        for name, rebar in reinforcement.items():
                            pos = rebar['pos']
                            spacing = rebar['spacing']
                            rmaterial = rebar['material']
                            angle = rebar['angle']
                            dia = rebar['dia']
                            A = 0.25 * pi * dia**2
                            # orientation = reinforcement['orientation']
                            # if orientation:
                            # pass
                            # f.write('*REBAR LAYER, ORIENTATION=ORIENT_{0}\n'.format(element))
                            # else:
                            f.write('*REBAR LAYER\n')
                            f.write('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(name, A, spacing, pos, rmaterial, angle))
                            # if orientation:
                            # pass
                            # f.write('*ORIENTATION, SYSTEM=RECTANGULAR, NAME=ORIENT_{0}\n'.format(element))
                            # ex, ey, origin point
                            f.write('**\n')

            # Solid sections

            elif stype in solids:

                f.write('*SOLID SECTION, ELSET={0}, MATERIAL={1}\n'.format(elset, material))
                if stype == 'TrussSection':
                    f.write('{0}\n'.format(geometry['A']))

        f.write('**\n')


def input_write_sets(f, sets):
    """ Creates the Abaqus .inp file node sets NSETs and element sets ELSETs.

    Note:
        - Restriction in Abaqus to 10 entries written per line in the .inp file.

    Parameters:
        f (obj): The open file object for the .inp file.
        sets (dic): Sets dictionary from structure.sets.

    Returns:
        None
    """
    cm = 9
    for key, set in sets.items():

        stype = set['type']

        f.write('**\n')
        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')
        f.write('**\n')

        if stype in ['node', 'element', 'surface_node']:

            if stype == 'node':
                f.write('*NSET, NSET={0}\n'.format(key))

            elif stype == 'element':
                f.write('*ELSET, ELSET={0}\n'.format(key))

            elif stype == 'surface_node':
                f.write('*SURFACE, TYPE=NODE, NAME={0}\n'.format(key))

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


def input_write_steps(f, structure, steps, loads, displacements, interactions, misc, fields):
    """ Writes step information to the Abaqus .inp file.

    Note:
        - Steps are analysed in the order given by structure.steps_order.

    Parameters:
        f (obj): The open file object for the .inp file.
        structure (obj): Struture object.
        steps (dic): Step objects from structure.steps.
        loads (dic): Load objects from structure.loads.
        displacements (dic): Displacement objects from structure.displacements.
        interactions (dic): Interaction objects from structure.interactions.
        misc (dic): Misc objects from structure.misc.
        fields (list): Data field requests.

    Returns:
        None
    """
    f.write('** -----------------------------------------------------------------------------\n')
    f.write('** ----------------------------------------------------------------------- Steps\n')

    dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']

    for key in structure.steps_order:

        step = steps[key]
        stype = step.__name__
        increments = step.increments
        method = step.type

        f.write('**\n')
        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')
        f.write('**\n')

        # Mechanical

        if stype in ['GeneralStep', 'BucklingStep']:

            # Header

            if stype == 'BucklingStep':
                nlgeom = 'NO'
            else:
                nlgeom = 'YES' if step.nlgeom else 'NO'
            perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''
            lf = step.factor
            f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
            f.write('*{0}\n'.format(method.upper()))
            f.write('**\n')

            # Modes

            if stype == 'BucklingStep':

                modes = step.modes
                f.write('{0}, {1}, {2}, {3}\n'.format(modes, modes, 2 * modes, increments))

            # Loads

            for k in step.loads:

                load = loads[k]
                ltype = load.__name__
                com = load.components
                axes = load.axes
                nset = load.nodes
                elset = load.elements

                f.write('**\n')
                f.write('** {0}\n'.format(k))
                f.write('** ' + '-' * len(k) + '\n')
                f.write('**\n')

                # Type

                if ltype in ['PointLoad', 'TributaryLoad']:
                    f.write('*CLOAD\n')
                    f.write('** NSET, dof, CLOAD\n')

                if ltype in ['LineLoad', 'AreaLoad', 'GravityLoad', 'BodyLoad']:
                    f.write('*DLOAD\n')
                    f.write('** ELSET, component, DLOAD\n')

                f.write('**\n')

                # Point load

                if ltype == 'PointLoad':

                    for c, dof in enumerate(dofs, 1):
                        if com[dof]:
                            f.write('{0}, {1}, {2}'.format(nset, c, lf * com[dof]) + '\n')

                # Line load

                elif ltype == 'LineLoad':

                    if axes == 'global':
                        for dof in dofs[:3]:
                            if com[dof]:
                                f.write('{0}, P{1}, {2}'.format(elset, dof.upper(), lf * com[dof]) + '\n')

                    elif axes == 'local':
                        if com['x']:
                            f.write('{0}, P1, {1}'.format(elset, lf * com['x']) + '\n')
                        if com['y']:
                            f.write('{0}, P2, {1}'.format(elset, lf * com['y']) + '\n')

                # Area load

                elif ltype == 'AreaLoad':

                    if axes == 'global':
                        raise NotImplementedError

                    elif axes == 'local':
                        # x COMPONENT
                        # y COMPONENT
                        if com['z']:
                            f.write('{0}, P, {1}'.format(elset, lf * com['z']) + '\n')

                # Body load

                elif ltype == 'BodyLoad':
                    raise NotImplementedError

                # Gravity load

                elif ltype == 'GravityLoad':

                    g = load.g
                    gx = 1 if com['x'] else 0
                    gy = 1 if com['y'] else 0
                    gz = 1 if com['z'] else 0
                    f.write('{0}, GRAV, {1}, {2}, {3}, {4}\n'.format(elset, lf * g, gx, gy, gz))

                # Tributary load

                elif ltype == 'TributaryLoad':

                    for node in sorted(com, key=int):
                        for c, dof in enumerate(dofs[:3], 1):
                            if com[node][dof]:
                                ni = node + 1
                                dl = com[node][dof] * lf
                                f.write('{0}, {1}, {2}\n'.format(ni, c, dl))

            # Displacements

            for k in step.displacements:

                displacement = displacements[k]
                com = displacement.components
                nset = displacement.nodes

                f.write('**\n')
                f.write('** {0}\n'.format(k))
                f.write('** ' + '-' * len(k) + '\n')
                f.write('**\n')
                f.write('*BOUNDARY\n')
                f.write('** NSET, dof.start, dof.end, displacement\n')
                f.write('**\n')

                for c, dof in enumerate(dofs, 1):
                    if com[dof] is not None:
                        f.write('{0}, {1}, {1}, {2}\n'.format(nset, c, com[dof] * lf))

            # Temperatures

            # try:
            #     duration = step.duration
            # except:
            #     duration = 1
            #     temperatures = steps[key].temperatures
            #     if temperatures:
            #         file = misc[temperatures].file
            #         einc = str(misc[temperatures].einc)
            #         f.write('**\n')
            #         f.write('*TEMPERATURE, FILE={0}, BSTEP=1, BINC=1, ESTEP=1, EINC={1}, INTERPOLATE\n'.format(file, einc))

            # fieldOutputs

            f.write('**\n')
            f.write('** Output\n')
            f.write('** ------\n')
            f.write('**\n')
            f.write('*OUTPUT, FIELD\n')
            f.write('**\n')

            if isinstance(fields, list):
                fields = structure.fields_dic_from_list(fields)
            if 'spf' in fields:
                fields['ctf'] = 'all'
                del fields['spf']

            f.write('*NODE OUTPUT\n')
            if fields == 'all':
                f.write(', '.join([i.upper() for i in node_fields]) + '\n')
            else:
                f.write(', '.join([i.upper() for i in node_fields if i in fields]) + '\n')
            f.write('**\n')

            f.write('*ELEMENT OUTPUT\n')
            if fields == 'all':
                f.write(', '.join([i.upper() for i in element_fields]) + '\n')
            else:
                f.write(', '.join([i.upper() for i in element_fields if (i in fields and i != 'rbfor')]) + '\n')
            f.write('**\n')

            if (fields == 'all') or ('rbfor' in fields):
                f.write('*ELEMENT OUTPUT, REBAR\n')
                f.write('RBFOR\n')
            f.write('**\n')

            f.write('*END STEP\n')

        # Thermal

        # elif stype == 'HeatStep':
        #     temp0 = step.temp0
        #     duration = step.duration
        #     deltmx = steps[key].deltmx
        #     interaction = interactions[step.interaction]
        #     amplitude = interaction.amplitude
        #     interface = interaction.interface
        #     sink_t = interaction.sink_t
        #     film_c = interaction.film_c
        #     ambient_t = interaction.ambient_t
        #     emissivity = interaction.emissivity

        #     # Initial T

        #     f.write('*INITIAL CONDITIONS, TYPE=TEMPERATURE\n')
        #     f.write('NSET_ALL, {0}\n'.format(temp0))
        #     f.write('**\n')

        #     # Interface

        #     f.write('*STEP, NAME={0}, INC={1}\n'.format(sname, increments))
        #     f.write('*{0}, END=PERIOD, DELTMX={1}\n'.format(method, deltmx))
        #     f.write('1, {0}, 5.4e-05, {0}\n'.format(duration))
        #     f.write('**\n')
        #     f.write('*SFILM, AMPLITUDE={0}\n'.format(amplitude))
        #     f.write('{0}, F, {1}, {2}\n'.format(interface, sink_t, film_c))
        #     f.write('**\n')
        #     f.write('*SRADIATE, AMPLITUDE={0}\n'.format(amplitude))
        #     f.write('{0}, R, {1}, {2}\n'.format(interface, ambient_t, emissivity))

        #     # fieldOutputs

        #     f.write('**\n')
        #     f.write('** OUTPUT\n')
        #     f.write('** ------\n')
        #     f.write('*OUTPUT, FIELD\n')
        #     f.write('**\n')
        #     f.write('*NODE OUTPUT\n')
        #     f.write('NT\n')
        #     f.write('**\n')
        #     f.write('*END STEP\n')

        f.write('**\n')
