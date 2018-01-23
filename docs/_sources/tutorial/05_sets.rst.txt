********************************************************************************
Sets
********************************************************************************


This page shows how sets can be used to gather groups of nodes, elements and surfaces with the **Structure** object, here given as ``mdl``. Sets are a group of components that can be conveniently referred to by a string name, for use with other classes and methods, as well as accessing specific data of a model after an analysis.

.. contents::


===========
Adding sets
===========

A set is a group of nodes, elements or surfaces that are given a string name. By assigning a name to such a group, it is easier and more meaningful to refer to them in other classes, instead of giving (and keeping track of) a long list of node or element numbers. Sets are stored in a dictionary at ``.sets`` through the method ``.add_set()``, where the string key is the ``name`` of the set, the ``type`` of the set is the string ``'node'``, ``'element'``, ``'surface_node'`` or ``'surface_element'``, and the ``selection`` stores the nodes, elements and surfaces of interest. To add node or element sets, use ``.add_set()`` like the following:

.. code-block:: python

    mdl.add_set(name='nset_top', type='node', selection=[4])

    mdl.add_set(name='elset_shell', type='element', selection=[7, 8])

If the ``selection`` is not given as a list, but instead as a single integer (to represent one node for example), it will be converted into a list with one item. Sets may be viewed and edited at any time through their string name keys, and then by changing the dictionary as needed.

.. code-block:: python

    >>> mdl.sets['nset_top']['selection'] = 5

    >>> mdl.sets['nset_top']
    {'type': 'node', 'selection': [5]}

    >>> mdl.sets['elset_shell']
    {'type': 'element', 'selection': [7, 8]}

From the node and element geometry of the **Structure** object, a surface can be defined by one of two surface set types. The first is by using ``type='surface_node'`` when creating a set with the ``.add_set()`` method. This will describe a surface by the nodes given in the ``selection`` list. This surface type can be created like:

.. code-block:: python

    mdl.add_set(name='surf_set', type='surface_node', selection=[1, 3, 4, 5, 9, 10])

The second way to define a surface set is with ``type='surface_element'``, where instead of a list of nodes for ``selection``, a dictionary of element number keys and list of element string sides is given. So for example, to add sides 1 and 2 (``'S1'`` and ``'S2'``) of solid element 4, and the top side (``'SPOS'`` for top and ```SNEG``` for bottom) of shell element 7 as an element surface set use:

.. code-block:: python

    mdl.add_set(name='surf_set', type='surface_element', selection={4: ['S1', 'S2'], 7: ['SPOS']})
