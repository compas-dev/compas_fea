
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import Writer

from math import pi
from math import sqrt


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
]


def input_generate(structure, fields, output):

    """ Creates the Sofistik .dat file from the Structure object.

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

    filename = '{0}{1}.dat'.format(structure.path, structure.name)

    with Writer(structure=structure, software='sofistik', filename=filename, fields=fields) as writer:

        writer.write_heading()
        writer.write_materials()
        write_sofistik_sections(writer, structure.element_properties, structure.materials, structure.sections)
        writer.write_nodes()
        writer.write_boundary_conditions()
        writer.write_elements()

        #     if software == 'sofistik':

#         _write_sofistik_loads_displacements(f, sets, displacements, loads, steps, structure)

#         f.write('END\n')
#         f.write('$\n')
#         f.write('$\n')

        writer.write_steps()

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))


def write_sofistik_sections(writer, properties, materials, sections):

    writer.write_section('Sections')
    writer.blank_line()

    for key, property in properties.items():

        section  = sections[property.section]
        s_index  = section.index + 1
        stype    = section.__name__
        geometry = section.geometry
        m_index  = materials[property.material].index + 1 if property.material else None

        if stype not in ['SolidSection', 'ShellSection', 'SpringSection']:

            writer.write_subsection(section.name)

            if stype in ['PipeSection', 'CircularSection']:

                D = geometry['D'] * 1000
                t = geometry['t'] * 1000 if stype == 'PipeSection' else 0

                writer.write_line('TUBE NO {0} D {1}[mm] T {2}[mm] MNO {3}'.format(s_index, D, t, m_index))

            elif stype == 'RectangularSection':

                b = geometry['b'] * 1000
                h = geometry['h'] * 1000

                writer.write_line('SREC NO {0} H {1}[mm] B {2}[mm] MNO {3}'.format(s_index, h, b, m_index))

            elif stype in ['TrussSection', 'StrutSection', 'TieSection']:

                D = sqrt(geometry['A'] * 4 / pi) * 1000
                writer.write_line('TUBE NO {0} D {1:.3f}[mm] T {2}[mm] MNO {3}'.format(s_index, D, 0, m_index))

            writer.blank_line()
            writer.blank_line()

    writer.write_line('END')
    writer.blank_line()
    writer.blank_line()
