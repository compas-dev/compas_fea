"""
compas_fea.fea.sofistik : Sofistik specific functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_heading

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
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

        write_input_heading(f, software='sofistik')
        urs = input_write_materials(f, materials, urs)
        urs = input_write_nodes_elements(f, structure, nodes, elements, sections, properties, materials, sets, steps,
                                         displacements, units, urs)
        urs = input_write_rebar(f, properties, sections, sets, urs)
        urs = input_write_steps(f, structure, steps, loads, displacements, sets, urs)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))


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

    key = structure.steps_order[0]
    step = steps[key]
    stype = step.__name__

    f.write('\n')
    f.write('$ {0}\n'.format(key))
    f.write('$ ' + '-' * len(key) + '\n')

    if stype in ['GeneralStep']:

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

    # Elements
    # --------

    shells = ['ShellSection']

    for key, property in properties.items():

        material_index = materials[property.material].index + 1
        reinforcement = property.reinforcement
        section = sections[property.section]
        geometry = section.geometry
        elsets = property.elsets
        stype = section.__name__
        rebar_index = materials[reinforcement.values()[0]['material']].index + 1
        # assumes all layers have the same material

        f.write('\n')
        f.write('$ Section: {0}\n'.format(key))
        f.write('$ ---------' + '-' * (len(key)) + '\n')
        f.write('\n')

        if isinstance(elsets, str):
            elsets = [elsets]

        for elset in elsets:
            selection = sets[elset]['selection']
            set_index = sets[elset]['index'] + 1

            f.write('GRP {0}\n'.format(set_index))
            f.write('\n')

            # Shell sections

            if stype in shells:

                tris = []
                quads = []
                for select in selection:
                    element = elements[select]
                    nodes = [node + 1 for node in element.nodes]
                    t = geometry['t']
                    data = [select + 1] + nodes + [material_index] + [t] * len(nodes)
                    if reinforcement:
                        data.append(rebar_index)
                    quads.append(data)

                if tris:
                    pass

                if quads:
                    f.write('QUAD NO N1 N2 N3 N4 MNO T1 T2 T3 T4')
                    if reinforcement:
                        f.write(' MRF')
                    f.write('\n')
                    f.write('$ No. node.1 node.2 node.3 node.4 material.index t.1[m] t.2[m] t.3[m] t.4[m]')
                    if reinforcement:
                        f.write(' rebar.index')
                    f.write('\n\n')
                    for quad in quads:
                        f.write('{0}\n'.format(' '.join([str(i) for i in quad])))

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
            posu, posl = [], []
            du, dl = [], []
            Au, Al = [], []

            for name, rebar in reinforcement.items():
                pos = rebar['pos']
                dia = rebar['dia']
                spacing = rebar['spacing']
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

            geom = 'GEOM -'
            data = ''

            if len(posu) == 1:
                geom += ' HA {0}[mm]'.format((0.5 * t - posu[0]) * 1000)
                data += ' DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]'.format(du[0] * 1000, Au[0], Au[0])

            elif len(posu) == 2:
                if posu[0] > posu[1]:
                    no1 = 0
                    no2 = 1
                else:
                    no1 = 1
                    no2 = 0
                DHA = abs(posu[0] - posu[1]) * 1000
                geom += ' HA {0}[mm] DHA {1}[mm]'.format((0.5 * t - posu[no1]) * 1000, DHA)
                data += ' DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]'.format(du[no1] * 1000, Au[no1], Au[no1])
                data += ' DU2 {0}[mm] ASU2 {1}[cm2/m] BSU2 {2}[cm2/m]'.format(du[no2] * 1000, Au[no2], Au[no2])

            if len(posl) == 1:
                geom += ' HB {0}[mm]'.format((0.5 * t + posl[0]) * 1000)
                data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[0] * 1000, Al[0], Al[0])

            elif len(posl) == 2:
                if posl[0] < posl[1]:
                    no1 = 0
                    no2 = 1
                else:
                    no1 = 1
                    no2 = 0
                DHB = abs(posl[0] - posl[1]) * 1000
                geom += ' HB {0}[mm] DHB {1}[mm]'.format((0.5 * t + posl[no1]) * 1000, DHB)
                data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[no1] * 1000, Al[no1], Al[no1])
                data += ' DL2 {0}[mm] ASL2 {1}[cm2/m] BSL2 {2}[cm2/m]'.format(dl[no2] * 1000, Al[no2], Al[no2])

            f.write(geom + '\n')
            f.write('\n')

            if isinstance(property.elsets, str):
                elsets = [property.elsets]

            # f.write('PARA NOG - WKU 0.1[mm] WKL 0.1[mm]\n')
            f.write('PARA NOG -\n')
            for elset in elsets:
                set_index = sets[elset]['index'] + 1
                f.write('PARA NOG {0}{1}\n'.format(set_index, data))

    f.write('\n')
    f.write('END\n')
    f.write('\n')
    f.write('\n')

    return urs


def input_write_steps(f, structure, steps, loads, displacements, sets, urs):
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
    sets : dic
        Sets dictionary from structure.sets.

    Returns
    -------
    None

    Notes
    -----
    - Steps are analysed in the order given by structure.steps_order.
    """

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ----------------------------------------------------------------------- Steps\n')

    for key in structure.steps_order[1:]:

        urs += 1

        f.write('\n')
        f.write('+PROG ASE urs:{0}\n'.format(urs))
        f.write('HEAD ASE\n')
        f.write('\n')

        f.write('\n')
        f.write('$ {0}\n'.format(key))
        f.write('$ ' + '-' * len(key) + '\n')
        f.write('\n')

        step = steps[key]
        step_index = step.index
        factor = step.factor
        stype = step.__name__
        DLX, DLY, DLZ = 0, 0, 0

        f.write('CTRL SOLV 1\n')
        f.write('\n')
        f.write("LC {0} TITL '{1}' FACT {2}".format(step_index, key, factor))

        for lkey in step.loads:

            load = loads[lkey]
            ltype = load.__name__
            com = load.components
            if ltype == 'GravityLoad':
                if com['x']:
                    DLX += com['x'] * factor
                if com['y']:
                    DLY += com['y'] * factor
                if com['z']:
                    DLZ += com['z'] * factor

        f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX, DLY, DLZ))

        for key in step.loads:

            pass
            # load = loads[key]
            # ltype = load.__name__
            # com = load.components
            # elset = load.elements
            # set_index = sets[elset]['index'] + 1

            # elif ltype == 'AreaLoad':

                # f.write('\n')
            #     components = ''
            #     if com['x']:
            #         pass
            #     if com['y']:
            #         pass
            #     if com['z']:
            #         components += ' PZZ {0}'.format(0.001 * com['z'] * lf)
            #     f.write('    QUAD GRP {0}{1}\n'.format(set_index, components))

        f.write('\n')
        f.write('END\n')
        f.write('\n')
        f.write('\n')

    return urs






# CTRL ITER V4 10
# CTRL CONC V4
# SYST PROB TH3 ITER 200 TOL 0.010 FMAX 1.1 NMAT YES
# REIQ LCR 4

# $ conventional steel reinforcement
# $ --------------------------------

# SREC 1 B 50[mm] H 149[mm] HO 1[mm] BO 50[mm] MNO 1 MRF 2 ASO 0.4[cm2] ASU 0.4[cm2]
# STEE 5 B 500A

# angle = rebar['angle'] 2nd layer is assumed 90 deg by default.
