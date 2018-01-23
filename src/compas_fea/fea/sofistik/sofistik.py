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
from compas_fea.fea import write_input_postprocess
from compas_fea.fea import write_input_steps

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
        f.write('HEAD AQUA\n')
        write_input_materials(f, 'sofistik', materials, sections, properties)
        f.write('END\n$\n$\n')

        urs += 1
        f.write('+PROG SOFIMSHA urs:{0}\n'.format(urs))
        write_input_nodes(f, 'sofistik', nodes)
        write_input_bcs(f, 'sofistik', structure, steps, displacements)
        write_input_elements(f, 'sofistik', sections, properties, elements, structure, materials)
        f.write('END\n$\n$\n')

        urs = input_write_rebar(f, properties, sections, sets, urs)  # need to get into write functions

        urs += 1
        f.write('+PROG ASE urs:{0}\n'.format(urs))
        write_input_steps(f, 'sofistik', structure, steps, loads, displacements, sets, fields)
        f.write('END\n$\n$\n')

        urs += 1
        f.write('+PROG BEMESS urs:{0}\n'.format(urs))
        write_input_postprocess(f, 'sofistik', structure)
        f.write('END\n$\n$\n')

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

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ --------------------------------------------------------------- Reinforcement\n')
    f.write('$\n')

    # Properties
    # ----------

    for key, property in properties.items():

        reinforcement = property.reinforcement
        property_index = property.index + 1

        if reinforcement:

            urs += 1

            f.write('+PROG BEMESS urs:{0}\n'.format(urs))
            f.write('$\n')
            f.write('CTRL WARN 7\n')  # Upper cover (<10mm or >0.70d)
            f.write('CTRL WARN 9\n')  # Bottom cover (<10mm or >0.70d)
            f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
            f.write('$\n')

            f.write('$ Reinforcement: {0}\n'.format(key))
            f.write('$ ---------------' + '-' * (len(key)) + '\n')
            f.write('$\n')

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
            f.write('$\n')

            if isinstance(property.elsets, str):
                elsets = [property.elsets]

            f.write('PARA NOG - WKU 0.1[mm] WKL 0.1[mm]\n')
            for elset in elsets:
                set_index = sets[elset]['index'] + 1
                f.write('PARA NOG {0}{1}\n'.format(set_index, data))

            f.write('$\n')
            f.write('$\n')

            f.write('END\n$\n$\n')

    return urs
