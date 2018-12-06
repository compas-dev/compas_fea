
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Elements',
]


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


class Elements(object):

    def __init__(self):

        pass


    def write_elements(self):

        self.write_section('Elements')
        self.blank_line()

        elements   = self.structure.elements
        materials  = self.structure.materials
        properties = self.structure.element_properties
        sections   = self.structure.sections
        sets       = self.structure.sets

        for key in sorted(properties):

            self.write_subsection(key)

            property      = properties[key]
            reinforcement = property.reinforcement
            elset         = property.elset

            section       = sections[property.section]
            s_index       = section.index + 1
            stype         = section.__name__
            geometry      = section.geometry

            material      = materials.get(property.material)
            m_index       = material.index + 1

            selection = property.elements if property.elements else sets[elset].selection

            t   = geometry.get('t', None)
            A   = geometry.get('A', None)
            J   = geometry.get('J', None)
            Ixx = geometry.get('Ixx', None)
            Iyy = geometry.get('Iyy', None)
            E   = material.E.get('E', None)
            G   = material.G.get('G', None)


            for select in selection:

                element = elements[select]
                nodes   = [str(i + 1) for i in element.nodes]
                no      = len(nodes)
                n       = select + 1
                ex      = element.axes.get('ex', None)
                ey      = element.axes.get('ey', None)


                # =====================================================================================================
                # =====================================================================================================
                # SHELL
                # =====================================================================================================
                # =====================================================================================================

                if stype == 'ShellSection':

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        shell = 'ShellNLDKGT' if no == 3 else 'ShellNLDKGQ'
                        self.write_line('section PlateFiber {0} {1} {2}'.format(n, m_index + 1000, t))
                        self.write_line('element {0} {1} {2} {1}'.format(shell, n, ' '.join(nodes)))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        e = 'element_{0}'.format(select)
                        self.write_line('*ELEMENT, TYPE={0}, ELSET={1}'.format('S3' if no == 3 else 'S4', e))
                        self.write_line('{0}, {1}'.format(n, ','.join(nodes)))

                        if ex and ey:
                            o   = 'ORI_element_{0}'.format(select)
                            ori = ', ORIENTATION={0}'.format(o)
                        #     self.write_line('*ORIENTATION, NAME={0}\n'.format(o))
                        #     self.write_line(', '.join([str(j) for j in ex]) + ', ')
                        #     self.write_line(', '.join([str(j) for j in ey]) + '\n')
                        #     self.write_line('**\n')
                        else:
                            ori = ''

                        self.write_line('*SHELL SECTION, ELSET={0}, MATERIAL={1} {2}'.format(e, material.name, ori))
                        self.write_line('{0}'.format(t))

                        # if reinforcement:
                        #     self.write_line('*REBAR LAYER\n')
                        #     for name, rebar in reinforcement.items():
                        #         pos     = rebar['pos']
                        #         spacing = rebar['spacing']
                        #         rmat    = rebar['material']
                        #         angle   = rebar['angle']
                        #         dia     = rebar['dia']
                        #         area    = 0.25 * pi * dia**2
                        #         self.write_line('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(name, area, spacing, pos, rmat, angle))

                    # -------------------------------------------------------------------------------------------------
                    # Ansys
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'ansys':

                        pass


                # =====================================================================================================
                # =====================================================================================================
                # TRUSS
                # =====================================================================================================
                # =====================================================================================================

                elif stype == 'TrussSection':

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        e = 'element corotTruss'
                        self.write_line('{0} {1} {2} {3} {4} {5}'.format(e, n, nodes[0], nodes[1], A, m_index))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        e = 'element_{0}'.format(select)
                        self.write_line('*ELEMENT, TYPE=T3D2, ELSET={0}'.format(e))
                        self.write_line('{0}, {1},{2}'.format(n, nodes[0], nodes[1]))
                        self.write_line('*SOLID SECTION, ELSET={0}, MATERIAL={1}'.format(e, material.name))
                        self.write_line(str(A))

                    # -------------------------------------------------------------------------------------------------
                    # Ansys
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'ansys':

                        pass


                # =====================================================================================================
                # =====================================================================================================
                # BEAM
                # =====================================================================================================
                # =====================================================================================================

                else:

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        e = 'element elasticBeamColumn'
                        self.write_line('geomTransf Corotational {0} {1}'.format(n, ' '.join([str(i) for i in ex])))
                        self.write_line('{} {} {} {} {} {} {} {} {} {} {}'.format(e, n, nodes[0], nodes[1], A, E, G, J, Ixx, Iyy, n))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        e = 'element_{0}'.format(select)
                        a = abaqus_data[stype]
                        h = '*BEAM GENERAL SECTION' if stype == 'GeneralSection' else '*BEAM SECTION'

                        self.write_line('*ELEMENT, TYPE=B31, ELSET={0}'.format(e))
                        self.write_line('{0}, {1},{2}'.format(n, nodes[0], nodes[1]))

                        self.write_line('{0}, SECTION={1}, ELSET={2}, MATERIAL={3}'.format(
                                        h, a['name'], e, material.name))
                        self.write_line(', '.join([str(geometry[k]) for k in a['geometry']]))

                        if ex:
                            self.write_line(', '.join([str(i) for i in ex]))

                    # -------------------------------------------------------------------------------------------------
                    # Ansys
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'ansys':

                        pass

                self.blank_line()

            self.blank_line()
            self.blank_line()























# from math import pi
# from math import sqrt





#     membranes  = ['MembraneSection']
#     solids     = ['SolidSection']
#     trusses    = ['TrussSection', 'StrutSection', 'TieSection']

#     written_springs = []
#     structure.sofistik_mapping = {}
#     has_rebar = False



#         # Check rebar

#         if reinforcement:
#             has_rebar = True

#         # Make elsets list



#         if not (stype == 'SpringSection'):
#             f.write('{0} Property: {1}\n'.format(c, key))
#             f.write('{0} ----------'.format(c) + '-' * (len(key)) + '\n')
#             f.write('{0}\n'.format(c))

#         for elset in elsets:

#             # Extract selection





# def _write_membranes(f, software, selection, elements, geometry, material, materials, reinforcement):

#     for select in selection:

#         element = elements[select]
#         nodes   = element.nodes
#         n  = select + 1
#         t  = geometry['t']
#         ex = element.axes.get('ex', None)
#         ey = element.axes.get('ey', None)

#         if software == 'abaqus':

#             e1 = 'element_{0}'.format(select)
#             f.write('*ELEMENT, TYPE={0}, ELSET={1}\n'.format('M3D3' if len(nodes) == 3 else 'M3D4', e1))
#             f.write('{0}, {1}\n'.format(n, ','.join([str(i + 1) for i in nodes])))

#             if ex and ey:
#                 ori = 'ORI_element_{0}'.format(select)
#                 f.write('*ORIENTATION, NAME={0}\n'.format(ori))
#                 f.write(', '.join([str(j) for j in ex]) + ', ')
#                 f.write(', '.join([str(j) for j in ey]) + '\n')
#                 f.write('**\n')
#             else:
#                 ori = None

#             f.write('*MEMBRANE SECTION, ELSET={0}, MATERIAL={1}'.format(e1, material.name))
#             if ori:
#                 f.write(', ORIENTATION={0}\n'.format(ori))
#             else:
#                 f.write('\n'.format(t))
#             f.write('{0}\n'.format(t))

#         elif software == 'opensees':

#             pass

#         elif software == 'sofistik':

#             pass

#         elif software == 'ansys':

#             pass

#         f.write('{0}\n'.format(comments[software]))


# def _write_blocks(f, software, selection, elements, material):

#     abaqus_etypes = {4: 'C3D4', 6: 'C3D6', 8: 'C3D8'}
#     sofistik_etypes = {8: 'BRIC NO N1 N2 N3 N4 N5 N6 N7 N8 MNO\n'}

#     for select in selection:

#         nodes = elements[select].nodes
#         ni    = select + 1

#         if software == 'sofistik':

#             f.write(sofistik_etypes[len(nodes)])
#             f.write('{0} {1} {2}\n'.format(ni, ' '.join([str(i + 1) for i in nodes]), material.index + 1))

#         elif software == 'opensees':

#             pass

#         elif software == 'ansys':

#             pass

#         elif software == 'abaqus':

#             f.write('*ELEMENT, TYPE={0}, ELSET=element_{1}\n'.format(abaqus_etypes[len(nodes)], select))
#             f.write('{0}, {1}\n'.format(ni, ','.join([str(i + 1) for i in nodes])))
#             f.write('*SOLID SECTION, ELSET=element_{0}, MATERIAL={1}\n'.format(select, material.name))
#             f.write('\n')

#         f.write('{0}\n'.format(comments[software]))


# def _write_springs(f, software, selection, elements, section, written_springs):

#     if section.stiffness:

#         kx = section.stiffness.get('axial', 0)
#         ky = section.stiffness.get('lateral', 0)
#         kr = section.stiffness.get('rotation', 0)

#     if software == 'abaqus':

#         b1 = 'BEH_{0}'.format(section.name)

#         if b1 not in written_springs:
#             f.write('*CONNECTOR BEHAVIOR, NAME={0}\n'.format(b1))

#             if kx:
#                 f.write('*CONNECTOR ELASTICITY, COMPONENT=1\n')
#                 f.write('{0}\n'.format(kx))

#             elif section.forces['axial'] and section.displacements['axial']:
#                 f.write('*CONNECTOR ELASTICITY, COMPONENT=1, NONLINEAR\n')
#                 for i, j in zip(section.forces['axial'], section.displacements['axial']):
#                     f.write('{0}, {1}\n'.format(i, j))

#             written_springs.append(b1)
#             f.write('**\n')

#     elif software == 'opensees':

#         section_index = section.index + 1

#         if section_index not in written_springs:
#             if kx:

#                 f.write('uniaxialMaterial Elastic 1{0:0>3} {1}\n'.format(section_index, kx))
#                 f.write('#\n')

#             # else:
#             #     i = ' '.join([str(k) for k in section.forces['axial']])
#             #     j = ' '.join([str(k) for k in section.displacements['axial']])
#             #     f.write('uniaxialMaterial ElasticMultiLinear {0}01 -strain {1} -stress {2}\n'.format(
#             #         section_index, j, i))
#             #     f.write('#\n')

#             written_springs.append(section_index)

#     for select in selection:

#         element = elements[select]
#         sp, ep = element.nodes
#         ni = select + 1
#         i  = sp + 1
#         j  = ep + 1
#         ey = element.axes.get('ey')
#         ez = element.axes.get('ez')

#         if software == 'abaqus':

#             e1 = 'element_{0}'.format(select)
#             f.write('*ELEMENT, TYPE=CONN3D2, ELSET={0}\n'.format(e1))
#             f.write('{0}, {1},{2}\n'.format(ni, i, j))

#             f.write('*ORIENTATION, NAME=ORI_{0}\n'.format(select))
#             f.write(', '.join([str(k) for k in ez]) + ', ')
#             f.write(', '.join([str(k) for k in ey]) + '\n')

#             f.write('*CONNECTOR SECTION, ELSET={0}, BEHAVIOR={1}\n'.format(e1, b1))
#             f.write('AXIAL\n')
#             f.write('ORI_{0}\n'.format(select))
#             f.write('**\n')

#         elif software == 'sofistik':

#             f.write('SPRI NO {0} NA {1} NE {2} CP {3} CT {4} CM {5}\n'.format(ni, j, i, kx, ky, kr))

#         elif software == 'opensees':

#             orientation = ' '.join([str(k) for k in ey])
#             f.write('element twoNodeLink {0} {1} {2} -mat 1{3:0>3} -dir 1 -orient {4} \n'.format(
#                     ni, i, j, section_index, orientation))
#             f.write('#\n')

#         elif software == 'ansys':

#             pass

#     return written_springs





# def _write_sofistik_rebar(f, properties, sections, sets):

#         f.write('+PROG BEMESS\n')
#         f.write('$\n')
#         f.write('CTRL WARN 7 $ Upper cover (<10mm or >0.70d)\n')
#         f.write('CTRL WARN 9 $ Bottom cover (<10mm or >0.70d)\n')
#         f.write('CTRL WARN 471 $ Element thickness too thin and not allowed for design\n')
#         f.write('$\n')

#         for key, property in properties.items():

#             if property.reinforcement:

#                 if isinstance(property.elsets, str):
#                     elsets = [property.elsets]

#                 f.write('$ Reinforcement: {0}\n'.format(key))
#                 f.write('$ ---------------' + '-' * (len(key)) + '\n')
#                 f.write('$\n')

#                 t = sections[property.section].geometry['t']
#                 pos_u, pos_l, dia_u, dia_l, A_u, A_l = [], [], [], [], [], []

#                 for name, rebar in property.reinforcement.items():
#                     pos = rebar['pos']
#                     dia = rebar['dia']
#                     A = 0.25 * pi * (dia * 100)**2 / rebar['spacing']
#                     if pos > 0:
#                         pos_u.append(pos)
#                         dia_u.append(dia)
#                         A_u.append(A)
#                     else:
#                         pos_l.append(pos)
#                         dia_l.append(dia)
#                         A_l.append(A)

#                 geom = 'GEOM -'
#                 data = ''

#                 if len(pos_u) == 1:

#                     geom += ' HA {0}[mm]'.format((0.5 * t - pos_u[0]) * 1000)
#                     data += '     DU {0}[mm] ASU {1}[cm2/m] BSU {2}[cm2/m]\n'.format(dia_u[0] * 1000, A_u[0], A_u[0])

#                 elif len(pos_u) == 2:

#                     no = [0, 1] if pos_u[0] > pos_u[1] else [1, 0]
#                     HA  = (0.5 * t - pos_u[no[0]]) * 1000
#                     DHA = abs(pos_u[0] - pos_u[1]) * 1000
#                     geom += ' HA {0}[mm] DHA {1}[mm]'.format(HA, DHA)
#                     data += '     DU {0}[mm] ASU {1}[cm2/m] BSU {1}[cm2/m]\n'.format(dia_u[no[0]] * 1000, A_u[no[0]])
#                     data += '     DU2 {0}[mm] ASU2 {1}[cm2/m] BSU2 {1}[cm2/m]\n'.format(dia_u[no[1]] * 1000, A_u[no[1]])

#                 if len(pos_l) == 1:

#                     geom += ' HB {0}[mm]'.format((0.5 * t + pos_l[0]) * 1000)
#                     data += '     DL {0}[mm] ASL {1}[cm2/m] BSL {2}[cm2/m]\n'.format(dia_l[0] * 1000, A_l[0], A_l[0])

#                 elif len(pos_l) == 2:

#                     no = [0, 1] if pos_l[0] < pos_l[1] else [1, 0]
#                     HB  = (0.5 * t + pos_l[no[0]]) * 1000
#                     DHB = abs(pos_l[0] - pos_l[1]) * 1000
#                     geom += ' HB {0}[mm] DHB {1}[mm]'.format(HB, DHB)
#                     data += '     DL {0}[mm] ASL {1}[cm2/m] BSL {1}[cm2/m]\n'.format(dia_l[no[0]] * 1000, A_l[no[0]])
#                     data += '     DL2 {0}[mm] ASL2 {1}[cm2/m] BSL2 {1}[cm2/m]\n'.format(dia_l[no[1]] * 1000, A_l[no[1]])

#                 f.write(geom + '\n')
#                 f.write('$\n')

#                 f.write('PARA NOG - WKU 0.1[mm] WKL 0.1[mm]\n')
#                 for elset in elsets:
#                     set_index = sets[elset]['index'] + 1
#                     f.write('PARA NOG {0}\n{1}'.format(set_index, data))

#                 f.write('$\n')
#                 f.write('$\n')

#         f.write('END\n')
#         f.write('$\n')
#         f.write('$\n')
