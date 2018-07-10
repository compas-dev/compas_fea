
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Load',
    'PrestressLoad',
    'PointLoad',
    'PointLoads',
    'LineLoad',
    'AreaLoad',
    'GravityLoad',
    'ThermalLoad',
    'TributaryLoad',
    'HarmonicPointLoad',
    'HarmonicPressureLoad'
]


class Load(object):

    """ Initialises base Load object.

    Parameters
    ----------
    name : str
        Name of the Load object.
    axes : str
        Load applied via 'local' or 'global' axes.
    components : dict
        Load components.
    nodes : str, list
        Node set or node keys the load is applied to.
    elements : str, list
        Element set or element keys the load is applied to.

    Returns
    -------
    None

    """

    def __init__(self, name, axes='global', components={}, nodes=[], elements=[]):

        self.__name__ = 'LoadObject'
        self.name = name
        self.axes = axes
        self.components = components
        self.nodes = nodes
        self.elements = elements
        self.attr_list = ['name', 'axes', 'components', 'nodes', 'elements']

    def __str__(self):

        print('compas_fea {0} object'.format(self.__name__))
        print('-' * (len(self.__name__) + 10))

        for attr in self.attr_list:
            print('{0:<10} : {1}'.format(attr, getattr(self, attr)))

        return ''


class PrestressLoad(Load):

    """ Pre-stress [units: N/m2] applied to element(s).

    Parameters
    ----------
    name : str
        Name of the PrestressLoad object.
    elements : str, list
        Element set or element keys the prestress is applied to.
    sxx : float
        Value of prestress for axial stress component sxx.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, sxx=0):
        Load.__init__(self, name=name, elements=elements, axes='local')

        self.__name__ = 'PrestressLoad'
        self.components = {'sxx': sxx}


class PointLoad(Load):

    """ Concentrated forces and moments [units:N, Nm] applied to node(s).

    Parameters
    ----------
    name : str
        Name of the PointLoad object.
    nodes : str, list
        Node set or node keys the load is applied to.
    x : float
        x component of force.
    y : float
        y component of force.
    z : float
        z component of force.
    xx : float
        xx component of moment.
    yy : float
        yy component of moment.
    zz : float
        zz component of moment.

    Returns
    -------
    None

    """

    def __init__(self, name, nodes, x=0, y=0, z=0, xx=0, yy=0, zz=0):
        Load.__init__(self, name=name, nodes=nodes, axes='global')

        self.__name__ = 'PointLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}


class PointLoads(Load):

    """ Different concentrated forces and moments [units:N, Nm] applied to different nodes.

    Parameters
    ----------
    name : str
        Name of the PointLoads object.
    components : dict
        Node key : components dictionary data.

    Returns
    -------
    None

    """

    def __init__(self, name, components):
        Load.__init__(self, name=name, components=components, axes='global')

        self.__name__ = 'PointLoads'


class LineLoad(Load):

    """ Distributed line forces and moments [units:N/m or Nm/m] applied to element(s).

    Parameters
    ----------
    name : str
        Name of the LineLoad object.
    elements : str, list
        Element set or element keys the load is applied to.
    x : float
        x component of force / length.
    y : float
        y component of force / length.
    z : float
        z component of force / length.
    xx : float
        xx component of moment / length.
    yy : float
        yy component of moment / length.
    zz : float
        zz component of moment / length.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, x=0, y=0, z=0, xx=0, yy=0, zz=0, axes='local'):
        Load.__init__(self, name=name, elements=elements, axes=axes)

        self.__name__ = 'LineLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}


class AreaLoad(Load):

    """ Distributed area force [units:N/m2] applied to element(s).

    Parameters
    ----------
    name : str
        Name of the AreaLoad object.
    elements : str, list
        Elements set or elements the load is applied to.
    x : float
        x component of area load.
    y : float
        y component of area load.
    z : float
        z component of area load.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, x=0, y=0, z=0, axes='local'):
        Load.__init__(self, name=name, elements=elements, axes=axes)

        self.__name__ = 'AreaLoad'
        self.components = {'x': x, 'y': y, 'z': z}


class GravityLoad(Load):

    """ Gravity load [units:N/m3] applied to element(s).

    Parameters
    ----------
    name : str
        Name of the GravityLoad object.
    elements : str, list
        Element set or element keys the load is applied to.
    g : float
        Value of gravitational acceleration.
    x : float
        Factor to apply to x direction.
    y : float
        Factor to apply to y direction.
    z : float
        Factor to apply to z direction.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, g=-9.81, x=0., y=0., z=1.):
        Load.__init__(self, name=name, elements=elements, axes='global')

        self.__name__ = 'GravityLoad'
        self.attr_list.append('g')
        self.g = g
        self.components = {'x': x, 'y': y, 'z': z}


class ThermalLoad(object):

    """ Thermal load.

    Parameters
    ----------
    name : str
        Name of the ThermalLoad object.
    elements : str, list
        Element set or element keys the load is applied to.
    temperature : float
        Temperature to apply to elements.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, temperature):

        self.__name__ = 'ThermalLoad'
        self.name = name
        self.elements = elements
        self.temperature = temperature


class TributaryLoad(Load):

    """ Tributary area loads applied to nodes.

    Parameters
    ----------
    structure : obj
        Structure class.
    name : str
        Name of the TributaryLoad object.
    mesh : str
        Tributary Mesh datastructure.
    x : float
        x component of area load.
    y : float
        y component of area load.
    z : float
        z component of area load.
    axes : str
        TributaryLoad applied via 'local' or 'global' axes.

    Returns
    -------
    None

    Notes
    -----
    - The load components are loads per unit area [N/m2].
    - Currently only supports 'global' axis.

    """

    def __init__(self, structure, name, mesh, x=0, y=0, z=0, axes='global'):
        Load.__init__(self, name=name, axes=axes)

        self.__name__ = 'TributaryLoad'
        self.attr_list.append('mesh')
        self.nodes = []

        for key in list(mesh.vertices()):
            node = structure.check_node_exists(mesh.vertex_coordinates(key))
            if node is not None:
                A = mesh.vertex_area(key)
                self.nodes.append(node)
                self.components[node] = {'x': x * A, 'y': y * A, 'z': z * A}


class HarmonicPointLoad(Load):

    """ Harmonic concentrated forces and moments [units:N, Nm] applied to node(s).

    Parameters
    ----------
    name : str
        Name of the HarmonicPointLoad object.
    nodes : str, list
        Node set or node keys the load is applied to.
    x : float
        x component of force.
    y : float
        y component of force.
    z : float
        z component of force.
    xx : float
        xx component of moment.
    yy : float
        yy component of moment.
    zz : float
        zz component of moment.

    Returns
    -------
    None

    """

    def __init__(self, name, nodes, x=0, y=0, z=0, xx=0, yy=0, zz=0):
        Load.__init__(self, name=name, nodes=nodes, axes='global')

        self.__name__ = 'HarmonicPointLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}


class HarmonicPressureLoad(Load):

    """ Harmonic pressure loads [units:N/m2] applied to element(s).

    Parameters
    ----------
    name : str
        Name of the HarmonicPressureLoad object.
    elements : str, list
        Elements set or element keys the load is applied to.
    pressure : float
        Normal acting pressure to be applied to the elements.
    phase : float
        Phase angle in radians.

    Returns
    -------
    None

    """

    def __init__(self, name, elements, pressure=0, phase=None):
        Load.__init__(self, name=name, elements=elements, axes='global')

        self.__name__ = 'HarmonicPressureLoad'
        self.components = {'pressure': pressure, 'phase': phase}
