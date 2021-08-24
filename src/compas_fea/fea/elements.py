from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi


# Author(s): Andrew Liew (github.com/andrewliew)


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

        elements = self.structure.elements
        materials = self.structure.materials
        properties = self.structure.element_properties
        sections = self.structure.sections
        sets = self.structure.sets

        written_springs = []

        for key in sorted(properties):

            self.write_subsection(key)

            property = properties[key]
            reinforcement = property.rebar
            elset = property.elset

            section = sections[property.section]
            stype = section.__name__
            geometry = section.geometry
            material = materials.get(property.material)

            if material:
                m_index = material.index + 1

            s_index = section.index + 1

            selection = property.elements if property.elements else sets[elset].selection

            if geometry is not None:

                t = geometry.get('t', None)
                A = geometry.get('A', None)
                J = geometry.get('J', None)
                Ixx = geometry.get('Ixx', None)
                Iyy = geometry.get('Iyy', None)
                E = material.E.get('E', None)
                G = material.G.get('G', None)

            for select in selection:

                element = elements[select]
                nodes = [str(i + 1) for i in element.nodes]
                no = len(nodes)
                n = select + 1
                ex = element.axes.get('ex', None)
                ey = element.axes.get('ey', None)
                ez = element.axes.get('ez', None)

                # =====================================================================================================
                # =====================================================================================================
                # SOLID
                # =====================================================================================================
                # =====================================================================================================

                if stype == 'SolidSection':

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        if len(nodes) == 4:

                            solid = 'FourNodeTetrahedron'
                            self.write_line('element {0} {1} {2} {3}'.format(solid, n, ' '.join(nodes), m_index + 1000))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        etypes = {4: 'C3D4', 6: 'C3D6', 8: 'C3D8'}
                        e = 'element_{0}'.format(select)

                        self.write_line('*ELEMENT, TYPE={0}, ELSET={1}'.format(etypes[len(nodes)], e))
                        self.write_line('{0}, {1}'.format(n, ','.join(nodes)))
                        self.write_line('*SOLID SECTION, ELSET={0}, MATERIAL={1}'.format(e, material.name))
                        self.write_line('')

                    # -------------------------------------------------------------------------------------------------
                    # Ansys
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'ansys':

                        pass

                # =====================================================================================================
                # =====================================================================================================
                # SHELL
                # =====================================================================================================
                # =====================================================================================================

                elif stype == 'ShellSection':

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        if no == 3:
                            self.write_line('element tri31 {0} {1} {2} PlaneStress {3} 0 {4} 0 0'.format(
                                            n, ' '.join(nodes), t, m_index + 1000, material.p))
                            # self.write_line('section PlateFiber {0} {1} {2}'.format(n, m_index + 1000, t))
                            # self.write_line('element ShellDKGT {0} {1} {0}'.format(n, ' '.join(nodes)))
                            # self.write_line('element ShellNLDKGT {0} {1} {0}'.format(n, ' '.join(nodes)))
                            # aparently unknown to OpenSees
                        else:
                            self.write_line('section PlateFiber {0} {1} {2}'.format(n, m_index + 1000, t))
                            self.write_line('element ShellNLDKGQ {0} {1} {0}'.format(n, ' '.join(nodes)))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        e = 'element_{0}'.format(select)
                        self.write_line('*ELEMENT, TYPE={0}, ELSET={1}'.format('S3' if no == 3 else 'S4', e))
                        self.write_line('{0}, {1}'.format(n, ','.join(nodes)))

                        if ex and ey:
                            o = 'ORI_element_{0}'.format(select)
                            ori = ', ORIENTATION={0}'.format(o)
                            self.write_line('*ORIENTATION, NAME={0}'.format(o))
                            self.write_line(', '.join([str(j) for j in ex]) + ', ' + ', '.join([str(j) for j in ey]))
                            self.blank_line()
                        else:
                            ori = ''

                        self.write_line('*SHELL SECTION, ELSET={0}, MATERIAL={1} {2}'.format(e, material.name, ori))
                        self.write_line('{0}'.format(t))

                        if reinforcement:
                            self.write_line('*REBAR LAYER')

                            for name, rebar in reinforcement.items():

                                pos = rebar['pos']
                                length = rebar['spacing']
                                rmat = rebar['material']
                                angle = rebar['angle']
                                dia = rebar['dia']
                                area = 0.25 * pi * dia**2

                                self.write_line('{0}, {1}, {2}, {3}, {4}, {5}'.format(name, area, length, pos, rmat, angle))

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
                # SPRING
                # =====================================================================================================
                # =====================================================================================================

                elif stype == 'SpringSection':

                    kx = section.stiffness.get('axial', 0)
                    # ky = section.stiffness.get('lateral', 0)
                    # kr = section.stiffness.get('rotation', 0)

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        if s_index not in written_springs:

                            if kx:

                                self.write_line('uniaxialMaterial Elastic 2{0:0>3} {1}'.format(s_index, kx))
                                self.blank_line()

                            # else:
                            #     i = ' '.join([str(k) for k in section.forces['axial']])
                            #     j = ' '.join([str(k) for k in section.displacements['axial']])
                            #     f.write('uniaxialMaterial ElasticMultiLinear {0}01 -strain {1} -stress {2}\n'.format(
                            #         s_index, j, i))
                            #     f.write('#\n')

                            written_springs.append(s_index)

                        orientation = ' '.join([str(k) for k in ey])

                        self.write_line('element twoNodeLink {0} {1} {2} -mat 2{3:0>3} -dir 1 -orient {4}'.format(n, nodes[0], nodes[1], s_index, orientation))

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        if section.stiffness:

                            b1 = 'BEH_{0}'.format(section.name)

                            if b1 not in written_springs:
                                self.write_line('*CONNECTOR BEHAVIOR, NAME={0}'.format(b1))

                                if kx:
                                    self.write_line('*CONNECTOR ELASTICITY, COMPONENT=1')
                                    self.write_line('{0}'.format(kx))

                        #         elif section.forces['axial'] and section.displacements['axial']:
                        #             f.write('*CONNECTOR ELASTICITY, COMPONENT=1, NONLINEAR\n')
                        #             for i, j in zip(section.forces['axial'], section.displacements['axial']):
                        #                 f.write('{0}, {1}\n'.format(i, j))

                                written_springs.append(b1)

                                self.blank_line()

                            e = 'element_{0}'.format(select)
                            self.write_line('*ELEMENT, TYPE=CONN3D2, ELSET={0}'.format(e))
                            self.write_line('{0}, {1},{2}'.format(n, nodes[0], nodes[1]))

                            self.write_line('*ORIENTATION, NAME=ORI_{0}'.format(select))
                            self.write_line(', '.join([str(k) for k in ez]) + ', ' + ', '.join([str(k) for k in ey]))

                            self.write_line('*CONNECTOR SECTION, ELSET={0}, BEHAVIOR={1}'.format(e, b1))
                            self.write_line('AXIAL')
                            self.write_line('ORI_{0}'.format(select))

                # =====================================================================================================
                # =====================================================================================================
                # MASS
                # =====================================================================================================
                # =====================================================================================================

                elif stype == 'MassSection':

                    # -------------------------------------------------------------------------------------------------
                    # OpenSees
                    # -------------------------------------------------------------------------------------------------

                    if self.software == 'opensees':

                        raise NotImplementedError

                    # -------------------------------------------------------------------------------------------------
                    # Abaqus
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'abaqus':

                        e = 'element_{0}'.format(select)

                        self.write_line('*ELEMENT, TYPE=MASS, ELSET={0}'.format(e))
                        self.write_line('{0}, {1}'.format(n, ','.join(nodes)))
                        self.write_line('*MASS, ELSET={0}'.format(e))
                        self.write_line(element.mass)

                    # -------------------------------------------------------------------------------------------------
                    # Ansys
                    # -------------------------------------------------------------------------------------------------

                    elif self.software == 'ansys':

                        raise NotImplementedError

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

#         f.write('{0}\n'.format(comments[software]))
