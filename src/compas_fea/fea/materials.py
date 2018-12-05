
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


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

            mtype       = material.__name__
            m_index     = material.index + 1
            compression = getattr(material, 'compression', None)
            tension     = getattr(material, 'tension', None)
            E           = material.E
            G           = material.G
            v           = material.v
            p           = material.p

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

                if mtype in ['ElasticIsotropic', 'ElasticPlastic', 'Steel', 'Concrete', 'Stiff']:

                    self.write_line('*ELASTIC')
                    self.blank_line()
                    self.write_line('{0}, {1}'.format(E['E'], v['v']))

                    if not compression:
                        self.write_line('*NO COMPRESSION')

                    if not tension:
                        self.write_line('*NO TENSION')

                # Plastic
                # -------

                if mtype in ['ElasticPlastic', 'Steel', 'Concrete']:

                    if mtype == 'Concrete':

                        self.blank_line()
                        self.write_line('*CONCRETE')
                        self.blank_line()

                        for i, j in zip(compression['f'], compression['e']):
                            self.write_line('{0}, {1}'.format(i, j))

                    else:

                        self.blank_line()
                        self.write_line('*PLASTIC')
                        self.blank_line()

                        for i, j in zip(tension['f'], tension['e']):
                            self.write_line('{0}, {1}'.format(i, j))

                # Tension
                # -------

                if mtype in ['Concrete']:

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
























        #     # ElasticOrthotropic

        #     elif mtype == 'ElasticOrthotropic':
        #         raise NotImplementedError

        #     # Cracked Concrete

        #     elif mtype == 'ConcreteSmearedCrack':
        #         _write_cracked_concrete(f, software, E, v, compression, tension, material, c)

        #     # Concrete

        #     elif mtype == 'Concrete':
        #         _write_concrete(f, software, E, v, p, compression, tension, m_index, material, c)

        #     # Concrete damaged plasticity

        #     elif mtype == 'ConcreteDamagedPlasticity':
        #         _write_plasticity_concrete(f, software, material, c, E, v)

        #     # Thermal

        #     elif mtype == 'ThermalMaterial':
        #         _write_thermal(f, software, material, c)



#         sets          = self.structure.sets
#         steps         = self.structure.steps
#         displacements = self.structure.displacements

#         try:

#             step = steps[self.structure.steps_order[0]]

#             if isinstance(step.displacements, str):
#                 step.displacements = [step.displacements]


#         except:

#             print('***** Error writing boundary conditions, check Step exists in structure.steps_order[0] *****')

#         self.blank_line()
#         self.blank_line()




# def _write_plasticity_concrete(f, software, material, c, E, v):

#     if software == 'abaqus':

#         f.write('*ELASTIC\n')
#         f.write('** E[Pa], v[-]\n')
#         f.write('**\n')
#         f.write('{0}, {1}\n'.format(E, v))
#         f.write('**\n')

#         f.write('*CONCRETE DAMAGED PLASTICITY\n')
#         f.write('** psi[deg], e[-], sr[-], Kc[-], mu[-]\n')
#         f.write('**\n')
#         f.write(', '.join([str(i) for i in material.damage]) + '\n')
#         f.write('**\n')

#         f.write('*CONCRETE COMPRESSION HARDENING\n')
#         f.write('** fy[Pa], eu[-], , T[C]\n')
#         f.write('**\n')

#         for i in material.hardening:
#             f.write(', '.join([str(j) for j in i]) + '\n')

#         f.write('**\n')
#         f.write('*CONCRETE TENSION STIFFENING, TYPE=GFI\n')
#         f.write('** ft[Pa], et[-], etd[1/s], T[C]\n')
#         f.write('**\n')

#         for i in material.stiffening:
#             f.write(', '.join([str(j) for j in i]) + '\n')

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         pass

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


# # ==============================================================================
# # Thermal
# # ==============================================================================

# def _write_thermal(f, software, material, c):

#     if software == 'abaqus':

#         f.write('*CONDUCTIVITY\n')
#         f.write('** k[W/mK]\n')
#         f.write('**\n')

#         for i in material.conductivity:
#             f.write(', '.join([str(j) for j in i]) + '\n')

#         f.write('**\n')
#         f.write('*SPECIFIC HEAT\n')
#         f.write('** c[J/kgK]\n')
#         f.write('**\n')

#         for i in material.sheat:
#             f.write(', '.join([str(j) for j in i]) + '\n')

#     f.write('{0}\n'.format(c))

