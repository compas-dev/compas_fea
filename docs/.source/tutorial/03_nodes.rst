********************************************************************************
Nodes
********************************************************************************

This page shows how nodes are added, viewed and edited within the **Structure** object, here given as object with handle ``mdl``. Node data is fundamental to the **Structure**, and is stored in the ``.nodes`` attribute as a dictionary of **Node** objects.

============
Adding nodes
============

Nodes can be added manually at prescribed spatial co-ordinates with the ``.add_node()`` and ``.add_nodes()`` methods, where ``xyz`` is given as a list of co-ordinates for a single node with ``.add_node()``, and for ``nodes`` as a list of lists for multiple node co-ordinates when using ``.add_nodes()``. If integer values for co-ordinates are given, they are converted to floats before adding to the **Structure** object. A ``mass`` can be added also, which is needed for some specific **compas_fea** functionality.

.. code-block:: python

    mdl.add_node(xyz=[-5, -5, 0])  # add a single node at x=-5, y=-5, z=0

    mdl.add_nodes(nodes=[[5, -5, 0], [5, 5, 0], [-5, 5, 0], [0, 0, 5]])  # add four nodes at one time


=============
Viewing nodes
=============

The nodes data are **Node** objects stored in the ``.nodes`` dictionary, and are added with integer keys numbered sequentially starting from 0 (Python based). The data summary for each node can be viewed by printing the **Node** to the terminal.

.. code-block:: python

    >>> print(mdl.nodes[3])  # print a summary of node number 3

    compas_fea Node object
    ----------------------
    key   : 3
    x     : -5.0
    y     : 5.0
    z     : 0.0
    ex    : [1, 0, 0]
    ey    : [0, 1, 0]
    ez    : [0, 0, 1]
    mass  : 0

Individually, all of the **Node** attributes are accessible for inspection.

.. code-block:: python

  >>> mdl.nodes[3]  # node number 3
  Node(3)

  >>> mdl.nodes[3].key  # the key of node number 3
  3

  >>> mdl.nodes[3].x  # the x coordinate of node number 3
  -5.0

  >>> mdl.nodes[3].ex  # the local axis of node number 3
  [1, 0, 0]


=============
Editing nodes
=============

To edit the data of a node use the ``.edit_node()`` method, which will change both the data of the **Node** and update the ``.node_index`` dictionary (explained later) if the co-ordinates were changed during editing.

.. code-block:: python

   >>> print(mdl.nodes[3].x, mdl.nodes[3].z)  # print the x and z coordinates of node number 3
   -5.0 0.0

   >>> mdl.edit_node(key=3, attr_dict={'x': 0.0, 'z': 4.0})  # update x and z values

   >>> print(mdl.nodes[3].x, mdl.nodes[3].z)  # print the new x and z coordinates
   0.0 4.0


=======
Methods
=======

The co-ordinates of a given node or many nodes, and the total number of nodes in the **Structure**, may be evaluated with the ``.node_xyz()``, ``.nodes_xyz()`` and ``.node_count()`` methods:

.. code-block:: python

   >>> mdl.node_xyz(node=3)  # fetch the coordinates of node number 3
   [-5.0, 5.0, 0.0]

.. code-block:: python

   >>> mdl.nodes_xyz(nodes=[3, 4])  # fetch the coordinates of nodes 3 and 4
   [[-5.0, 5.0, 0.0], [5.0, 0.0, 2.0]]

If ``nodes`` is not given for ``.nodes_xyz()``, then all of the node coordinates will be returned.

.. code-block:: python

   >>> mdl.node_count()  # get the count of nodes in the structure
   5

The simple bounding box made by the **Structure** can be found by calling the ``.node_bounds()`` method. This will return three lists, containing the minimum and maximum `x`, `y` and `z` co-ordinates of the node coordinates in ``.nodes``.

.. code-block:: python

    >>> mdl.node_bounds()  # return [xmin, xmax], [ymin, ymax], [zmin, zmax]
    ([-5.0, 5.0], [-5.0, 5.0], [0.0, 5.0])

It can be checked if a node is already present in the **Structure** object by a query with the method ``.check_node_exists()`` and with a list of test node co-ordinates. If a node exists at those coordinates, then the method will return the integer key, if not, ``None`` will be returned. Integer values that are given for co-ordinates will be converted to floats during this check.

.. code-block:: python

   >>> mdl.check_node_exists([5, 5, 0])  # does a node exist at x=5, y=5, z=0
   2

   >>> mdl.check_node_exists([5, 5, -1])  # does a node exist at x=5, y=5, z=-1
   None

**Note**: no more than one node can exist for the same co-ordinates, i.e. no overlapping nodes are allowed, this ensures a unique entry in the node index dictionary (see below) and is currently important for many operations in **compas_fea**.


==========
Node index
==========

The **Structure** object's node index is a geometric key to integer key dictionary accessed through ``.node_index``. The geometric key is the string representation of the node's co-ordinates to a prescribed (default 3) float precision, while the value that is returned for this geometric key is the node's number. The node index can be used to quickly see what node number corresponds to a nodal spatial location. **Note**: the ``.node_index`` should never be edited manually.

.. code-block:: python

   >>> mdl.node_index  # show the current node index dictionary
   {'-5.000,-5.000,0.000': 0, '5.000,-5.000,0.000': 1, '5.000,5.000,0.000': 2, '-5.000,5.000,0.000': 3}
