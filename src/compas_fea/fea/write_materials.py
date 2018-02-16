
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import pi
from math import sqrt


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
    'sofistik': '+PROG AQUA\nHEAD AQUA\n$\nNORM DC SIA NDC 262\n',
    'ansys':    '',
}

footers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': 'END\n$\n$\n',
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
    f.write('{0}\n'.format(c))

    if headers[software]:
        f.write('{0}'.format(headers[software]))
        f.write('{0}\n'.format(c))

    for key, material in materials.items():

        if software == 'abaqus':
            f.write('*MATERIAL, NAME={0}\n'.format(key))
            f.write('**\n')

        mtype = material.__name__
        material_index = material.index + 1
        compression = material.compression
        tension     = material.tension
        E = material.E['E']
        G = material.G['G']
        v = material.v['v']
        p = material.p

        f.write('{0} {1}\n'.format(c, key))
        f.write('{0} '.format(c) + '-' * len(key) + '\n')
        f.write('{0}\n'.format(c))

        if mtype == 'ElasticIsotropic':

            _write_elastic(f, software, E, G, v, p, compression, tension, c, material_index)

        # ElasticOrthotropic

        elif mtype == 'ElasticOrthotropic':

            raise NotImplementedError

        # Elastic--Plastic

        elif mtype == 'ElasticPlastic':

            _write_elastic_plastic(f, software, E, v, tension, c)

        # Steel

        elif mtype == 'Steel':

            _write_steel(f, software, E, v, p, tension, c, material_index, material)

        # Cracked Concrete

        elif mtype == 'ConcreteSmearedCrack':

            _write_cracked_concrete(f, software, E, v, compression, tension, material)

        # Concrete

        elif mtype == 'Concrete':

            _write_concrete(f, software, E, v, p, compression, tension, material_index, material)

        # Concrete damaged plasticity

        elif mtype == 'ConcreteDamagedPlasticity':

            _write_plasticity_concrete(f, software, material)

        # Thermal

        elif mtype == 'ThermalMaterial':

            _write_thermal(f, software, material)

        # Density

        _write_density(f, software, p, c)

    if software == 'sofistik':

        _write_sofistik_sections(f, properties, materials, sections)

    if footers[software]:
        f.write('{0}'.format(footers[software]))


def _write_sofistik_sections(f, properties, materials, sections):

    f.write('$\n')
    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ -------------------------------------------------------------------- Sections\n')
    f.write('$\n')

    for key, property in properties.items():

        section = sections[property.section]
        section_index = section.index + 1
        stype = section.__name__
        geometry = section.geometry
        if property.material:
            material_index = materials[property.material].index + 1
        else:
            material_index = None

        if stype not in ['SolidSection', 'ShellSection', 'SpringSection']:

            f.write('$ {0}\n'.format(section.name))
            f.write('$ ' + '-' * len(section.name) + '\n')
            f.write('$\n')

            if stype in ['PipeSection', 'CircularSection']:

                D = geometry['r'] * 2 * 1000
                t = geometry['t'] * 1000 if stype == 'PipeSection' else 0
                f.write('TUBE NO {0} D {1} T {2} MNO {3}\n'.format(section_index, D, t, material_index))

            elif stype == 'RectangularSection':

                pass

            elif stype in ['TrussSection']:

                D = sqrt(geometry['A'] * 4 / pi) * 1000
                f.write('TUBE NO {0} D {1} T {2} MNO {3}\n'.format(section_index, D, 0, material_index))

            f.write('$\n')


def _write_elastic(f, software, E, G, v, p, compression, tension, c, material_index):

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

        if not compression:
            f.write('*NO COMPRESSION\n')
        if not tension:
            f.write('*NO TENSION\n')

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        E /= 10**6
        G /= 10**6
        yc = p / 100
        f.write('MATE {0} E {1} MUE {2} G {3} GAM {4}\n'.format(material_index, E, v, G, yc))

    elif software == 'ansys':

        pass

    f.write('{0}\n'.format(c))


def _write_density(f, software, p, c):

    if software == 'abaqus':

        f.write('*DENSITY\n')

        if isinstance(p, list):
            f.write('** p[kg/m3], T[C]\n')
            f.write('**\n')
            for pj, T in p:
                f.write('{0}, {1}\n'.format(pj, T))

        else:
            f.write('** p[kg/m3]\n')
            f.write('**\n')
            f.write('{0}\n'.format(p))

        f.write('**\n')

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        pass

    elif software == 'ansys':

        pass


def _write_elastic_plastic(f, software, E, v, tension, c):

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

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        pass

    elif software == 'ansys':

        pass

    f.write('{0}\n'.format(c))


def _write_steel(f, software, E, v, p, tension, c, material_index, material):

    if software == 'abaqus':

        _write_elastic_plastic(f, software, E, v, tension, c)

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        id = 'B' if material.id == 'r' else 'S'
        E /= 10**6
        yc = p / 100
        fy = material.fy / 10.**6
        fu = material.fu / 10.**6
        sf = material.sf
        eyp = 1000 * fy / E
        eup = 10 * material.eu
        f.write('STEE {0} {1} ES {2} GAM {3} FY {4} FT {5} FP {4} SCM {6} EPSY {7} EPST {8} MUE {9}\n'.format(
            material_index, id, E, yc, fy, fu, sf, eyp, eup, v))
        f.write('$\n')

    elif software == 'ansys':

        pass


def _write_cracked_concrete(f, software, E, v, compression, tension, material):

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

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        pass

    elif software == 'ansys':

        pass


def _write_concrete(f, software, E, v, p, compression, tension, material_index, material):

    if software == 'abaqus':

        _write_cracked_concrete(f, software, E, v, compression, tension, material)

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        fck = material.fck / 10.**6
        yc = p / 100
        f.write('CONC {0} TYPE C FCN {1} MUE {2} GAM {3} TYPR C\n'.format(material_index, fck, v, yc))
        f.write('$\n')

    elif software == 'ansys':

        pass


def _write_thermal(f, software, material):

    if software == 'abaqus':

        f.write('**\n')
        f.write('*CONDUCTIVITY\n')
        f.write('** k[W/mK]\n')
        f.write('**\n')
        for i in material.conductivity:
            f.write(', '.join([str(j) for j in i]) + '\n')

        f.write('**\n')
        f.write('*SPECIFIC HEAT\n')
        f.write('** c[J/kgK]\n')
        f.write('**\n')
        for i in material.sheat:
            f.write(', '.join([str(j) for j in i]) + '\n')

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        pass

    elif software == 'ansys':

        pass


def _write_plasticity_concrete(f, software, material):

    if software == 'abaqus':

        f.write('**\n')
        f.write('*CONCRETE DAMAGED PLASTICITY\n')
        f.write('** psi[deg], e[-], sr[-], Kc[-], mu[-]\n')
        f.write('**\n')
        f.write(', '.join([str(i) for i in material.damage]) + '\n')
        f.write('**\n')

        f.write('*CONCRETE COMPRESSION HARDENING\n')
        f.write('** fy[Pa], eu[-], , T[C]\n')
        f.write('**\n')
        for i in material.hardening:
            f.write(', '.join([str(j) for j in i]) + '\n')
        f.write('**\n')

        f.write('*CONCRETE TENSION STIFFENING, TYPE=GFI\n')
        f.write('** ft[Pa], et[-], etd[1/s], T[C]\n')
        f.write('**\n')
        for i in material.stiffening:
            f.write(', '.join([str(j) for j in i]) + '\n')

    elif software == 'opensees':

        pass

    elif software == 'sofistik':

        pass

    elif software == 'ansys':

        pass
