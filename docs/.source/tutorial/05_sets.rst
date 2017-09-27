********************************************************************************
Sets
********************************************************************************


This page shows how sets can be used to gather groups of nodes and elements with the **Structure** object, here given as ``mdl``.

.. .. contents::


===========
Adding sets
===========

A set, is a group of nodes, elements or surfaces that are given a name. By assigning a name to such a group, it is easier and more meaningful to refer to them in other classes, instead of giving a longer list of numbers. Sets are stored in a dictionary at ``.sets`` through the method ``add_set()``, where the string key is the ``name`` of the set, the ``type`` of the set is the string ``'node'``, ``'element'``, ``'surface_node'`` or ``'surface_element'`` (the latter two are described in more detail later on this page), and the ``selection`` stores the nodes and elements of interest.

.. code-block:: python

   mdl.add_set(name='nset_top', type='node', selection=[4], explode=False)

   mdl.add_set(name='elset_shell', type='element', selection=[7, 8], explode=False)

.. code-block:: python

   >>> mdl.sets['nset_top']
   {'type': 'node', 'selection': [4], 'explode': False}

   >>> mdl.sets['elset_shell']
   {'type': 'element', 'selection': [7, 8], 'explode': False}


=========
Exploding
=========

The argument ``explode`` is a boolean that if ``True`` (default ``False``) will take all elements of that set, and make an individual set for each element in the selection. For example:

.. code-block:: python

   mdl.add_set(name='elset_exploded', type='element', selection=[4, 6], explode=True)

will additionally make two new element sets named ``'element_4'`` and ``'element_6'`` with ``selection=[4]`` and ``selection=[6]``. The utility of this is, the user can break up a larger set knowing that individual sets can now be referenced to, to individually assign a thickness, material, section or cross-section orientation to specific elements by their number.

.. code-block:: python

    >>> mdl.sets['element_4']
    {'type': 'element', 'selection': [4], 'explode': False}

    >>> mdl.sets['element_6']
    {'type': 'element', 'selection': [6], 'explode': False}

The same exploding method works for node sets:

.. code-block:: python

    >>> mdl.add_set(name='nset_exploded', type='node', selection=[1, 2], explode=True)

    >>> mdl.sets['node_1']
    {'type': 'node', 'selection': [1], 'explode': False}

    >>> mdl.sets['node_2']
    {'type': 'node', 'selection': [2], 'explode': False}


============
Surface sets
============

From the node and element geometry of the **Structure** object, a surface can be defined by one of two surface set types. The first is by using ``type='surface_node'`` when creating a set with the ``add_set()`` method, and describes a surface by the nodes it connects to in the ``selection`` list. This surface type can be created like:

.. code-block:: python

   mdl.add_set(name='surf_set', type='surface_node', selection=[1, 3, 4, 5, 9, 10])

The second way to define a surface set is with ``type='surface_element'``, where instead of a list of nodes for ``selection``, a dictionary of element number keys and list of element string sides is given. So for example, to add sides 1 and 2 of solid element 4, and the top side (``'SPOS'`` for top and ```SNEG``` for bottom) of shell element 7 as an element surface set use:

.. code-block:: python

   mdl.add_set(name='surf_set', type='surface_element', selection={4: ['S1', 'S2'], 7: ['SPOS']})

For both types, the ``explode`` argument can be kept as ``False``, as it currently has no meaning in a surface set definition.
