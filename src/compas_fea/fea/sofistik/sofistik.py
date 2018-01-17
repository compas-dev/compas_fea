"""
compas_fea.fea.sofistik : Sofistik specific functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_bcs
from compas_fea.fea import write_input_elements
from compas_fea.fea import write_input_heading
from compas_fea.fea import write_input_materials
from compas_fea.fea import write_input_nodes

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
    'input_write_materials',
    'input_write_rebar',
]


dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']


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

        write_input_heading(f, software='sofistik')

        urs = 1
        f.write('+PROG AQUA urs:{0}\n'.format(urs))
        write_input_materials(f, 'sofistik', materials)
        f.write('END\n$\n')

        urs += 1
        f.write('+PROG SOFIMSHA urs:{0}\n'.format(urs))
        write_input_nodes(f, 'sofistik', nodes)
        write_input_bcs(f, 'sofistik', structure, steps, displacements)
        write_input_elements(f, 'sofistik', sections, properties, elements, structure, materials)
        f.write('END\n$\n')

        # urs = input_write_rebar(f, properties, sections, sets, urs)
        # urs = input_write_steps(f, structure, steps, loads, displacements, sets, urs)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))


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
    f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
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

        step = steps[key]
        stype = step.__name__

        if stype != 'DesignStep':

            urs += 1

            step_index = step.index
            factor = step.factor

            f.write('\n')
            f.write('+PROG ASE urs:{0}\n'.format(urs))
            f.write('HEAD ASE\n')

            f.write('\n')
            f.write('$ {0}\n'.format(key))
            f.write('$ ' + '-' * len(key) + '\n')
            f.write('\n')

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

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ---------------------------------------------------------------------- Design\n')

    for key in structure.steps_order[1:]:

        step = steps[key]
        stype = step.__name__

        if stype == 'DesignStep':

            urs += 1

            dtype = step.type
            state = step.state
            lc_step = steps[step.step].index

            if dtype == 'rebar':

                f.write('\n')
                f.write('+PROG BEMESS urs:{0}\n'.format(urs))
                f.write('HEAD {0} {1}\n'.format(dtype, state))
                # CTRL PFAI 2
                # CTRL SERV GALF 1.45
                # CTRL LCR 2
                f.write('LC {0}\n'.format(lc_step))

            f.write('\n')
            f.write('END\n')
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
