
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_elements',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}

abaqus_data = {
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
    'TrussSection':       {'name': None,          'geometry': ['A']},
}


def write_input_elements(f, software, sections, properties, elements, structure, materials):

    """ Writes the element and section information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    sections : dic
        Section objects from structure.sections.
    properties : dic
        ElementProperties objects from structure.element_properties.
    elements : dic
        Element objects from structure.elements.
    structure : obj
        The Structure object.
    materials : dic
        Material objects from structure.materials.

    Returns
    -------
    None

    """

    c = comments[software]

    shells = ['ShellSection']
    solids = ['SolidSection']
    trusses = ['TrussSection', 'StrutSection', 'TieSection']

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} -------------------------------------------------------------------- Elements\n'.format(c))
    f.write('{0}\n'.format(c))

#     has_rebar = False
#     written_springs = []
    written_elsets = []
    structure.sofistik_mapping = {}

    for key in sorted(properties):
        property = properties[key]

        section = sections[property.section]
        section_index = section.index + 1
        stype = section.__name__
        geometry = section.geometry
        material = materials.get(property.material, None)
#         reinforcement = property.reinforcement
#         if reinforcement:
#             rebar_index = materials[list(reinforcement.values())[0]['material']].index + 1
#             has_rebar = True
#         else:
#             rebar_index = None

        f.write('{0} Property: {1}\n'.format(c, key))
        f.write('{0} ----------'.format(c) + '-' * (len(key)) + '\n')
        f.write('{0}\n'.format(c))

        if property.elements:
            elset = 'elset_{0}'.format(key)
            elsets = [elset]
            structure.add_set(name=elset, type='element', selection=property.elements)
        else:
            elsets = property.elsets
            if isinstance(elsets, str):
                elsets = [elsets]
            written_elsets.extend(elsets)

        for elset in elsets:

            if property.elements:
                selection = property.elements
            else:
                selection = structure.sets[elset]['selection']

            if software == 'sofistik':
                set_index = structure.sets[elset]['index'] + 1
                for i in selection:
                    entry = int(100000 * set_index + i + 1)
                    structure.sofistik_mapping[i] = entry
                f.write('GRP {0} BASE {0}00000\n'.format(set_index))
                f.write('$\n')

            # Springs

            if stype == 'SpringSection':
                pass
#                 _write_springs(f, software, selection, elements, section, written_springs)

            # Beam sections

            elif stype not in shells + solids + trusses:
                _write_beams(f, software, elements, selection, geometry, material, section_index, stype, elset)

            # Truss sections

            elif stype in trusses:
                _write_trusses(f, selection, software, elements, section, material, elset)

#             # Shell sections

#             elif stype in shells:
#                 _write_shells(f, software, selection, elements, geometry, material, reinforcement, rebar_index, c)

#             # Solid sections

#             elif stype in solids:
#                 _write_blocks(f, software, selection, elements, material, c)

            f.write('{0}\n'.format(c))
            f.write('{0}\n'.format(c))

    if software == 'sofistik':

        f.write('END\n')
        f.write('$\n')
        f.write('$\n')

    elif software == 'abaqus':

        cm = 9
        for key, set in structure.sets.items():
            stype = set['type']

            if (key not in written_elsets) and (stype != 'node'):

                f.write('** {0}\n'.format(key))
                f.write('** ' + '-' * len(key) + '\n')
                f.write('**\n')

                if stype in ['element', 'surface_node']:

                    if stype == 'element':
                        f.write('*ELSET, ELSET={0}\n'.format(key))
                        f.write('**\n')

                    elif stype == 'surface_node':
                        f.write('*SURFACE, TYPE=NODE, NAME={0}\n'.format(key))
                        f.write('**\n')

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

#         if has_rebar:
#             _write_sofistik_rebar(f, properties, sections, sets)


# def _write_sofistik_rebar(f, properties, sections, sets):

#         f.write('+PROG BEMESS\n')
#         f.write('$\n')
#         f.write('CTRL WARN 7 $ Upper cover (<10mm or >0.70d)\n')
#         f.write('CTRL WARN 9 $ Bottom cover (<10mm or >0.70d)\n')
#         f.write('CTRL WARN 471 $ Element thickness too thin and not allowed for design\n')
#         f.write('$\n')

#         for key, property in properties.items():

#             reinforcement = property.reinforcement

#             if reinforcement:

#                 f.write('$ Reinforcement: {0}\n'.format(key))
#                 f.write('$ ---------------' + '-' * (len(key)) + '\n')
#                 f.write('$\n')

#                 t = sections[property.section].geometry['t']
#                 posu, posl = [], []
#                 du, dl = [], []
#                 Au, Al = [], []

#                 for name, rebar in reinforcement.items():
#                     pos = rebar['pos']
#                     dia = rebar['dia']
#                     spacing = rebar['spacing']
#                     Ac = 0.25 * pi * (dia * 100)**2
#                     Apm = Ac / spacing
#                     if pos > 0:
#                         posu.append(pos)
#                         du.append(dia)
#                         Au.append(Apm)
#                     elif pos < 0:
#                         posl.append(pos)
#                         dl.append(dia)
#                         Al.append(Apm)

#                 geom = 'GEOM -'
#                 data = ''

#                 if len(posu) == 1:
#                     geom += ' HA {0}[mm]'.format((0.5 * t - posu[0]) * 1000)
#                     data += ' DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]'.format(du[0] * 1000, Au[0], Au[0])

#                 elif len(posu) == 2:
#                     if posu[0] > posu[1]:
#                         no1 = 0
#                         no2 = 1
#                     else:
#                         no1 = 1
#                         no2 = 0
#                     DHA = abs(posu[0] - posu[1]) * 1000
#                     geom += ' HA {0}[mm] DHA {1}[mm]'.format((0.5 * t - posu[no1]) * 1000, DHA)
#                     data += ' DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]'.format(du[no1] * 1000, Au[no1], Au[no1])
#                     data += ' DU2 {0}[mm] ASU2 {1}[cm2/m] BSU2 {2}[cm2/m]'.format(du[no2] * 1000, Au[no2], Au[no2])

#                 if len(posl) == 1:
#                     geom += ' HB {0}[mm]'.format((0.5 * t + posl[0]) * 1000)
#                     data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[0] * 1000, Al[0], Al[0])

#                 elif len(posl) == 2:
#                     if posl[0] < posl[1]:
#                         no1 = 0
#                         no2 = 1
#                     else:
#                         no1 = 1
#                         no2 = 0
#                     DHB = abs(posl[0] - posl[1]) * 1000
#                     geom += ' HB {0}[mm] DHB {1}[mm]'.format((0.5 * t + posl[no1]) * 1000, DHB)
#                     data += ' DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]'.format(dl[no1] * 1000, Al[no1], Al[no1])
#                     data += ' DL2 {0}[mm] ASL2 {1}[cm2/m] BSL2 {2}[cm2/m]'.format(dl[no2] * 1000, Al[no2], Al[no2])

#                 f.write(geom + '\n')
#                 f.write('$\n')

#                 if isinstance(property.elsets, str):
#                     elsets = [property.elsets]

#                 f.write('PARA NOG - WKU 0.1[mm] WKL 0.1[mm]\n')
#                 for elset in elsets:
#                     set_index = sets[elset]['index'] + 1
#                     f.write('PARA NOG {0}{1}\n'.format(set_index, data))

#                 f.write('$\n')
#                 f.write('$\n')

#         f.write('END\n')
#         f.write('$\n')
#         f.write('$\n')


# def _write_blocks(f, software, selection, elements, material, c):

#     for select in selection:

#         element = elements[select]
#         nodes = element.nodes
#         n = select + 1

#         if software == 'sofistik':

#             if len(nodes) == 8:
#                 f.write('BRIC NO N1 N2 N3 N4 N5 N6 N7 N8 MNO\n')

#             f.write('{0} {1} {2}\n'.format(n, ' '.join([str(i + 1) for i in nodes]), material.index + 1))

#         elif software == 'opensees':

#             pass

#         elif software == 'ansys':

#             pass

#         elif software == 'abaqus':

#             if len(nodes) == 4:
#                 etype = 'C3D4'
#             elif len(nodes) == 6:
#                 etype = 'C3D6'
#             elif len(nodes) == 8:
#                 etype = 'C3D8'

#             f.write('*ELEMENT, TYPE={0}, ELSET=element_{1}\n'.format(etype, select))
#             f.write('{0}, {1}\n'.format(n, ','.join([str(i + 1) for i in nodes])))
#             f.write('*SOLID SECTION, ELSET=element_{0}, MATERIAL={1}\n'.format(select, material.name))
#             f.write('\n')

#         f.write('{0}\n'.format(c))


# def _write_shells(f, software, selection, elements, geometry, material, reinforcement, rebar_index, c):

#     for select in selection:

#         element = elements[select]
#         nodes = element.nodes
#         n = select + 1
#         t = geometry['t']

#         if software == 'abaqus':

#             if len(nodes) == 3:
#                 etype = 'S3'
#             elif len(nodes) == 4:
#                 etype = 'S4'

#             f.write('*ELEMENT, TYPE={0}, ELSET=element_{1}\n'.format(etype, select))
#             f.write('{0}, {1}\n'.format(n, ','.join([str(i + 1) for i in nodes])))

#             e1 = 'element_{0}'.format(select)
#             ex = element.axes.get('ex', None)
#             ey = element.axes.get('ey', None)
#             pre = '*SHELL SECTION, ELSET='

#             if ex and ey:
#                 ori = 'ORI_element_{0}'.format(select)
#                 f.write('*ORIENTATION, NAME={0}\n'.format(ori))
#                 f.write(', '.join([str(j) for j in ex]) + ', ')
#                 f.write(', '.join([str(j) for j in ey]) + '\n')
#                 f.write('**\n')
#                 f.write('{0}{1}, MATERIAL={2}, ORIENTATION={3}\n'.format(pre, e1, material.name, ori))
#             else:
#                 f.write('{0}{1}, MATERIAL={2}\n'.format(pre, e1, material.name))

#             f.write(str(t) + '\n')

#             if reinforcement:
#                 f.write('*REBAR LAYER\n')
#                 for name, rebar in reinforcement.items():
#                     pos     = rebar['pos']
#                     spacing = rebar['spacing']
#                     rmat    = rebar['material']
#                     angle   = rebar['angle']
#                     dia     = rebar['dia']
#                     area    = 0.25 * pi * dia**2
#                     f.write('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(name, area, spacing, pos, rmat, angle))

#         elif software == 'opensees':

#             E = material.E['E']
#             v = material.v['v']
#             p = material.p

#             if len(nodes) == 3:
#                 pass
#             if len(nodes) == 4:
#                 f.write('section ElasticMembranePlateSection {0} {1} {2} {3} {4}\n'.format(n, E, v, t, p))
#                 f.write('element ShellNLDKGQ {0} {1} {0}\n'.format(n, ' '.join([str(i + 1) for i in nodes])))

#         elif software == 'sofistik':

#             if len(nodes) == 3:
#                 pass
#             elif len(nodes) == 4:
#                 f.write('QUAD NO N1 N2 N3 N4 MNO T1 T2 T3 T4')

#             if rebar_index:
#                 f.write(' MRF')
#             f.write('\n')

#             data = [n] + [i + 1 for i in nodes] + [material.index + 1] + [t] * len(nodes)
#             if rebar_index:
#                 data.append(rebar_index)
#             f.write('{0}\n'.format(' '.join([str(i) for i in data])))

#         elif software == 'ansys':

#             pass

#         f.write('{0}\n'.format(c))


def _write_beams(f, software, elements, selection, geometry, material, section_index, stype, elset):

    for select in selection:

        element = elements[select]
        sp, ep = element.nodes
        n = select + 1
        i = sp + 1
        j = ep + 1
        ex = element.axes.get('ex', None)

        if software == 'abaqus':

            e1 = 'element_{0}'.format(select)
            f.write('*ELEMENT, TYPE=B31, ELSET={0}\n'.format(e1))
            f.write('{0}, {1},{2}\n'.format(n, i, j))

            data = abaqus_data[stype]
            f.write('*BEAM GENERAL SECTION' if stype == 'GeneralSection' else '*BEAM SECTION')
            f.write(', SECTION={0}, ELSET={1}, MATERIAL={2}\n'.format(data['name'], e1, material.name))
            f.write(', '.join([str(geometry[k]) for k in data['geometry']]) + '\n')
            if ex:
                f.write(', '.join([str(k) for k in ex]) + '\n')
            f.write('**\n')

        elif software == 'opensees':

            A   = geometry['A']
            E   = material.E['E']
            G   = material.G['G']
            J   = geometry['J']
            Ixx = geometry['Ixx']
            Iyy = geometry['Iyy']

            ex = ' '.join([str(k) for k in element.axes['ex']])
            et = 'element elasticBeamColumn'
            f.write('geomTransf Corotational {0} {1}\n'.format(select + 1, ex))
            f.write('{} {} {} {} {} {} {} {} {} {} {}\n'.format(et, n, i, j, A, E, G, J, Ixx, Iyy, n))
            f.write('#\n')

        elif software == 'sofistik':

            f.write('BEAM NO {0} NA {1} NE {2} NCS {3}\n'.format(n, i, j, section_index))

        elif software == 'ansys':

            pass

    if software == 'abaqus':

        f.write('** {0}\n'.format(elset))
        f.write('** ' + '-' * len(elset) + '\n')
        f.write('**\n')
        f.write('*ELSET, ELSET={0}\n'.format(elset))
        f.write('**\n')

        cm = 9
        cnt = 0
        for j in selection:
            f.write(str(j + 1))
            if (cnt < cm) and (j != selection[-1]):
                f.write(',')
                cnt += 1
            elif cnt >= cm:
                f.write('\n')
                cnt = 0
            else:
                f.write('\n')


def _write_trusses(f, selection, software, elements, section, material, elset):


    A = section.geometry['A']

    if software == 'abaqus':

        f.write('*SOLID SECTION, ELSET={0}, MATERIAL={1}\n'.format(elset, material.name))
        f.write('{0}\n'.format(A))
        f.write('**\n')
        f.write('*ELEMENT, TYPE=T3D2, ELSET={0}\n'.format(elset))
        f.write('**\n')

    elif software == 'sofistik':

        f.write('TRUS NO NA NE NCS')
        if material.__name__ in ['Steel']:
            Ny = A * material.fy / 1000.
            f.write(' YIEL')
        else:
            Ny = None
        f.write('\n$\n')

    elif software == 'opensees':

        pass

    for select in selection:

        sp, ep = elements[select].nodes
        n = select + 1
        i = sp + 1
        j = ep + 1

        if software == 'abaqus':

            f.write('{0}, {1},{2}\n'.format(n, i, j))

        elif software == 'sofistik':

            if Ny:
                f.write('{0} {1} {2} {3} {4}\n'.format(n, i, j, section.index + 1, Ny))
            else:
                f.write('{0} {1} {2} {3}\n'.format(n, i, j, section.index + 1))

        elif software == 'opensees':

            f.write('element corotTruss {0} {1} {2} {3} {4}\n'.format(n, i, j, A, material.index + 1))

        elif software == 'ansys':

            pass


# def _write_springs(f, software, selection, elements, section, written_springs):

#     if software == 'abaqus':

#         b1 = 'BEH_{0}'.format(section.name)
#         if b1 not in written_springs:
#             f.write('*CONNECTOR BEHAVIOR, NAME={0}\n'.format(b1))
#             if section.stiffness:
#                 f.write('*CONNECTOR ELASTICITY, COMPONENT=1\n')
#                 f.write('{0}\n'.format(section.stiffness['axial']))
#             else:
#                 f.write('*CONNECTOR ELASTICITY, COMPONENT=1, NONLINEAR\n')
#                 for i, j in zip(section.forces['axial'], section.displacements['axial']):
#                     f.write('{0}, {1}\n'.format(i, j))
#             written_springs.append(b1)
#             f.write('**\n')

#     elif software == 'opensees':

#         section_index = section.index + 1
#         if section_index not in written_springs:
#             if section.stiffness:
#                 E = section.stiffness['axial']
#                 f.write('uniaxialMaterial Elastic {0}01 {1}\n'.format(section_index, E))
#                 f.write('#\n')
#             else:
#                 i = ' '.join([str(k) for k in section.forces['axial']])
#                 j = ' '.join([str(k) for k in section.displacements['axial']])
#                 f.write('uniaxialMaterial ElasticMultiLinear {0}01 -strain {1} -stress {2}\n'.format(
#                     section_index, j, i))
#                 f.write('#\n')
#             written_springs.append(section_index)

#     for select in selection:

#         element = elements[select]
#         sp, ep = element.nodes
#         n = select + 1
#         i = sp + 1
#         j = ep + 1
#         ey = element.axes.get('ey', None)
#         ez = element.axes.get('ez', None)

#         if software == 'abaqus':

#             e1 = 'element_{0}'.format(select)
#             f.write('*ELEMENT, TYPE=CONN3D2, ELSET={0}\n'.format(e1))
#             f.write('{0}, {1},{2}\n'.format(n, i, j))

#             f.write('*ORIENTATION, NAME=ORI_{0}\n'.format(select))
#             f.write(', '.join([str(k) for k in ez]) + ', ')
#             f.write(', '.join([str(k) for k in ey]) + '\n')

#             f.write('*CONNECTOR SECTION, ELSET={0}, BEHAVIOR={1}\n'.format(e1, b1))
#             f.write('AXIAL\n')
#             f.write('ORI_{0}\n'.format(select))
#             f.write('**\n')

#         elif software == 'sofistik':

#             kx = section.stiffness.get('axial', 0)
#             ky = section.stiffness.get('lateral', 0)
#             kr = section.stiffness.get('rotation', 0)
#             f.write('SPRI NO {0} NA {1} NE {2} CP {3} CT {4} CM {5}\n'.format(n, j, i, kx, ky, kr))
#             f.write('$\n')

#         elif software == 'opensees':

#             orientation = ' '.join([str(k) for k in ey])
#             f.write('element twoNodeLink {0} {1} {2} -mat {3}01 -dir 1 -orient {4} \n'.format(n, i, j, section_index,
#                     orientation))
#             f.write('#\n')
#         elif software == 'ansys':

#             pass

#     return written_springs
