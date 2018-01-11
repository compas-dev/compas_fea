"""
compas_fea.fea.sofistik : Sofistik specific functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
    'input_write_heading',
    'input_write_materials',
    'input_write_nodes_elements',
    'input_write_rebar',
]


dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']
fixitys = ['PX', 'PY', 'PZ', 'MX', 'MY' 'MZ']


def input_generate(structure, fields, units='m'):
    """ Creates the Sofistik .dat file from the Structure object.

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
    filename = '{0}{1}.dat'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

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

        urs = 0

        input_write_heading(f)
        urs = input_write_materials(f, materials, urs)
        urs = input_write_nodes_elements(f, structure, nodes, elements, sections, properties, materials, sets, steps,
                                         displacements, units, urs)
        urs = input_write_rebar(f, properties, sections, sets, urs)
        urs = input_write_steps(f, structure, steps, loads, displacements, urs)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))


def input_write_heading(f):
    """ Creates the Sofistik .dat file heading.

    Parameters
    ----------
    f : obj
        The open file object for the .dat file.

    Returns
    -------
    None
    """
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ --------------------------------------------------------------------- Heading\n')
    f.write('$\n')
    f.write('$                           Sofistik input file                                \n')
    f.write('$                          SI units: [kN, m, kg, s]                             \n')
    f.write('$            compas_fea package: Dr Andrew Liew - liew@arch.ethz.ch            \n')
    f.write('$\n')
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('\n')
    f.write('\n')

    f.write('$ UNITS ARE IN kN FOR FORCE!!\n')


def input_write_materials(f, materials, urs):
    """ Writes materials to the Sofistik .dat file.

    Parameters
    ----------
    f : obj
        The open file object for the .dat file.
    materials : dic
        Material objects from structure.materials.

    Returns
    -------
    None
    """
    urs += 1

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ------------------------------------------------------------------- Materials\n')
    f.write('\n')
    f.write('+PROG AQUA urs:{0}\n'.format(urs))
    f.write('\n')
    f.write('HEAD AQUA\n')
    f.write('NORM DC SIA NDC 262\n')

    for key, material in materials.items():

        mtype = material.__name__
        material_index = material.index + 1

        f.write('\n')
        f.write('$ {0}\n'.format(key))
        f.write('$ ' + '-' * len(key) + '\n')
        f.write('\n')

        if mtype == 'Concrete':

            fck = material.fck
            v = material.v['v']
            yc = material.p / 100
            f.write('CONC {0} TYPE C FCN {1} MUE {2} GAM {3} TYPR C\n'.format(material_index, fck, v, yc))

        if mtype == 'Steel':

            if material.id == 's':
                id = 'S'
            elif material.id == 'r':
                id = 'B'
            fy = material.fy
            fu = material.fu
            sf = material.sf
            E = material.E['E'] / 10**6
            v = material.v['v']
            ys = material.p / 100
            eyp = 1000 * fy / E
            eup = 10 * material.eu
            f.write('STEE {0} {1} ES {2} GAM {3} FY {4} FT {5} FP {4} SCM {6} EPSY {7} EPST {8} MUE {9}\n'.format(
                material_index, id, E, ys, fy, fu, sf, eyp, eup, v))

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')

    return urs


def input_write_nodes_elements(f, structure, nodes, elements, sections, properties, materials, sets, steps,
                               displacements, units, urs):
    """ Writes the nodal co-ordinates and element information to the Sofistik .dat file.

    Parameters
    ----------
    f : obj
        The open file object for the .dat file.
    structure : obj
        The Structure object.
    nodes : dic
        Node dictionary from structure.nodes.
    elements : dic
        Element dictionary from structure.elements.
    sections : dic
        Section objects from structure.sections.
    properties : dic
        ElementProperties objects from structure.element_properties.
    materials : dic
        Material objects from structure.materials.
    sets : dic
        Sets dictionary from structure.sets.
    steps : dic
        Step objects from structure.steps.
    displacements : dic
        Displacement objects from structure.displacements.
    units : str
        Units of the nodal co-ordinates.

    Returns
    -------
    None
    """
    urs += 1

    cl = {'m': 1., 'cm': 0.01, 'mm': 0.001}

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ---------------------------------------------------------- Nodes and elements\n')
    f.write('\n')
    f.write('+PROG SOFIMSHA urs:{0}\n'.format(urs))
    f.write('\n')
    f.write('HEAD SOFIMSHA\n')
    f.write('UNIT 0\n')
    f.write('SYST 3D GDIR POSX,POSY,NEGZ\n')
    f.write('CTRL OPT OPTI 10\n')
    f.write('\n')

    # Nodes
    # -----

    f.write('NODE NO X Y Z\n')
    f.write('$ No., x[m], y[m], z[m]\n')
    f.write('\n')

    for key in sorted(nodes, key=int):

        xyz = [str(nodes[key][i] * cl[units]) for i in 'xyz']
        f.write(' '.join([str(key + 1)] + xyz) + '\n')

    # Properties
    # ----------

    for key, property in properties.items():

        if isinstance(property.elsets, str):
            elsets = [property.elsets]

        material_index = materials[property.material].index + 1
        geometry = sections[property.section].geometry
        reinforcement = property.reinforcement
        rebar_index = materials[reinforcement.values()[0]['material']].index + 1
        # assumes all layers have same material

        for elset in elsets:
            for select in sets[elset]['selection']:
                elements[select].material_index = material_index
                elements[select].geometry = geometry

    # Elements
    # --------

    etypes = ['QUAD']
    edic = {i: [] for i in etypes}

    for ekey in sorted(elements, key=int):

        element = elements[ekey]
        nodes = [node + 1 for node in element.nodes]
        data = [element.number + 1] + nodes + [element.material_index]
        geometry = element.geometry
        etype = element.__name__

        if etype == 'ShellElement':
            if len(nodes) == 4:
                estr = 'QUAD'
                data.extend([geometry['t']] * 4)
            if reinforcement:
                data.append(rebar_index)

        edic[estr].append(data)

    for key, edata in edic.items():

        if edata:
            f.write('\n')
            f.write('$ {0}\n'.format(key))
            f.write('$ ' + '-' * len(key) + '\n')
            f.write('\n')

            if key == 'QUAD':
                # f.write('POSI KR\n')
                f.write('QUAD NO N1 N2 N3 N4 MNO T1 T2 T3 T4')
                if reinforcement:
                    f.write(' MRF')
                f.write('\n')
                f.write('$ No. node.1 node.2 node.3 node.4 material.index t.1[m] t.2[m] t.3[m] t.4[m]')
                if reinforcement:
                    f.write(' rebar.index')
                f.write('\n\n')

            for j in edata:
                f.write('{0}\n'.format(' '.join([str(i) for i in j])))

    # Boundary conditions
    # -------------------

    key = structure.steps_order[0]
    step = steps[key]
    stype = step.__name__

    f.write('\n')
    f.write('$ {0}\n'.format(key))
    f.write('$ ' + '-' * len(key) + '\n')

    # Mechanical

    if stype in ['GeneralStep']:

        # Displacements

        for k in step.displacements:
            displacement = displacements[k]
            com = displacement.components
            nset = displacement.nodes

            f.write('\n')
            f.write('$ {0}\n'.format(k))
            f.write('$ ' + '-' * len(k) + '\n')
            f.write('\n')
            f.write('NODE NO FIX\n')
            f.write('$ node fixity\n')
            f.write('\n')

            j = ''
            for dof, fixity in zip(dofs, fixitys):
                if com[dof] == 0:
                    j += fixity

            for node in sorted(sets[nset]['selection'], key=int):
                f.write('{0} {1}\n'.format(node + 1, j))

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')

    return urs


def input_write_rebar(f, properties, sections, sets, urs):
    """ Writes any reinforcement properties.

    Parameters
    ----------
    f : obj
        The open file object for the .dat file.
    properties : dic
        ElementProperties objects from structure.element_properties.
    sections : dic
        Section objects from structure.sections.
    sets : dic
        Sets dictionary from structure.sets.

    Returns
    -------
    None
    """
    urs += 1

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ --------------------------------------------------------------- Reinforcement\n')
    f.write('\n')
    f.write('+PROG BEMESS urs:{0}\n'.format(urs))
    f.write('\n')
    f.write('HEAD BEMESS\n')
    f.write('\n')
    f.write('CTRL WARN 7\n')  # Upper cover (<10mm or >0.70d)
    f.write('CTRL WARN 9\n')  # Bottom cover (<10mm or >0.70d)
    f.write('\n')

    # Properties
    # ----------

    for key, property in properties.items():

        reinforcement = property.reinforcement

        if reinforcement:

            f.write('$ Reinforcement: {0}\n'.format(key))
            f.write('$ ---------------' + '-' * (len(key)) + '\n')
            f.write('\n')

            t = sections[property.section].geometry['t']
            geom = 'GEOM'
            posu, posl = [], []
            du, dl = [], []
            Au, Al = [], []

            for name, rebar in reinforcement.items():
                pos = rebar['pos']
                dia = rebar['dia']
                spacing = rebar['spacing']
                # angle = rebar['angle']
                Ac = 0.25 * pi * (dia * 100)**2
                Apm = Ac / spacing
                if pos > 0:
                    posu.append(pos)
                    du.append(dia)
                    Au.append(Apm)
                elif pos < 0:
                    posl.append(pos)
                    dl.append(dia)
                    Al.append(Apm)

            if len(posu) == 1:
                geom += ' HA {0}[mm]'.format((0.5 * t - posu[0]) * 1000)
                DU = du[0] * 1000
                ASU = Au[0]
                BSU = Au[0]
            elif len(posu) == 2:
                pass

            if len(posl) == 1:
                geom += ' HB {0}[mm]'.format((0.5 * t + posl[0]) * 1000)
                DL = dl[0] * 1000
                ASL = Al[0]
                BSL = Al[0]
            elif len(posu) == 2:
                pass

            f.write(geom + '\n')
            f.write('\n')

            if isinstance(property.elsets, str):
                elsets = [property.elsets]

            for elset in elsets:
                for select in sets[elset]['selection']:
                    noel = select + 1
                    # f.write('PARA WKU 0.1[mm] WKL 0.1[mm]\n')
                    f.write('PARA NOG -\n')
                    f.write('PARA NOEL {0} DU {1}[mm] ASU {2}[cm2/m] BSU {3}[cm2/m] DL {4}[mm] ASL {5}[cm2/m] BSL {6}[cm2/m] \n'.format(noel, DU, ASU, BSU, DL, ASL, BSL))

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')

    # DHA = (0.5 * t - min(pos_pos)) * 1000
    # DHB =  (0.5 * t + max(pos_neg)) * 1000

    return urs


def input_write_steps(f, structure, steps, loads, displacements, urs):
    """ Writes step information to the Sofistik .dat file.

    Parameters
    ----------
    f : obj
        The open file object for the .dat file.
    structure : obj
        Struture object.
    steps : dic
        Step objects from structure.steps.
    loads : dic
        Load objects from structure.loads.
    displacements : dic
        Displacement objects from structure.displacements.

    Returns
    -------
    None

    Notes
    -----
    - Steps are analysed in the order given by structure.steps_order.
    """
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ----------------------------------------------------------------------- Steps\n')

    for key in structure.steps_order[1:]:  # assuming first step used already in BC

        urs += 1

        step = steps[key]
        lf = step.factor
        # stype = step.__name__

        f.write('\n')
        f.write('$ {0}\n'.format(key))
        f.write('$ ' + '-' * len(key) + '\n')
        f.write('\n')

        f.write('+PROG ASE urs:{0}\n'.format(urs))
        f.write('HEAD ASE\n')
        f.write('\n')

        f.write('CTRL SOLV 1\n')

        for key, load in loads.items():

            load_index = load.index + 1
            ltype = load.__name__
            com = load.components

            f.write('\n')
            f.write('$ {0}\n'.format(key))
            f.write('$ ' + '-' * len(key) + '\n')
            f.write('\n')

            if ltype == 'GravityLoad':

                components = ''
                if com['x']:
                    components += ' DLX {0}'.format(com['x'] * lf)
                if com['y']:
                    components += ' DLY {0}'.format(com['y'] * lf)
                if com['z']:
                    components += ' DLZ {0}'.format(com['z'] * lf)
                f.write("LC {0} TITL '{1}'{2}\n".format(load_index, key, components))


        f.write('\n')
        f.write('END\n')
        f.write('\n')
        f.write('\n')

    return urs

# QUAD GRP 1 TYPE PZZ 0.535  $ in kN/m2
# CTRL ITER V4 10
# CTRL CONC V4
# SYST PROB TH3 ITER 200 TOL 0.010 FMAX 1.1 NMAT YES
# REIQ LCR 4
