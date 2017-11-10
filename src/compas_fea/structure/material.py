"""
compas_fea.structure.material : Material classes.
For creating and/or selecting linear and non-linear material model classes.
"""

from __future__ import absolute_import
from __future__ import print_function

from math import log


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'Concrete',
    'ConcreteSmearedCrack',
    'ConcreteDamagedPlasticity',
    'ElasticIsotropic',
    'ElasticOrthotropic',
    'ElasticPlastic',
    'ThermalMaterial',
    'Steel'
]


# ==============================================================================
# linear elastic
# ==============================================================================

class ElasticIsotropic(object):

    """ Elastic, isotropic and homogeneous material.

    Parameters:
        name (str): Material name.
        E (float, list): Young's modulus E.
        v (float, list): Poisson's ratio v.
        p (float, list): Density.
        tension (bool): Can take tension.
        compression (bool): Can take compression.

    Returns:
        None
    """

    def __init__(self, name, E, v, p, tension=True, compression=True):
        self.__name__ = 'ElasticIsotropic'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        self.tension = tension
        self.compression = compression


class ElasticOrthotropic(object):

    """ Elastic, orthotropic and homogeneous material.

    Note:
        - Class can be created but is currently not implemented.

    Parameters:
        name (str): Material name.
        Ex (float, list): Young's modulus Ex in x direction.
        Ey (float, list): Young's modulus Ey in y direction.
        Ez (float, list): Young's modulus Ez in z direction.
        vxy (float, list): Poisson's ratio vxy in x-y directions.
        vyz (float, list): Poisson's ratio vyz in y-z directions.
        vzx (float, list): Poisson's ratio vzx in z-x directions.
        Gxy (float, list): Shear modulus Gxy in x-y directions.
        Gyz (float, list): Shear modulus Gyz in y-z directions.
        Gzx (float, list): Shear modulus Gzx in z-x directions.
        p (float, list): Density.
        tension (bool): Can take tension.
        compression (bool): Can take compression.

    Returns:
        None
    """

    def __init__(self, name, Ex, Ey, Ez, vxy, vyz, vzx, Gxy, Gyz, Gzx, p, tension=True, compression=True):
        self.__name__ = 'ElasticOrthotropic'
        self.name = name
        self.E = {'Ex': Ex, 'Ey': Ey, 'Ez': Ez}
        self.v = {'vxy': vxy, 'vyz': vyz, 'vzx': vzx}
        self.G = {'Gxy': Gxy, 'Gyz': Gyz, 'Gzx': Gzx}
        self.p = p
        self.tension = tension
        self.compression = compression


# ==============================================================================
# non-linear general
# ==============================================================================

class ElasticPlastic(object):

    """ Elastic and plastic, isotropic and homogeneous material.

    Note:
        - Plastic stress--strain pairs applies to both compression and tension.

    Parameters:
        name (str): Material name.
        E (float, list): Young's modulus E.
        v (float, list): Poisson's ratio v.
        p (float, list): Density.
        f (list): Plastic stress data (positive tension values).
        e (list): Plastic strain data (positive tension values).

    Returns:
        None
    """

    def __init__(self, name, E, v, p, f, e):
        self.__name__ = 'ElasticPlastic'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        fc = [-i for i in f]
        ec = [-i for i in e]
        self.compression = {'f': fc, 'e': ec}
        self.tension = {'f': f, 'e': e}


# ==============================================================================
# non-linear metal
# ==============================================================================

class Steel(object):

    """ Construction steel with given yield stress.

    Parameters:
        name (str): Material name.
        fy (float): Yield stress [MPa].
        E (float): Young's modulus E.
        v (float): Poisson's ratio v.
        p (float): Density.
        type (str): 'elastic-plastic.

    Returns:
        None
    """

    def __init__(self, name, fy=355, E=210*10**9, v=0.3, p=7850, type='elastic-plastic'):
        self.__name__ = 'Steel'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.G = {'G': 0.5 * E / (1 + v)}
        self.p = p
        if type == 'elastic-plastic':
            f = [fy * 10**6]
            e = [0]
        fc = [-i for i in f]
        ec = [-i for i in e]
        self.compression = {'f': fc, 'e': ec}
        self.tension = {'f': f, 'e': e}


# ==============================================================================
# non-linear timber
# ==============================================================================


# ==============================================================================
# non-linear masonry
# ==============================================================================


# ==============================================================================
# non-linear concrete
# ==============================================================================

class Concrete(object):

    """ Elastic and plastic-cracking concrete material.

    Note:
        - The concrete model is based on Eurocode 2 up to fck=90 MPa.

    Parameters:
        name (str): Material name.
        fck (float): Characteristic (5%) 28 day cylinder strength MPa.
        v (float, list): Poisson's ratio v.
        p (float, list): Density.
        fr (list): Failure ratios.

    Returns:
        None
    """

    def __init__(self, name, fck, v=0.2, p=2400, fr=None):
        de = 0.0001
        fcm = fck + 8  # MPa
        Ecm = 22 * 10**3 * (fcm / 10.)**0.3  # MPa
        ec1 = min(0.7 * fcm**0.31, 2.8) * 0.001
        ecu1 = 0.0035 if fck < 50 else (2.8 + 27 * ((98 - fcm) / 100.)**4) * 0.001
        n = int(ecu1 / de)
        k = 1.05 * Ecm * ec1 / fcm
        e = [i * de for i in range(n + 1)]
        ec = [ei - e[1] for ei in e[1:]]
        fctm = 0.3 * fck**(2. / 3.) if fck <= 50 else 2.12 * log(1 + fcm / 10.)  # MPa
        f = [10**6 * fcm * (k * (ei / ec1) - (ei / ec1)**2) / (1. + (k - 2) * (ei / ec1)) for ei in e]
        E = f[1] / e[1]
        ft = [1., 0.]
        et = [0., 0.001]
        if not fr:
            fr = [1.16, fctm / fcm]

        self.__name__ = 'Concrete'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.p = p
        self.compression = {'f': f[1:], 'e': ec}
        self.tension = {'f': ft, 'e': et}
        self.fratios = fr


class ConcreteSmearedCrack(object):

    """ Elastic and plastic, cracking concrete material.

    Parameters:
        name (str): Material name.
        E (float, list): Young's modulus E.
        v (float, list): Poisson's ratio v.
        p (float, list): Density.
        fc (list): Plastic stress data in compression.
        ec (list): Plastic strain data in compression.
        ft (list): Plastic stress data in tension.
        et (list): Plastic strain data in tension.
        fr (list): Failure ratios.

    Returns:
        None
    """

    def __init__(self, name, E, v, p, fc, ec, ft, et, fr=[1.16, 0.0836]):
        self.__name__ = 'ConcreteSmearedCrack'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.p = p
        self.compression = {'f': fc, 'e': ec}
        self.tension = {'f': ft, 'e': et}
        self.fratios = fr


class ConcreteDamagedPlasticity(object):

    """ Damaged plasticity isotropic and homogeneous material.

    Parameters:
        name (str): Material name.
        E (float, list): Young's modulus E.
        v (float, list): Poisson's ratio v.
        p (float, list): Density.
        damage (list): Damage parameters.
        hardening (list): Compression hardening parameters.
        stiffening (list): Tension stiffening parameters.

    Returns:
        None
    """

    def __init__(self, name, E, v, p, damage, hardening, stiffening):
        self.__name__ = 'ConcreteDamagedPlasticity'
        self.name = name
        self.E = {'E': E}
        self.v = {'v': v}
        self.p = p
        self.damage = damage
        self.hardening = hardening
        self.stiffening = stiffening


# ==============================================================================
# thermal
# ==============================================================================

class ThermalMaterial(object):

    """ Class for thermal material properties.

    Parameters:
        name (str): Material name.
        conductivity (list): Pairs of conductivity and temperature values.
        p (list): Pairs of density and temperature values.
        sheat (list): Pairs of specific heat and temperature values.

    Returns:
        None
    """

    def __init__(self, name, conductivity, p, sheat):
        self.__name__ = 'ThermalMaterial'
        self.name = name
        self.conductivity = conductivity
        self.p = p
        self.sheat = sheat
