from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Materials',
]

MPa = 10**(-6)
GPa = 10**(-9)


class Materials(object):

    def __init__(self):
        pass

    def write_materials(self):

        self.write_section('Materials')
        self.blank_line()

        materials = self.structure.materials

        for key, material in materials.items():

            self.write_subsection(key)

            mtype = material.__name__
            m_index = material.index + 1
            compression = getattr(material, 'compression', None)
            tension = getattr(material, 'tension', None)
            E = material.E
            # G = material.G
            v = material.v
            p = material.p

            # ------------------------------------------------------------------------------------------------------
            # OpenSees
            # ------------------------------------------------------------------------------------------------------

            if self.software == 'opensees':

                # Elastic
                # -------

                if mtype == 'ElasticIsotropic':

                    self.write_line('uniaxialMaterial Elastic {0} {1}'.format(m_index, E['E']))
                    self.write_line('nDMaterial ElasticIsotropic {0} {1} {2} {3}'.format(
                                    m_index + 1000, E['E'], v['v'], p))

                elif mtype == 'Steel':

                    fy = material.fy
                    fu = material.fu
                    ep = material.ep
                    EshE = (fu - fy) / ep

                    self.write_line('uniaxialMaterial Steel01 {0} {1} {2} {3}'.format(m_index, fy, E['E'], EshE))

            # ------------------------------------------------------------------------------------------------------
            # Abaqus
            # ------------------------------------------------------------------------------------------------------

            elif self.software == 'abaqus':

                self.write_line('*MATERIAL, NAME={0}'.format(key))
                self.blank_line()

                # Elastic
                # -------

                if mtype in ['ElasticIsotropic', 'ElasticPlastic', 'Steel', 'Concrete', 'Stiff',
                             'ConcreteSmearedCrack', 'ConcreteDamagedPlasticity']:

                    self.write_line('*ELASTIC')
                    self.blank_line()
                    self.write_line('{0}, {1}'.format(E['E'], v['v']))

                    if not compression:
                        self.write_line('*NO COMPRESSION')

                    if not tension:
                        self.write_line('*NO TENSION')

                # Compression
                # -----------

                if mtype in ['ElasticPlastic', 'Steel', 'Concrete', 'ConcreteSmearedCrack',
                             'ConcreteDamagedPlasticity']:

                    if mtype in ['Concrete', 'ConcreteSmearedCrack']:

                        self.blank_line()
                        self.write_line('*CONCRETE')
                        self.blank_line()

                        for i, j in zip(compression['f'], compression['e']):
                            self.write_line('{0}, {1}'.format(i, j))

                    elif mtype == 'ConcreteDamagedPlasticity':

                        self.blank_line()
                        self.write_line('*CONCRETE DAMAGED PLASTICITY')
                        self.blank_line()

                        self.write_line(', '.join([str(i) for i in material.damage]))

                        self.blank_line()
                        self.write_line('*CONCRETE COMPRESSION HARDENING')
                        self.blank_line()

                        for i in material.hardening:
                            self.write(', '.join([str(j) for j in i]))

                    else:

                        self.blank_line()
                        self.write_line('*PLASTIC')
                        self.blank_line()

                        for i, j in zip(compression['f'], compression['e']):
                            self.write_line('{0}, {1}'.format(abs(i), abs(j)))

                # Tension
                # -------

                if mtype in ['Concrete', 'ConcreteSmearedCrack']:

                    self.blank_line()
                    self.write_line('*TENSION STIFFENING')
                    self.blank_line()

                    for i, j in zip(tension['f'], tension['e']):
                        self.write_line('{0}, {1}'.format(i, j))

                    self.blank_line()
                    self.write_line('*FAILURE RATIOS')
                    self.blank_line()

                    a, b = material.fratios

                    self.write_line('{0}, {1}'.format(a, b))

                elif mtype == 'ConcreteDamagedPlasticity':

                    self.blank_line()
                    self.write_line('*CONCRETE TENSION STIFFENING, TYPE=GFI')
                    self.blank_line()

                    for i in material.stiffening:
                        self.write_line(', '.join([str(j) for j in i]))

                # Density
                # -------

                self.blank_line()
                self.write_line('*DENSITY')
                self.blank_line()

                if isinstance(p, list):
                    for pi, T in p:
                        self.write_line('{0}, {1}'.format(pi, T))
                else:
                    self.write_line(str(p))

            # ------------------------------------------------------------------------------------------------------
            # Ansys
            # ------------------------------------------------------------------------------------------------------

            elif self.software == 'ansys':

                pass

            self.blank_line()

        self.blank_line()
        self.blank_line()


# f.write('*CONDUCTIVITY\n')
# f.write('** k[W/mK]\n')
# f.write('**\n')

# for i in material.conductivity:
#     f.write(', '.join([str(j) for j in i]) + '\n')

# f.write('**\n')
# f.write('*SPECIFIC HEAT\n')
# f.write('** c[J/kgK]\n')
# f.write('**\n')

# for i in material.sheat:
#     f.write(', '.join([str(j) for j in i]) + '\n')
