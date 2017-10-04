"""
compas_fea.structure.load : Load class.
Apply point loads and distributed loads to nodes and elements.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'Load',
    'PrestressLoad',
    'PointLoad',
    'LineLoad',
    'AreaLoad',
    'BodyLoad',
    'GravityLoad',
    'AcousticLoad',
    'TributaryLoad',
    'HarmonicPointLoad'
]


class Load(object):

    """ Initialises base Load object for use in finite element analysis.

    Parameters:
        name (str): Name of the Load object.
        axes (str): Load applied via 'local' or 'global' axes.
        components (dic): Load components.
        nodes (str, list): NSET or nodes the load is applied to.
        elements (str, list): ELSET or elements the load is applied to.

    Returns:
        None
    """

    def __init__(self, name, axes='global', components={}, nodes=[], elements=[]):
        self.name = name
        self.axes = axes
        self.components = components
        self.nodes = nodes
        self.elements = elements


class PrestressLoad(Load):

    """ Pre-stress [units: N/m2] applied to element(s).

    Parameters:
        name (str): Name of the PrestressLoad object.
        elements (str, list): ELSET or elements the prestress is applied to.
        prestress (float): Value of prestress.

    Returns:
        None
    """

    def __init__(self, name, elements, prestress):
        Load.__init__(self, name=name, elements=elements, axes='local')
        self.__name__ = 'PrestressLoad'
        self.components = {'prestress': prestress}


class PointLoad(Load):

    """ Concentrated forces and moments [units:N, Nm] applied to node(s).

    Parameters:
        name (str): Name of the PointLoad object.
        nodes (str, list): NSET or nodes the load is applied to.
        x (float): x component of force.
        y (float): y component of force.
        z (float): z component of force.
        xx (float): xx component of moment.
        yy (float): yy component of moment.
        zz (float): zz component of moment.

    Returns:
        None
    """

    def __init__(self, name, nodes, x=0, y=0, z=0, xx=0, yy=0, zz=0):
        Load.__init__(self, name=name, nodes=nodes, axes='global')
        self.__name__ = 'PointLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}


class LineLoad(Load):

    """ Distributed line forces and moments [units:N/m or Nm/m] applied to element(s).

    Parameters:
        name (str): Name of the LineLoad object.
        elements (str, list): ELSET or elements the load is applied to.
        x (float): x component of force / length.
        y (float): y component of force / length.
        z (float): z component of force / length.
        xx (float): xx component of moment / length.
        yy (float): yy component of moment / length.
        zz (float): zz component of moment / length.

    Returns:
        None
    """

    def __init__(self, name, elements, x=0, y=0, z=0, xx=0, yy=0, zz=0):
        Load.__init__(self, name=name, elements=elements, axes='local')
        self.__name__ = 'LineLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}


class AreaLoad(Load):

    """ Distributed area force [units:N/m2] applied to element(s).

    Parameters:
        name (str): Name of the AreaLoad object.
        elements (str, list): ELSET or elements the load is applied to.
        x (float): x component of pressure.
        y (float): y component of pressure.
        z (float): z component of pressure.

    Returns:
        None
    """

    def __init__(self, name, elements, x=0, y=0, z=0):
        Load.__init__(self, name=name, elements=elements, axes='local')
        self.__name__ = 'AreaLoad'
        self.components = {'x': x, 'y': y, 'z': z}


class BodyLoad(Load):

    """ Distributed body force [units:N/m3] applied to element(s).

    Parameters:
        name (str): Name of the BodyLoad object.
        elements (str, list): ELSET or elements the load is applied to.
        x (float): x component of body load.
        y (float): y component of body load.
        z (float): z component of body load.

    Returns:
        None
    """

    def __init__(self, name, elements, x=0, y=0, z=0):
        Load.__init__(self, name=name, elements=elements, axes='global')
        self.__name__ = 'BodyLoad'
        self.components = {'x': x, 'y': y, 'z': z}


class GravityLoad(Load):

    """ Gravity load [units:N/m3] applied to element(s).

    Parameters:
        name (str): Name of the GravityLoad object.
        elements (str, list): ELSET or elements the load is applied to.
        g (float): Value of gravitational acceleration.
        x (bool): Apply to x direction.
        y (bool): Apply to y direction.
        z (bool): Apply to z direction.

    Returns:
        None
    """

    def __init__(self, name, elements, g=-9.81, x=False, y=False, z=True):
        Load.__init__(self, name=name, elements=elements, axes='global')
        self.__name__ = 'GravityLoad'
        self.g = g
        self.components = {'x': x, 'y': y, 'z': z}


class AcousticLoad(Load):

    """ Acoustic load.

    Note:
        - Placeholder for an acoustic load.

    Parameters:
        name (str): Name of the AcousticLoad object.
        elements (str, list): ELSET or elements the load is applied to.
        axes (str): AcousticLoad applied via 'local' or 'global' axes.

    Returns:
        None
    """

    def __init__(self, name, elements, axes='global'):
        Load.__init__(self)
        self.__name__ = 'AcousticLoad'
        self.axes = axes
        self.name = name
        self.elements = elements


class TributaryLoad(Load):

    """ Tributary area pressure loads applied to nodes.

    Note:
        - The load components are loads per unit area [N/m2].

    Parameters:
        structure (obj): Structure class.
        name (str): Name of the TributaryLoad object.
        mesh (str): Tributary Mesh datastructure.
        x (float): x component of pressure.
        y (float): y component of pressure.
        z (float): z component of pressure.
        axes (str): TributaryLoad applied via 'local' or 'global' axes.

    Returns:
        None
    """

    def __init__(self, structure, name, mesh, x=0, y=0, z=0, axes='global'):
        Load.__init__(self, name=name, axes=axes)
        self.__name__ = 'TributaryLoad'
        self.nodes = []
        for key in list(mesh.vertices()):
            node = structure.check_node_exists(mesh.vertex_coordinates(key))
            if node is not None:
                A = mesh.vertex_area(key)
                self.nodes.append(node)
                self.components[node] = {'x': x * A, 'y': y * A, 'z': z * A}


class HarmonicPointLoad(Load):

    """ Harmonic concentrated forces and moments [units:N, Nm] applied to node(s).

    Parameters:
        name (str): Name of the PointLoad object.
        nodes (str, list): NSET or nodes the load is applied to.
        x (float): x component of force.
        y (float): y component of force.
        z (float): z component of force.
        xx (float): xx component of moment.
        yy (float): yy component of moment.
        zz (float): zz component of moment.

    Returns:
        None
    """

    def __init__(self, name, nodes, x=0, y=0, z=0, xx=0, yy=0, zz=0):
        Load.__init__(self, name=name, nodes=nodes, axes='global')
        self.__name__ = 'HarmonicPointLoad'
        self.components = {'x': x, 'y': y, 'z': z, 'xx': xx, 'yy': yy, 'zz': zz}
