
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import centroid_points

from compas.utilities import geometric_key

from compas_fea.structure.element import *


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'ElementMixins',
]


func_dic = {
    'BeamElement':        BeamElement,
    'SpringElement':      SpringElement,
    'TrussElement':       TrussElement,
    'StrutElement':       StrutElement,
    'TieElement':         TieElement,
    'ShellElement':       ShellElement,
    'MembraneElement':    MembraneElement,
    'FaceElement':        FaceElement,
    'SolidElement':       SolidElement,
    'TetrahedronElement': TetrahedronElement,
    'PentahedronElement': PentahedronElement,
    'HexahedronElement':  HexahedronElement,
}


class ElementMixins(object):

    def add_element(self, nodes, type, thermal=False, axes={}):

        """ Adds an element to structure.elements with centroid geometric key.

        Parameters
        ----------
        nodes : list
            Nodes the element is connected to.
        type : str
            Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.
        thermal : bool
            Thermal properties on or off.
        axes : dic
            The local element axes 'ex', 'ey' and 'ez'.

        Returns
        -------
        int
            Key of the added or existing element.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        if len(nodes) == len(set(nodes)):

            ekey = self.check_element_exists(nodes)

            if ekey is None:
                ekey = self.element_count()
                element         = func_dic[type]()
                element.axes    = axes
                element.nodes   = nodes
                element.number  = ekey
                element.thermal = thermal
                self.elements[ekey] = element
                self.add_element_to_element_index(ekey, nodes)

            return ekey

        else:

            return None


    def add_elements(self, elements, type, thermal=False, axes={}):

        """ Adds multiple elements of the same type to structure.elements.

        Parameters
        ----------
        elements : list
            List of lists of the nodes the elements are connected to.
        type : str
            Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.
        thermal : bool
            Thermal properties on or off.
        axes : dic
            The local element axes 'ex', 'ey' and 'ez' for all elements.

        Returns
        -------
        list
            Keys of the added or existing elements.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        return [self.add_element(nodes=nodes, type=type, thermal=thermal, axes=axes)
                for nodes in elements]


    def add_element_to_element_index(self, key, nodes, virtual=False):

        """ Adds the element to the element_index dictionary.

        Parameters
        ----------
        key : int
            Prescribed element key.
        nodes : list
            Node numbers the element is connected to.
        virtual: bool
            If true, adds element to the virtual_element_index dictionary.

        Returns
        -------
        None

        """

        centroid = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(centroid, '{0}f'.format(self.tol))
        if virtual:
            self.virtual_element_index[gkey] = key
        else:
            self.element_index[gkey] = key


    def check_element_exists(self, nodes, xyz=None, virtual=False):

        """ Check if an element already exists based on the nodes it connects to or its centroid.

        Parameters
        ----------
        nodes : list
            Node numbers the element is connected to.
        xyz : list
            Direct co-ordinates of the element centroid to check.
        virtual: bool
            Is the element to be checked a virtual element.

        Returns
        -------
        int
            The element index if the element already exists, None if not.

        Notes
        -----
        - Geometric key check is made according to self.tol [m] tolerance.

        """

        if not xyz:
            xyz = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        if virtual:
            return self.virtual_element_index.get(gkey, None)
        else:
            return self.element_index.get(gkey, None)


    def edit_element(self):
        raise NotImplementedError


    def element_count(self):

        """ Return the number of elements in structure.elements.

        Parameters
        ----------
        virtual: bool
            If true, returns the number of vurtual elements.

        Returns
        -------
        int
            Number of elements stored in the Structure object.

        """

        return len(self.elements) + len(self.virtual_elements)


    def make_element_index_dic(self):

        """ Makes an element_index dictionary from existing structure.elements.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        for key, element in self.elements.items():
            self.add_element_to_element_index(key=key, nodes=element.nodes)


    def element_centroid(self, element):

        """ Return the centroid of an element.

        Parameters
        ----------
        element : int
            Number of the element.

        Returns
        -------
        list
            Co-ordinates of the element centroid.

        """

        nodes = self.elements[element].nodes
        return centroid_points([self.node_xyz(node) for node in nodes])

    def add_nodal_element(self, node, type, virtual_node=False):

        """ Adds a nodal element to structure.elements with the possibility of
        adding a coincident virtual node. Virtual nodes are added to a node
        set called 'virtual_nodes'.

        Parameters
        ----------
        node : int
            Node number the element is connected to.
        type : str
            Element type: 'SpringElement'.
        virtual_node : bool
            Create a virtual node or not.

        Returns
        -------
        int
            Key of the added element.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        if virtual_node:
            xyz = self.node_xyz(node)
            key = self.virtual_nodes.setdefault(node, self.node_count())
            self.nodes[key] = {'x': xyz[0], 'y': xyz[1], 'z': xyz[2],
                               'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1], 'virtual': True}
            if 'virtual_nodes' in self.sets:
                self.sets['virtual_nodes']['selection'].append(key)
            else:
                self.sets['virtual_nodes'] = {'type': 'node', 'selection': [key], 'explode': False}
            nodes = [node, key]
        else:
            nodes = [node]

        func_dic = {
            'SpringElement': SpringElement,
        }

        ekey = self.element_count()
        element = func_dic[type]()
        element.nodes = nodes
        element.number = ekey
        self.elements[ekey] = element
        return ekey

    def add_virtual_element(self, nodes, type, thermal=False, axes={}):

        """ Adds a virtual element to structure.elements. Virtual elements are
        added to an element set called 'virtual_elements'.

        Parameters
        ----------
        nodes : list
            Nodes the element is connected to.
        type : str
            Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.

        Returns
        -------
        int
            Key of the added virtual element.

        Notes
        -----
        - Virtual elements are numbered sequentially starting from 0.

        """

        ekey = self.check_element_exists(nodes, virtual=True)
        if ekey is None:
            ekey = self.element_count()
            element = func_dic[type]()
            element.axes = axes
            element.nodes = nodes
            element.number = ekey
            element.thermal = thermal
            self.virtual_elements[ekey] = element
            self.add_element_to_element_index(ekey, nodes, virtual=True)

            if 'virtual_elements' in self.sets:
                self.sets['virtual_elements']['selection'].append(ekey)
            else:
                self.sets['virtual_elements'] = {'type': 'virtual_element', 'selection': [ekey], 'index': len(self.sets)}

        return ekey

    def assign_element_property(self, element_property):

        """ Assign the ElementProperties object name to associated Elements.

        Parameters
        ----------
        element_property : str
            Name of the ElementProperties object.

        Returns
        -------
        None

        """

        if element_property.elset:
            elements = self.sets[element_property.elset].selection
        else:
            elements = element_property.elements

        for element in elements:
            self.elements[element].element_property = element_property.name
