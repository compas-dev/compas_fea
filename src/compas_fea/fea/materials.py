
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

headers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': '+PROG AQUA\nHEAD AQUA\nNORM DC SIA NDC 262\n$\n$',
    'ansys':    '',
}


class Materials(object):

    def __init__(self):

        pass


    def write_materials(self):

        self.write_section('Materials')
        self.blank_line()

        materials = self.structure.materials

        if headers[self.software]:
            self.write_line(headers[self.software])

        for key, material in materials.items():

            self.write_subsection(key)

            mtype       = material.__name__
            mindex      = material.index + 1
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

                    self.write_line('uniaxialMaterial Elastic {0} {1}'.format(mindex, E['E']))
                    self.write_line('nDMaterial ElasticIsotropic {0} {1} {2} {3}'.format(
                                    mindex + 100, E['E'], v['v'], p))

            # ------------------------------------------------------------------------------------------------------
            # Sofistik
            # ------------------------------------------------------------------------------------------------------

            elif self.software == 'sofistik':

                # Elastic
                # -------

                if mtype == 'ElasticIsotropic':

                    self.write_line('MATE {0} E {1}[MPa] MUE {2} G {3:.1f}[MPa] GAM {4}'.format(
                                    mindex, E['E'] * MPa, v['v'], G['G'] * MPa, p * 0.01))

            # ------------------------------------------------------------------------------------------------------
            # Abaqus
            # ------------------------------------------------------------------------------------------------------

            elif self.software == 'abaqus':

                self.write_line('*MATERIAL, NAME={0}'.format(key))
                self.blank_line()

                # Elastic
                # -------

                if mtype in ['ElasticIsotropic']:

                    self.write_line('*ELASTIC')
                    self.blank_line()
                    self.write_line('{0}, {1}'.format(E['E'], v['v']))

                    if not compression:
                        self.write_line('*NO COMPRESSION')

                    if not tension:
                        self.write_line('*NO TENSION')

            # ------------------------------------------------------------------------------------------------------
            # Ansys
            # ------------------------------------------------------------------------------------------------------

            elif self.software == 'ansys':

                pass

        self.blank_line()
        self.blank_line()
























        #     # Stiff

        #     elif mtype == 'Stiff':
        #         _write_elastic(f, software, E, G, v, p, compression, tension, c, mindex)

        #     # ElasticOrthotropic

        #     elif mtype == 'ElasticOrthotropic':
        #         raise NotImplementedError

        #     # Elastic--Plastic

        #     elif mtype == 'ElasticPlastic':
        #         _write_elastic_plastic(f, software, E, v, tension, c)

        #     # Steel

        #     elif mtype == 'Steel':
        #         _write_steel(f, software, E, v, p, tension, c, mindex, material)

        #     # Cracked Concrete

        #     elif mtype == 'ConcreteSmearedCrack':
        #         _write_cracked_concrete(f, software, E, v, compression, tension, material, c)

        #     # Concrete

        #     elif mtype == 'Concrete':
        #         _write_concrete(f, software, E, v, p, compression, tension, mindex, material, c)

        #     # Concrete damaged plasticity

        #     elif mtype == 'ConcreteDamagedPlasticity':
        #         _write_plasticity_concrete(f, software, material, c, E, v)

        #     # Thermal

        #     elif mtype == 'ThermalMaterial':
        #         _write_thermal(f, software, material, c)

        #     # Density

        #     _write_density(f, software, p, c)

        # f.write('{0}\n'.format(c))



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


# from compas_fea.fea.write_elements import _write_sofistik_sections












# # ==============================================================================
# # Plastic
# # ==============================================================================

# def _write_elastic_plastic(f, software, E, v, tension, c):

#     if software == 'abaqus':

#         f.write('*ELASTIC\n')
#         f.write('** E[Pa], v[-]\n')
#         f.write('**\n')
#         f.write('{0}, {1}\n'.format(E, v))
#         f.write('**\n')

#         f.write('*PLASTIC\n')
#         f.write('** f[Pa], e[-] : compression-tension\n')
#         f.write('**\n')

#         for i, j in zip(tension['f'], tension['e']):
#             f.write('{0}, {1}\n'.format(i, j))

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         pass

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


# # ==============================================================================
# # Metals
# # ==============================================================================

# def _write_steel(f, software, E, v, p, tension, c, mindex, material):

#     if software == 'abaqus':

#         _write_elastic_plastic(f, software, E, v, tension, c)

#     elif software == 'opensees':

#         fy = material.fy
#         fu = material.fu
#         ep = material.ep
#         EshE = (fu - fy) / ep

#         f.write('uniaxialMaterial Steel01 {0} {1} {2} {3}\n#\n'.format(mindex, fy, E, EshE))

#     elif software == 'sofistik':

#         it = 'B' if material.id == 'r' else 'S'
#         fy = material.fy
#         fu = material.fu
#         sf = material.sf
#         eyp = 1000 * fy / E
#         eup = 1000 * material.eu

#         f.write('STEE {0} {1} ES {2} GAM {3} FY {4} FT {5} FP {4} SCM {6} EPSY {7} EPST {8} MUE {9}\n$\n'.format(mindex, it, E * MPa, p * 0.01, fy * MPa, fu * MPa, sf, eyp, eup, v))

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


# # ==============================================================================
# # Concrete
# # ==============================================================================

# def _write_cracked_concrete(f, software, E, v, compression, tension, material, c):

#     if software == 'abaqus':

#         f.write('*ELASTIC\n')
#         f.write('** E[Pa], v[-]\n')
#         f.write('**\n')
#         f.write('{0}, {1}\n'.format(E, v))
#         f.write('**\n')

#         f.write('*CONCRETE\n')
#         f.write('** f[Pa], e[-] : compression\n')
#         f.write('**\n')

#         for cf, ce in zip(compression['f'], compression['e']):
#             f.write('{0}, {1}\n'.format(cf, ce))

#         f.write('**\n')
#         f.write('*TENSION STIFFENING\n')
#         f.write('** f[Pa], e[-] : tension\n')
#         f.write('**\n')

#         for tf, te in zip(tension['f'], tension['e']):
#             f.write('{0}, {1}\n'.format(tf, te))

#         f.write('**\n')
#         f.write('*FAILURE RATIOS\n')

#         a, b = material.fratios

#         f.write('{0}, {1}\n'.format(a, b))

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         pass

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


# def _write_concrete(f, software, E, v, p, compression, tension, mindex, material, c):

#     if software == 'abaqus':

#         _write_cracked_concrete(f, software, E, v, compression, tension, material, c)

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         f.write('CONC {0} TYPE C FCN {1} MUE {2} GAM {3} TYPR C SCM {4}\n'.format(
#                 mindex, material.fck * MPa, v, p * 0.01, material.sf))
#         f.write('$\n')

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


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

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         pass

#     elif software == 'ansys':

#         pass

#     f.write('{0}\n'.format(c))


# # ==============================================================================
# # Density
# # ==============================================================================

# def _write_density(f, software, p, c):

#     if software == 'abaqus':

#         f.write('*DENSITY\n')

#         if isinstance(p, list):
#             f.write('** p[kg/m3], T[C]\n')
#             f.write('**\n')

#             for pj, T in p:
#                 f.write('{0}, {1}\n'.format(pj, T))

#         else:
#             f.write('** p[kg/m3]\n')
#             f.write('**\n')
#             f.write('{0}\n'.format(p))

#         f.write('**\n')

#     elif software == 'opensees':

#         pass

#     elif software == 'sofistik':

#         pass

#     elif software == 'ansys':

#         pass
