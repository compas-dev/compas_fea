from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import log


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'Material',
    'Concrete',
    'ConcreteSmearedCrack',
    'ConcreteDamagedPlasticity',
    'ElasticIsotropic',
    'Stiff',
    'ElasticOrthotropic',
    'ElasticPlastic',
    # 'ThermalMaterial',
    'Steel'
]


class Material(object):
    """Initialises base Material object.

    Parameters
    ----------
    name : str
        Name of the Material object.

    Attributes
    ----------
    name : str
        Name of the Material object.

    """

    def __init__(self, name):

        self.__name__ = 'Material'
        self.name = name
        self.attr_list = ['name']

    def __str__(self):
        print('\n')
        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 18))

        for attr in self.attr_list:
            print('{0:<11} : {1}'.format(attr, getattr(self, attr)))

        return ''

    def __repr__(self):
        return '{0}({1})'.format(self.__name__, self.name)


# ==============================================================================
# linear elastic
# ==============================================================================

class ElasticIsotropic(Material):
    """Elastic, isotropic and homogeneous material.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus E [Pa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].
    tension : bool
        Can take tension.
    compression : bool
        Can take compression.

    """

    def __init__(self, name, E, v, p, tension=True, compression=True):
        Material.__init__(self, name=name)

        self.__name__ = 'ElasticIsotropic'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = tension
        self.compression = compression
        self.attr_list.extend(['E', 'v', 'G', 'p', 'tension', 'compression'])


class Stiff(ElasticIsotropic):
    """Elastic, very stiff and massless material.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus E [Pa].

    """

    def __init__(self, name, E=10**13):
        ElasticIsotropic.__init__(self, name=name, E=E, v=0.3, p=10**(-1))

        self.__name__ = 'Stiff'


class ElasticOrthotropic(Material):
    """Elastic, orthotropic and homogeneous material.

    Parameters
    ----------
    name : str
        Material name.
    Ex : float
        Young's modulus Ex in x direction [Pa].
    Ey : float
        Young's modulus Ey in y direction [Pa].
    Ez : float
        Young's modulus Ez in z direction [Pa].
    vxy : float
        Poisson's ratio vxy in x-y directions [-].
    vyz : float
        Poisson's ratio vyz in y-z directions [-].
    vzx : float
        Poisson's ratio vzx in z-x directions [-].
    Gxy : float
        Shear modulus Gxy in x-y directions [Pa].
    Gyz : float
        Shear modulus Gyz in y-z directions [Pa].
    Gzx : float
        Shear modulus Gzx in z-x directions [Pa].
    p : float
        Density [kg/m3].
    tension : bool
        Can take tension.
    compression : bool
        Can take compression.

    Notes
    -----
    - Can be created but is currently not implemented.

    """

    def __init__(self, name, Ex, Ey, Ez, vxy, vyz, vzx, Gxy, Gyz, Gzx, p, tension=True, compression=True):
        Material.__init__(self, name=name)

        self.__name__ = 'ElasticOrthotropic'
        self.name = name
        self.E = {'Ex': Ex, 'Ey': Ey, 'Ez': Ez}
        self.v = {'vxy': vxy, 'vyz': vyz, 'vzx': vzx}
        self.G = {'Gxy': Gxy, 'Gyz': Gyz, 'Gzx': Gzx}
        self.p = p
        self.tension = tension
        self.compression = compression
        self.attr_list.extend(['E', 'v', 'G', 'p', 'tension', 'compression'])


# ==============================================================================
# non-linear general
# ==============================================================================

class ElasticPlastic(Material):
    """Elastic and plastic, isotropic and homogeneous material.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus E [Pa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].
    f : list
        Plastic stress data (positive tension values) [Pa].
    e : list
        Plastic strain data (positive tension values) [-].

    Notes
    -----
    - Plastic stress--strain pairs applies to both compression and tension.

    """

    def __init__(self, name, E, v, p, f, e):
        Material.__init__(self, name=name)

        fc = [-i for i in f]
        ec = [-i for i in e]

        self.__name__ = 'ElasticPlastic'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = {'f': f, 'e': e}
        self.compression = {'f': fc, 'e': ec}
        self.attr_list.extend(['E', 'v', 'G', 'p', 'tension', 'compression'])


# ==============================================================================
# non-linear metal
# ==============================================================================

class Steel(Material):
    """Bi-linear steel with given yield stress.

    Parameters
    ----------
    name : str
        Material name.
    fy : float
        Yield stress [MPa].
    fu : float
        Ultimate stress [MPa].
    eu : float
        Ultimate strain [%].
    E : float
        Young's modulus E [GPa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].

    """

    def __init__(self, name, fy=355, fu=None, eu=20, E=210, v=0.3, p=7850):
        Material.__init__(self, name=name)

        E *= 10.**9
        fy *= 10.**6
        eu *= 0.01

        if not fu:
            fu = fy
        else:
            fu *= 10.**6

        ep = eu - fy / E
        f = [fy, fu]
        e = [0, ep]
        fc = [-i for i in f]
        ec = [-i for i in e]

        self.__name__ = 'Steel'
        self.name = name
        self.fy = fy
        self.fu = fu
        self.eu = eu
        self.ep = ep
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = {'f': f, 'e': e}
        self.compression = {'f': fc, 'e': ec}
        self.attr_list.extend(['fy', 'fu', 'eu', 'ep', 'E', 'v', 'G', 'p', 'tension', 'compression'])


# ==============================================================================
# non-linear timber
# ==============================================================================


# ==============================================================================
# non-linear masonry
# ==============================================================================


# ==============================================================================
# non-linear concrete
# ==============================================================================

class Concrete(Material):
    """Elastic and plastic-cracking Eurocode based concrete material.

    Parameters
    ----------
    name : str
        Material name.
    fck : float
        Characteristic (5%) 28 day cylinder strength [MPa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].
    fr : list
        Failure ratios.

    Notes
    -----
    - The concrete model is based on Eurocode 2 up to fck=90 MPa.

    """

    def __init__(self, name, fck, v=0.2, p=2400, fr=None):
        Material.__init__(self, name=name)

        de = 0.0001
        fcm = fck + 8
        Ecm = 22 * 10**3 * (fcm / 10.)**0.3
        ec1 = min(0.7 * fcm**0.31, 2.8) * 0.001
        ecu1 = 0.0035 if fck < 50 else (2.8 + 27 * ((98 - fcm) / 100.)**4) * 0.001

        k = 1.05 * Ecm * ec1 / fcm
        e = [i * de for i in range(int(ecu1 / de) + 1)]
        ec = [ei - e[1] for ei in e[1:]]
        fctm = 0.3 * fck**(2. / 3.) if fck <= 50 else 2.12 * log(1 + fcm / 10.)
        f = [10**6 * fcm * (k * (ei / ec1) - (ei / ec1)**2) / (1. + (k - 2) * (ei / ec1)) for ei in e]

        E = f[1] / e[1]
        ft = [1., 0.]
        et = [0., 0.001]

        if not fr:
            fr = [1.16, fctm / fcm]

        self.__name__ = 'Concrete'
        self.name = name
        self.fck = fck * 10.**6
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = {'f': ft, 'e': et}
        self.compression = {'f': f[1:], 'e': ec}
        self.fratios = fr
        self.attr_list.extend(['fck', 'fratios', 'E', 'v', 'G', 'p', 'tension', 'compression'])


class ConcreteSmearedCrack(Material):
    """Elastic and plastic, cracking concrete material.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus E [Pa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].
    fc : list
        Plastic stress data in compression [Pa].
    ec : list
        Plastic strain data in compression [-].
    ft : list
        Plastic stress data in tension [-].
    et : list
        Plastic strain data in tension [-].
    fr : list
        Failure ratios.

    """

    def __init__(self, name, E, v, p, fc, ec, ft, et, fr=[1.16, 0.0836]):
        Material.__init__(self, name=name)

        self.__name__ = 'ConcreteSmearedCrack'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = {'f': ft, 'e': et}
        self.compression = {'f': fc, 'e': ec}
        self.fratios = fr
        self.attr_list.extend(['E', 'v', 'G', 'p', 'tension', 'compression', 'fratios'])


class ConcreteDamagedPlasticity(Material):
    """Damaged plasticity isotropic and homogeneous material.

    Parameters
    ----------
    name : str
        Material name.
    E : float
        Young's modulus E [Pa].
    v : float
        Poisson's ratio v [-].
    p : float
        Density [kg/m3].
    damage : list
        Damage parameters.
    hardening : list
        Compression hardening parameters.
    stiffening : list
        Tension stiffening parameters.

    """

    def __init__(self, name, E, v, p, damage, hardening, stiffening):
        Material.__init__(self, name=name)

        self.__name__ = 'ConcreteDamagedPlasticity'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.damage = damage
        self.hardening = hardening
        self.stiffening = stiffening
        self.attr_list.extend(['E', 'v', 'G', 'p', 'damage', 'hardening', 'stiffening'])


# ==============================================================================
# thermal
# ==============================================================================

class ThermalMaterial(Material):
    """Class for thermal material properties.

    Parameters
    ----------
    name : str
        Material name.
    conductivity : list
        Pairs of conductivity and temperature values.
    p : list
        Pairs of density and temperature values.
    sheat : list
        Pairs of specific heat and temperature values.

    """

    def __init__(self, name, conductivity, p, sheat):
        Material.__init__(self, name=name)

        self.__name__ = 'ThermalMaterial'
        self.name = name
        self.conductivity = conductivity
        self.p = p
        self.sheat = sheat
        self.attr_list.extend(['p', 'conductivity', 'sheat'])
