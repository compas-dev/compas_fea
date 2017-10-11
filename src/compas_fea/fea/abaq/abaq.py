"""
compas_fea.fea.abaq : Abaqus .inp file creator.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas_fea.fea.abaq import odb

from subprocess import Popen
from subprocess import PIPE

from math import pi

import json
import os


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'abaqus_launch_process',
    'inp_write_constraints',
    'inp_write_elements',
    'inp_generate',
    'inp_write_heading',
    'inp_write_materials',
    'inp_write_misc',
    'inp_write_nodes',
    'inp_write_properties',
    'inp_write_sets',
    'inp_write_steps'
]


def abaqus_launch_process(structure, path, name, exe, fields, cpus):
    """ Runs the analysis through the chosen FEA software/library.

    Parameters:
        structure (obj): Structure object.
        path (str): Folder to save data.
        name (str): Name of the Structure object and analysis files.
        exe (str): Full terminal command to bypass subprocess defaults.
        fields (str): Data fields to extract e.g 'U,S,SM'.
        cpus (int): Number of CPU cores to use.

    Returns:
        None
    """

    # Create temp folder

    temp = '{0}{1}/'.format(path, name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Save node data

    nkeys = sorted(structure.nodes, key=int)
    nodes = {nkey: structure.node_xyz(nkey) for nkey in nkeys}
    with open('{0}{1}-nodes.json'.format(temp, name), 'w') as f:
        json.dump(nodes, f)

    # Save elements' nodes data

    ekeys = sorted(structure.elements, key=int)
    elements = {ekey: structure.elements[ekey].nodes for ekey in ekeys}
    with open('{0}{1}-elements.json'.format(temp, name), 'w') as f:
        json.dump(elements, f)

    # Run sub-process odb.py file

    odb_loc = odb.__file__
    subprocess = 'noGUI=' + odb_loc.replace('\\', '/')

    success = False
    if not exe:
        args = ['abaqus', 'cae', subprocess, '--', fields, str(cpus), temp, path, name]
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
                print('***** Attempting to read .msg log *****')
                with open('{0}{1}.msg'.format(temp, name)) as f:
                    lines = f.readlines()
                    for c, line in enumerate(lines):
                        if (' ***ERROR' in line) or (' ***WARNING' in line):
                            print(lines[c][:-2])
                            print(lines[c + 1][:-2])
            except:
                print('***** Loading .msg log failed *****')
            try:
                print('***** Attempting to read abaqus.rpy log *****')
                with open('{0}abaqus.rpy'.format(path)) as f:
                    lines = f.readlines()
                    for c, line in enumerate(lines):
                        if '#: ' in line:
                            print(lines[c])
            except:
                print('***** Loading abaqus.rpy log failed *****')
        else:
            print('***** Analysis successful *****')

    else:
        args = '{0} -- {1} {2} {3} {4} {5}'.format(subprocess, fields, cpus, temp, path, name)
        os.chdir(temp)
        os.system('{0}{1}'.format(exe, args))

    # Store data

    try:
        with open('{0}{1}-results.json'.format(temp, name), 'r') as f:
            structure.results = json.load(f)
        structure.save_to_obj('{0}{1}.obj'.format(path, name))
        print('***** Saving data to structure.results successful *****')
    except:
        print('***** Saving data to structure.results unsuccessful *****')


def inp_write_constraints(f, constraints):
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
        f.write('** {0}\n'.format(key))
        f.write('** ' + '-' * len(key) + '\n')
        ctype = constraint.__name__

        # Tie constraint

        if ctype == 'TieConstraint':
            tol = constraint.tol
            slave = constraint.slave
            master = constraint.master
            f.write('*TIE, POSITION TOLERANCE={0}, NAME={1}, ADJUST=NO\n'.format(tol, key))
            f.write('** SLAVE, MASTER\n')
            f.write('{0}, {1}\n'.format(slave, master))

    f.write('**\n')


def inp_write_elements(f, elements):
    """ Writes the element information to the Abaqus .inp file.

    Note:
        - T3D2  truss    2 nodes elset_T3D2.
        - B31   beam     2 nodes elset_B31.
        - S3    shell    3 nodes elset_S3.
        - S4    shell    4 nodes elset_S4.
        - M3D3  membrane 3 nodes elset_M3D3.
        - M3D4  membrane 4 nodes elset_M3D4.
        - C3D4  solid    4 nodes elset_C3D4.
        - C3D6  solid    6 nodes elset_C3D6.
        - C3D8  solid    8 nodes elset_C3D8.
        - DC3D4 solid    4 nodes elset_DC3D4 thermal.
        - DC3D6 solid    6 nodes elset_DC3D6 thermal.
        - DC3D8 solid    8 nodes elset_DC3D8 thermal.

    Parameters:
        f (obj): The open file object for the .inp file.
        elements (dic): Elements from structure.elements.

    Returns:
        None
    """

    # Sort elements

    etypes = ['T3D2', 'B31', 'S3', 'S4', 'M3D3', 'M3D4', 'C3D4', 'C3D6', 'C3D8', 'DC3D4', 'DC3D6', 'DC3D8']
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
        if element.thermal:
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


def inp_generate(structure, filename, units='m'):
    """ Creates the Abaqus .inp file from the Structure object.

    Parameters:
        structure (obj): The Structure object to read from.
        filename (str): Path to save the .inp file to.
        units (str): Units of the nodal co-ordinates 'm','cm','mm'.

    Returns:
        None
    """
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

        inp_write_heading(f)
        inp_write_nodes(f, nodes, units)
        inp_write_elements(f, elements)
        inp_write_sets(f, sets)
        inp_write_materials(f, materials)
        inp_write_misc(f, misc)
        inp_write_properties(f, sections, properties, elements, sets)
        inp_write_constraints(f, constraints)
        inp_write_steps(f, structure, steps, loads, displacements, interactions, misc)

    print('***** Abaqus input file generated: {0} *****\n'.format(filename))


def inp_write_heading(f):
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
    f.write('                               ABAQUS input file                                \n')
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


def inp_write_materials(f, materials):
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
            compression = material.compression
            for i, j in zip(compression['f'], compression['e']):
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


def inp_write_misc(f, misc):
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


def inp_write_nodes(f, nodes, units):
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


def inp_write_properties(f, sections, properties, elements, sets):
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
    for key, property in properties.items():
        material = property.material
        elsets = property.elsets
        reinforcement = property.reinforcement
        section = sections[property.section]
        stype = section.__name__
        geometry = section.geometry

        f.write('**\n')
        f.write('** Section: {0}\n'.format(key))
        f.write('** --------' + '-' * (len(key)) + '\n')
        f.write('**\n')

        if isinstance(elsets, str):
            elsets = [elsets]
        for elset in elsets:

            # Beam sections

            if (stype not in shells) and (stype not in solids):
                s1 = sdata[stype]['name']
                if sets[elset]['explode']:
                    for select in sets[elset]['selection']:
                        e1 = 'element_{0}'.format(select)
                        f.write('*BEAM SECTION, SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(s1, e1, material))
                        f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')
                        ex = elements[select].axes.get('ex', None)
                        if ex:
                            f.write(', '.join([str(j) for j in ex]) + '\n')
                        f.write('**\n')
                else:
                    if stype == 'GeneralSection':
                        f.write('*BEAM GENERAL SECTION, SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(s1, elset, material))
                    else:
                        f.write('*BEAM SECTION, SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(s1, elset, material))
                    f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')

            # Shell sections

            elif stype in shells:
                if sets[elset]['explode']:
                    for select in sets[elset]['selection']:
                        e1 = 'element_{0}'.format(select)
                        f.write('*SHELL SECTION, ELSET={0}, MATERIAL={1}\n'.format(e1, material))
                        f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')
                else:
                    f.write('*SHELL SECTION, ELSET={0}, MATERIAL={1}\n'.format(elset, material))
                    f.write(', '.join([str(geometry[j]) for j in sdata[stype]['geometry']]) + '\n')
                    if reinforcement:
                        orientation = reinforcement['orientation']
                        spacing = reinforcement['spacing']
                        offset = reinforcement['offset']
                        rmaterial = reinforcement['material']
                        dia = reinforcement['dia']
                        area = 0.25 * pi * dia**2
                        if orientation:
                            pass
                            # f.write('*REBAR LAYER, ORIENTATION=ORIENT_{0}\n'.format(element))
                        else:
                            f.write('*REBAR LAYER\n')
                        f.write('U1, {0}, {1}, {2}, {3}, {4}\n'.format(area, spacing, +offset, rmaterial, 0))
                        f.write('U2, {0}, {1}, {2}, {3}, {4}\n'.format(area, spacing, +offset - dia, rmaterial, 90))
                        f.write('L1, {0}, {1}, {2}, {3}, {4}\n'.format(area, spacing, -offset, rmaterial, 0))
                        f.write('L2, {0}, {1}, {2}, {3}, {4}\n'.format(area, spacing, -offset + dia, rmaterial, 90))
                        if orientation:
                            pass
                            # f.write('*ORIENTATION, SYSTEM=RECTANGULAR, NAME=ORIENT_{0}\n'.format(element))
                            # ex, ey, origin points
                        f.write('**\n')

            # Solid sections

            elif stype in solids:
                f.write('*SOLID SECTION, ELSET={0}, MATERIAL={1}\n'.format(elset, material))
                if stype == 'TrussSection':
                    f.write('{0}\n'.format(geometry['A']))

        f.write('**\n')


def inp_write_sets(f, sets):
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


def inp_write_steps(f, structure, steps, loads, displacements, interactions, misc):
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

            nlgeom = 'YES' if step.nlgeom else 'NO'
            perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''
            lf = step.factor
            f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
            f.write('*{0}\n'.format(method))

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
                        if com['y']:
                            f.write('{0}, P1, {1}'.format(elset, lf * com['y']) + '\n')
                        if com['z']:
                            f.write('{0}, P2, {1}'.format(elset, lf * com['z']) + '\n')

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
            f.write('*NODE OUTPUT\n')
            f.write('RF, RM, U, UR, CF, CM, NT\n')
            f.write('**\n')
            f.write('*ELEMENT OUTPUT\n')
            f.write('SF, SM, SE, SK, S, E, PE\n')
            f.write('**\n')
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
