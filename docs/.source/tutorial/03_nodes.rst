********************************************************************************
Nodes
********************************************************************************

This page shows how nodes are added, viewed and edited within the **Structure** object, here given as object with handle ``mdl``. Node data is fundamental to the **Structure**, and is stored in the ``.nodes`` attribute as a dictionary of data.

============
Adding nodes
============

Nodes can be added manually at prescribed spatial co-ordinates with the ``.add_node()`` and ``.add_nodes()`` methods, where ``xyz`` is given as a list of co-ordinates for a single node in ``.add_node()``, and ``nodes`` as a list of lists for multiple node co-ordinates for ``.add_nodes()``. If integer values for co-ordinates are given, they are converted to floats before adding to the **Structure** object.

.. code-block:: python

    mdl.add_node(xyz=[-5, -5, 0])

    mdl.add_nodes(nodes=[[5, -5, 0], [5, 5, 0], [-5, 5, 0], [0, 0, 5]])


=============
Viewing nodes
=============

The nodes data are stored in the ``.nodes`` dictionary, and are added with integer keys numbered sequentially starting from 0 (Python based). The dictionary of data for each node can be accessed the same as any standard Python dictionary.

.. code-block:: python

    >>> mdl.nodes[3]
    {'x': -5.0, 'y': 5.0, 'z': 0.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}


=============
Editing nodes
=============

To edit the data of a node use the ``.edit_node()`` method, which will change both the data of the node and update the ``.node_index`` dictionary (explained later) if the co-ordinates were changed during editing.

.. code-block:: python

   >>> mdl.nodes[3]
   {'x': 5.0, 'y': -5.0, 'z': 0.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}

   >>> mdl.edit_node(key=3, attr_dic={'x': 0.0, 'z': 4.0})

   >>> mdl.nodes[3]
   {'x': 0.0, 'y': -5.0, 'z': 4.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}


=======
Methods
=======

The co-ordinates of a given node or many nodes, and the total number of nodes in the **Structure**, may be evaluated with the ``.node_xyz()``, ``.nodes_xyz()`` and ``.node_count()`` methods:

.. code-block:: python

   >>> mdl.node_xyz(node=3)
   [-5.0, 5.0, 0.0]

.. code-block:: python

   >>> mdl.nodes_xyz(nodes=[3, 4])
   [[-5.0, 5.0, 0.0], [5.0, 0.0, 2.0]]

If ``nodes`` is not given for ``.nodes_xyz()``, all nodes will be assumed.

.. code-block:: python

   >>> mdl.node_count()
   5

The simple bounding box made by the **Structure** can be found by calling the ``.node_bounds()`` method. This will return three lists, containing the minimum and maximum `x`, `y` and `z` co-ordinates of the nodes in ``.nodes``.

.. code-block:: python

    >>> mdl.node_bounds()
    ([-5.0, 5.0], [-5.0, 5.0], [0.0, 5.0])

It can be checked if a node is present in the **Structure** object by a query with the method ``.check_node_exists()`` and with the list of node co-ordinates. If a node exists, the method will return the integer key, if not, ``None`` will be returned. Integer values for co-ordinates will be converted to floats during this check.

.. code-block:: python

   >>> mdl.check_node_exists([5, 5, 0])
   2

   >>> mdl.check_node_exists([5, 5, -1])
   None

**Note**: no more than one node can exist for the same co-ordinates, i.e. no overlapping nodes are allowed, this ensures a unique entry in the node index dictionary (see below) and is currently important for many operations in **compas_fea**.


==========
Node index
==========

The **Structure** object's node index is a geometric key to integer key dictionary accessed through ``.node_index``. The geometric key is the string representation of the node's co-ordinates to a prescribed (default 3) float precision, while the integer key is the node's number. The node index can be used to quickly see what node number corresponds to a nodal spatial location.

.. code-block:: python

   >>> mdl.node_index
   {'-5.000,-5.000,0.000': 0, '5.000,-5.000,0.000': 1, '5.000,5.000,0.000': 2, '-5.000,5.000,0.000': 3}
