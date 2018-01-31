
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_postprocess',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}


def write_input_postprocess(f, software, structure, steps, properties, sections):

    """ Writes any post-processing information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        The Structure object to read from.
    steps : dic
        Step objects from structure.steps.
    properties : dic
        ElementProperties objects from structure.element_properties.
    sections : dic
        Section objects from structure.sections.

    Returns
    -------
    None

    """

    c = comments[software]
    key = structure.steps_order[-1]  # assumption you want the last step
    # step = steps[key]
    # step_index = step.index

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ------------------------------------------------------------- Post-processing\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'abaqus':

        pass

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        f.write('$ -----------------------------------------------------------------------------\n')
        f.write('$ --------------------------------------------------------------- Reinforcement\n')
        f.write('$\n')
        f.write('+PROG BEMESS\n')
        f.write('$\n')
        f.write('CTRL WARN 7\n')  # Upper cover (<10mm or >0.70d)
        f.write('CTRL WARN 9\n')  # Bottom cover (<10mm or >0.70d)
        f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
        f.write('$\n')

        for key, property in properties.items():

            reinforcement = property.reinforcement

            if reinforcement:

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

        #         elif len(posu) == 2:
        #             if posu[0] > posu[1]:
        #                 no1 = 0
        #                 no2 = 1
        #             else:
        #                 no1 = 1
        #                 no2 = 0
        #             DHA = abs(posu[0] - posu[1]) * 1000
        #             geom += ' HA {0}[mm] DHA {1}[mm]'.format((0.5 * t - posu[no1]) * 1000, DHA)
        #             data += ' DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]'.format(du[no1] * 1000, Au[no1], Au[no1])
        #             data += ' DU2 {0}[mm] ASU2 {1}[cm2/m] BSU2 {2}[cm2/m]'.format(du[no2] * 1000, Au[no2], Au[no2])

                if len(posl) == 1:
                    geom += ' HB {0}[mm]'.format((0.5 * t + posl[0]) * 1000)
                    data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[0] * 1000, Al[0], Al[0])

        #         elif len(posl) == 2:
        #             if posl[0] < posl[1]:
        #                 no1 = 0
        #                 no2 = 1
        #             else:
        #                 no1 = 1
        #                 no2 = 0
        #             DHB = abs(posl[0] - posl[1]) * 1000
        #             geom += ' HB {0}[mm] DHB {1}[mm]'.format((0.5 * t + posl[no1]) * 1000, DHB)
        #             data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[no1] * 1000, Al[no1], Al[no1])
        #             data += ' DL2 {0}[mm] ASL2 {1}[cm2/m] BSL2 {2}[cm2/m]'.format(dl[no2] * 1000, Al[no2], Al[no2])

                f.write(geom + '\n')
                f.write('$\n')

                if isinstance(property.elsets, str):
                    elsets = [property.elsets]

                f.write('PARA NOG - WKU 0.1[mm] WKL 0.1[mm]\n')
                for elset in elsets:
                    set_index = structure.sets[elset]['index'] + 1
                    f.write('PARA NOG {0}{1}\n'.format(set_index, data))

                f.write('$\n')
                f.write('$\n')

        # f.write('CTRL WARN 471\n')  # Element thickness too thin and not allowed for design.
        # f.write('CTRL SLS\n')
        # # f.write('CTRL ULTI\n')
        # # CTRL PFAI 2
        # f.write('CRAC WK PARA\n')
        # f.write('$\n')
        # f.write('LC 10{0}\n'.format(step_index))
        # f.write('$\n')

        f.write('END\n')





    elif software == 'ansys':

        pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))
