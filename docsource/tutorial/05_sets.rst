********************************************************************************
Sets
********************************************************************************

This page shows how sets can be used to gather groups of nodes, elements and surfaces within the **Structure** object, here given as ``mdl``. A **Set** object is a group of components that can be conveniently referred to by a string name, for use with other classes and methods, and accessing specific data of a model after an analysis.

===========
Adding sets
===========

A set is a group of nodes, elements or surfaces that are given a string name. By assigning a name to such a group of components, it is easier and more meaningful to refer to them in other classes, instead of giving (and keeping track of) a long list of node or element numbers. A **Set** object is stored in the dictionary ``.sets`` through the method ``.add_set()``, where the string key is the ``name`` of the set, the ``type`` of the set is the string ``'node'``, ``'element'``, ``'surface_node'`` or ``'surface_element'``, and the ``selection`` stores the nodes, elements and surfaces of interest. To add node or element sets, use ``.add_set()`` as follows:

.. code-block:: python

    mdl.add_set(name='nset_top', type='node', selection=[4])  # add a note set 'nset_top'

    mdl.add_set(name='elset_shell', type='element', selection=[7, 8])  # add an element set 'elset_shell'

If the ``selection`` is not given as a list, but instead as a single integer (to represent one node for example), it will be converted into a list with one item. Sets may be viewed and edited at any time through their string name keys, and then by viewing or changing the object attributes as needed. Like all other objects, printing the **Set** will give a short summary.

.. code-block:: python

    >>> mdl.sets['nset_top']
    Set(nset_top)

    >>> print(mdl.sets['nset_top'])  # give a summary of set `nset_top

    compas_fea Set object
    ---------------------
    name      : nset_top
    type      : node
    selection : [4]
    index     : 1

    >>> print(mdl.sets['elset_shell'])  # give a summary of set `elset_shell

    compas_fea Set object
    ---------------------
    name      : elset_shell
    type      : element
    selection : [7, 8]
    index     : 3

    >>> mdl.sets['elset_shell'].selection.append(5)  # add an element to the element set

    >>> mdl.sets['elset_shell'].selection  # show updated selection
    [7, 8, 5]

From the node and element data of the **Structure** object, a surface can be defined by one of two surface set types. The first is by using ``type='surface_node'`` when creating a set with the ``.add_set()`` method. This will describe a surface by the nodes given in the ``selection`` list. This surface type can be created like:

.. code-block:: python

    mdl.add_set(name='surf_set', type='surface_node', selection=[1, 3, 4, 10])  # surface node set

The second way to define a surface set is with ``type='surface_element'``, where instead of a list of nodes for ``selection``, a dictionary of element number keys and list of element string sides is given. So for example, to add sides 1 and 2 (``'S1'`` and ``'S2'``) of solid element 4, and the top side (``'SPOS'`` for top and ```SNEG``` for bottom) of shell element 7 as an element surface set use the following. You can find which surface sides correspond to which, in the **Elements** topic.

.. code-block:: python

    mdl.add_set(name='surf_set', type='surface_element', selection={4: ['S1', 'S2'], 7: ['SPOS']})


