from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.structure import Node

from compas.utilities import geometric_key


# Author(s): Andrew Liew (github.com/andrewliew), Tomas Mendez Echenagucia (github.com/tmsmendez)


__all__ = [
    'NodeMixins',
]


class NodeMixins(object):

    def add_node(self, xyz, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1], mass=0, virtual=False):
        """ Adds a node to structure.nodes at co-ordinates xyz with local frame [ex, ey, ez].

        Parameters
        ----------
        xyz : list
            [x, y, z] co-ordinates of the node.
        ex : list
            Node's local x axis.
        ey : list
            Node's local y axis.
        ez : list
            Node's local z axis.
        mass : float
            Lumped mass at node.
        virtual: bool
            Is the node virtual.

        Returns
        -------
        int
            Key of the added or pre-existing node.

        Notes
        -----
        - Nodes are numbered sequentially starting from 0.

        """

        xyz = [float(i) for i in xyz]
        key = self.check_node_exists(xyz)

        if key is None:

            key = self.node_count()
            self.nodes[key] = Node(key=key, xyz=xyz, ex=ex, ey=ey, ez=ez, mass=mass)

            if virtual:
                self.add_node_to_node_index(key=key, xyz=xyz, virtual=True)
            else:
                self.add_node_to_node_index(key=key, xyz=xyz)

        return key

    def add_nodes(self, nodes, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1]):
        """ Adds a list of nodes to structure.nodes at given co-ordinates all with local frame [ex, ey, ez].

        Parameters
        ----------
        nodes : list
            [[x, y, z], ..] co-ordinates for each node.
        ex : list
            Nodes' local x axis.
        ey : list
            Nodes' local y axis.
        ez : list
            Nodes' local z axis.

        Returns
        -------
        list
            Keys of the added or pre-existing nodes.

        Notes
        -----
        - Nodes are numbered sequentially starting from 0.

        """

        return [self.add_node(xyz=node, ex=ex, ey=ey, ez=ez) for node in nodes]

    def add_node_to_node_index(self, key, xyz, virtual=False):
        """ Adds the node to the node_index dictionary.

        Parameters
        ----------
        key : int
            Prescribed node key.
        xyz : list
            [x, y, z] co-ordinates of the node.
        virtual: bool
            Is the node virtual or not.

        Returns
        -------
        None

        """

        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        if virtual:
            self.virtual_node_index[gkey] = key
        else:
            self.node_index[gkey] = key

    def check_node_exists(self, xyz):
        """ Check if a node already exists at given x, y, z co-ordinates.

        Parameters
        ----------
        xyz : list
            [x, y, z] co-ordinates of node to check.

        Returns
        -------
        int
            The node index if the node already exists, None if not.

        Notes
        -----
        - Geometric key check is made according to self.tol [m] tolerance.

        """

        xyz = [float(i) for i in xyz]
        return self.node_index.get(geometric_key(xyz, '{0}f'.format(self.tol)), None)

    def edit_node(self, key, attr_dict):
        """ Edit a node's data.

        Parameters
        ----------
        key : int
            Key of the node to edit.
        attr_dict : dict
            Attribute dictionary of data to edit.

        Returns
        -------
        None

        """

        gkey = geometric_key(self.node_xyz(key), '{0}f'.format(self.tol))
        del self.node_index[gkey]

        for attr, item in attr_dict.items():
            setattr(self.nodes[key], attr, item)

        self.add_node_to_node_index(key, self.node_xyz(key))

    def node_bounds(self):
        """ Return the bounds formed by the Structure's nodal co-ordinates.

        Parameters
        ----------
        None

        Returns
        -------
        list
            [xmin, xmax].
        list
            [ymin, ymax].
        list
            [zmin, zmax].

        """

        n = self.node_count()
        x = [0] * n
        y = [0] * n
        z = [0] * n

        for c, node in self.nodes.items():
            x[c] = node.x
            y[c] = node.y
            z[c] = node.z

        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)
        zmin, zmax = min(z), max(z)

        return [xmin, xmax], [ymin, ymax], [zmin, zmax]

    def node_count(self):
        """ Return the number of nodes in the Structure.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Number of nodes stored in the Structure object.

        """

        return len(self.nodes) + len(self.virtual_nodes)

    def node_xyz(self, node):
        """ Return the xyz co-ordinates of a node.

        Parameters
        ----------
        node : int
            Node number.

        Returns
        -------
        list
            [x, y, z] co-ordinates.

        """

        return [getattr(self.nodes[node], i) for i in 'xyz']

    def nodes_xyz(self, nodes=None):
        """ Return the xyz co-ordinates of given or all nodes.

        Parameters
        ----------
        nodes : list
            Node numbers, give None for all nodes.

        Returns
        -------
        list
            [[x, y, z] ...] co-ordinates.

        """

        if nodes is None:
            nodes = sorted(self.nodes, key=int)

        return [self.node_xyz(node=node) for node in nodes]
