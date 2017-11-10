********************************************************************************
Nodes
********************************************************************************


This page shows how nodes are added and inspected within the **Structure** object, here given as object with handle ``mdl``.

.. .. contents::


============
Adding nodes
============

Nodes can be added manually at prescribed spatial co-ordinates with the ``add_node()`` and ``add_nodes()`` methods, where ``xyz`` is a list of co-ordinates for a single node, and ``nodes`` a list of lists for multiple nodes.

.. code-block:: python

   mdl.add_node(xyz=[-5, -5, 0])

   mdl.add_nodes(nodes=[[5, -5, 0], [5, 5, 0], [-5, 5, 0], [0, 0, 5]])


=============
Viewing nodes
=============

The nodes data are stored in the ``.nodes`` dictionary, and are added with integer keys numbered sequentially starting from 0 (Python based). The dictionary of data for each node can accessed the same as any standard Python dictionary.

.. code-block:: python

   >>> mdl.nodes[3]
   {'x': -5.0, 'y': 5.0, 'z': 0.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}


=============
Editing nodes
=============

To edit the data of a node, use the method ``edit_node()``, this will both change the data of the node, and update the ``.node_index`` dictionary.

.. code-block:: python

  >>> mdl.nodes[1]
  {'x': 5.0, 'y': -5.0, 'z': 0.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}

  >>> mdl.edit_node(key=1, attr_dic={'x': 0})

  >>> mdl.nodes[1]
  {'x': 0, 'y': -5.0, 'z': 0.0, 'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1]}


=======
Methods
=======

The co-ordinates and number of nodes may be evaluated with the ``node_xyz()`` and ``node_count()`` methods:

.. code-block:: python

   >>> mdl.node_xyz(3)
   [-5.0, 5.0, 0.0]

.. code-block:: python

   >>> mdl.node_count()
   5

The simple bounding box made by the **Structure** can be found by calling the ``node_bounds()`` method. This will return three lists, containing the minimum and maximum `x`, `y` and `z` co-ordinates of the nodes in ``.nodes``.

.. code-block:: python

    >>> mdl.node_bounds()
    ([-5.0, 5.0], [-5.0, 5.0], [0.0, 5.0])

It can be checked if a node is present in the **Structure** object by a query with the method ``check_node_exists()`` and giving the list of node co-ordinates. If a node exists, the method will return the integer key, if not, ``None`` will be returned.

.. code-block:: python

   >>> mdl.check_node_exists([5, 5, 0])
   2

   >>> mdl.check_node_exists([5, 5, -1])
   None

**Note**: no more than one node can exist for the same co-ordinates, i.e. no overlapping nodes are allowed.


==========
Node index
==========

The **Structure** object's node index is a geometric key to integer key dictionary accessed through ``.node_index``. The geometric key is the string representation of the node's co-ordinates to a prescribed (default 3) float precision, while the integer key is the node's number.

.. code-block:: python

   >>> mdl.node_index
   {'-5.000,-5.000,0.000': 0, '5.000,-5.000,0.000': 1, '5.000,5.000,0.000': 2, '-5.000,5.000,0.000': 3}
