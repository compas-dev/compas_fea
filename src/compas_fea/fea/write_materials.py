
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_materials',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}

headers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': '$\nNORM DC SIA NDC 262\n',
    'ansys':    '',
}


def write_input_materials(f, software, materials, sections=None, properties=None):

    """ Writes materials to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    materials : dic
        Material objects from structure.materials.
    sections : dic
        Section objects from structure.sections (for Sofistik).
    properties : dic
        ElementProperties objects from structure.element_properties (for Sofistik).

    Returns
    -------
    None

    """

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ------------------------------------------------------------------- Materials\n'.format(c))

    if headers[software]:
        f.write('{0}'.format(headers[software]))

    for key, material in materials.items():

        leaders = {
            'abaqus':   '*MATERIAL, NAME={0}'.format(key),
            'opensees': '',
            'sofistik': '',
            'ansys':    '',
        }

        mtype = material.__name__
        material_index = material.index + 1
        compression = material.compression
        tension = material.tension
        E = material.E['E']
        v = material.v['v']
        density = material.p
        yc = density / 100

        f.write('{0}\n'.format(c))
        f.write('{0} {1}\n'.format(c, key))
        f.write('{0} '.format(c) + '-' * len(key) + '\n')
        f.write('{0}\n'.format(c))
        if leaders[software]:
            f.write('{0}\n'.format(leaders[software]))
            f.write('{0}\n'.format(c))

        # ElasticOrthotropic

        if mtype == 'ElasticOrthotropic':
            raise NotImplementedError

        elif mtype == 'ElasticIsotropic':

            if software == 'abaqus':

                f.write('*ELASTIC\n')

                if isinstance(E, list):
                    f.write('** E[Pa], v[-], T[C]\n')
                    f.write('**\n')
                    for j in range(len(E)):
                        f.write('{0}, {1}, {2}\n'.format(E[j][0], v[j][0], E[j][1]))
                else:
                    f.write('** E[Pa], v[-]\n')
                    f.write('**\n')
                    f.write('{0}, {1}\n'.format(E, v))

                if not material.compression:
                    f.write('*NO COMPRESSION\n')
                if not material.tension:
                    f.write('*NO TENSION\n')

                f.write('**\n')
                f.write('*DENSITY\n')

                if isinstance(density, list):
                    f.write('** p[kg/m3], T[C]\n')
                    f.write('**\n')
                    for p, T in density:
                        f.write('{0}, {1}\n'.format(p, T))

                else:
                    f.write('** p[kg/m3]\n')
                    f.write('**\n')
                    f.write('{0}\n'.format(density))

            elif software == 'opensees':
                pass

            elif software == 'sofistik':
                pass

        # Concrete

        elif mtype in ['ConcreteSmearedCrack', 'Concrete']:

            if software == 'abaqus':

                f.write('*ELASTIC\n')
                f.write('** E[Pa], v[-]\n')
                f.write('**\n')
                f.write('{0}, {1}\n'.format(E, v))
                f.write('**\n')

                f.write('*CONCRETE\n')
                f.write('** f[Pa], e[-] : compression\n')
                f.write('**\n')
                for cf, ce in zip(compression['f'], compression['e']):
                    f.write('{0}, {1}\n'.format(cf, ce))
                f.write('**\n')

                f.write('*TENSION STIFFENING\n')
                f.write('** f[Pa], e[-] : tension\n')
                f.write('**\n')
                for tf, te in zip(tension['f'], tension['e']):
                    f.write('{0}, {1}\n'.format(tf, te))

                f.write('**\n')
                f.write('*FAILURE RATIOS\n')
                a, b = material.fratios
                f.write('{0}, {1}\n'.format(a, b))

                f.write('**\n')
                f.write('*DENSITY\n')
                f.write('** p[kg/m3]\n')
                f.write('**\n')
                f.write('{0}\n'.format(density))

            elif software == 'opensees':
                pass

            elif software == 'sofistik':

                fck = material.fck
                f.write('CONC {0} TYPE C FCN {1} MUE {2} GAM {3} TYPR C\n'.format(material_index, fck, v, yc))

        # Concrete damaged plasticity

        elif mtype == 'ConcreteDamagedPlasticity':

            if software == 'abaqus':

                pass

                # f.write('**\n')
                # f.write('*CONCRETE DAMAGED PLASTICITY\n')
                # f.write('** psi[deg], e[-], sr[-], Kc[-], mu[-]\n')
                # f.write('**\n')
                # f.write(', '.join([str(i) for i in material.damage]) + '\n')
                # f.write('**\n')

                # f.write('*CONCRETE COMPRESSION HARDENING\n')
                # f.write('** fy[Pa], eu[-], , T[C]\n')
                # f.write('**\n')
                # for i in material.hardening:
                #     f.write(', '.join([str(j) for j in i]) + '\n')
                # f.write('**\n')

                # f.write('*CONCRETE TENSION STIFFENING, TYPE=GFI\n')
                # f.write('** ft[Pa], et[-], etd[1/s], T[C]\n')
                # f.write('**\n')
                # for i in material.stiffening:
                #     f.write(', '.join([str(j) for j in i]) + '\n')

            elif software == 'opensees':

                pass

            elif software == 'sofistik':

                pass

        # Elastic--Plastic

        elif mtype in ['ElasticPlastic', 'Steel']:

            if software == 'abaqus':

                f.write('*ELASTIC\n')
                f.write('** E[Pa], v[-]\n')
                f.write('**\n')
                f.write('{0}, {1}\n'.format(E, v))
                f.write('**\n')

                f.write('*PLASTIC\n')
                f.write('** f[Pa], e[-] : compression-tension\n')
                f.write('**\n')
                for i, j in zip(tension['f'], tension['e']):
                    f.write('{0}, {1}\n'.format(i, j))

                f.write('**\n')
                f.write('*DENSITY\n')
                f.write('** p[kg/m3]\n')
                f.write('**\n')
                f.write('{0}\n'.format(density))

            elif software == 'opensees':

                pass

            elif software == 'sofistik':

                id = 'S'
                if material.id == 'r':
                    id = 'B'
                fy = material.fy
                fu = material.fu
                sf = material.sf
                E /= 10**6
                eyp = 1000 * fy / E
                eup = 10 * material.eu
                f.write('STEE {0} {1} ES {2} GAM {3} FY {4} FT {5} FP {4} SCM {6} EPSY {7} EPST {8} MUE {9}\n'.format(
                    material_index, id, E, yc, fy, fu, sf, eyp, eup, v))

        # Thermal

        elif mtype == 'ThermalMaterial':

            if software == 'abaqus':

                pass

                # f.write('**\n')
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

            elif software == 'opensees':

                pass

            elif software == 'sofistik':

                pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))

    if software == 'sofistik':

        f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
        f.write('{0} -------------------------------------------------------------------- Sections\n'.format(c))

        for key, property in properties.items():

            section = sections[property.section]
            section_index = section.index + 1
            material = materials[property.material]
            material_index = material.index + 1
            geometry = section.geometry
            stype = section.__name__

            if stype in ['PipeSection']:

                f.write('{0}\n'.format(c))
                f.write('{0} {1}\n'.format(c, section.name))
                f.write('{0} '.format(c) + '-' * len(section.name) + '\n')
                f.write('{0}\n'.format(c))

                if stype == 'PipeSection':

                    D = geometry['r'] * 2 * 1000
                    t = geometry['t'] * 1000
                    f.write('TUBE NO {0} D {1} T {2} MNO {3}\n'.format(section_index, D, t, material_index))

        f.write('{0}\n'.format(c))
        f.write('{0}\n'.format(c))
