********************************************************************************
Elements
********************************************************************************


This page shows how different types of **Element** objects are added and edited with the **Structure** object, here the example **Structure** object is given as ``mdl``. The **Element** objects represent linear, surface and solid finite elements connecting different nodes of the structure.

.. contents::


===============
Adding elements
===============

**Element** objects are added to the **Structure** object with the ``.add_element()`` and ``.add_elements()`` methods, by giving the list(s) of nodes that the element(s) connect to, as well as the element type as a string. The **Element** objects are added to the ``.elements`` dictionary, from the classes found in module **compas_fea.structure.elements**, where the class names match the string entered for the element type ``type``. The element types include, amongst others, 1D elements: **SpringElement**, **BeamElement**, **TrussElement**, 2D elements: **ShellElement**, **MembraneElement**, and 3D elements: **PentahedronElement**, **TetrahedronElement**, **HexahedronElement**. As with nodes, the elements will be added with integer keys numbered sequentially starting from 0. **Note**: currently no more than one element can exist for the same nodes, i.e. no overlapping elements are allowed. If you use ``.add_element()`` and an element already exists there, nothing else will be added.

.. code-block:: python

    mdl.add_elements(elements=[[0, 4], [1, 4], [2, 4], [3, 4]], type='BeamElement')

    mdl.add_element(nodes=[0, 1, 4], type='ShellElement')


================
Viewing elements
================

The **Element** objects can be viewed through their integer key to get their attributes (``.__name__``, ``.axes``, ``.nodes``, ``.number``, ``.acoustic``, ``.thermal``).

.. code-block:: python

    >>> mdl.elements[3].nodes
    [3, 4]

    >>> mdl.elements[3].__name__
   'BeamElement'

    >>> mdl.elements[3].acoustic
    False


=============
Element index
=============

A geometric key to integer key index dictionary is accessed through ``.element_index``, where the geometric key is taken as the element centroid and the key is the number of the element. The ``.element_index`` dictionary is similar in function to the ``.node_index`` dictionary, and is useful for checking if an element exists (see methods below).

.. code-block:: python

    >>> mdl.element_index
    {'-2.500,-2.500,2.500': 0, '2.500,-2.500,2.500': 1, '2.500,2.500,2.500': 2, '-2.500,2.500,2.500':  3}


=======
Methods
=======

It can be checked if an element is already present in the **Structure** object (via ``.element_index``), by a query with the method ``.check_element_exists()`` and giving either the list of ``nodes`` the element would be connected to, or the location ``xyz`` of where its centroid would be. As the check is based on the centroid of the element, it does not matter the order that the nodes are given in the list ``nodes``. If an element exists, the method will return the integer key, if not, ``None`` will be returned.

.. code-block:: python

    >>> mdl.check_element_exists([1, 4])
    1

    >>> mdl.check_element_exists([1, 2, 3])
    None

    >>> mdl.check_element_exists(xyz=[0, 10, 5])
    3


The number of elements in the **Structure** can be returned with method ``.element_count()``, which essentially takes the length of ``structure.elements``.

.. code-block:: python

    >>> mdl.element_count()
    5

An element centroid can be determined by the method ``.element_centroid()``.

.. code-block:: python

    >>> mdl.element_centroid(element=3)
    (-2.5, 2.5, 2.5)


====
Axes
====

Giving a dictionary for the argument ``axes`` when adding the element will store ``{'ex': [], 'ey': [], 'ez': []}`` in the **Element** object's ``.axes`` attribute. The ``'ex'``, ``'ey'`` and ``'ez'`` lists are the element's local `x`, `y` and `z` axes, and are used for example, when orientating cross-sections, using anisotropic materials, or for aligning rebar in concrete shells. If no ``axes`` data are given, it is left up to the finite element solver to determine default local axes values. This default alignment, if supported by the software, is often based on the global axes of the model, thus it is important to understand if these defaults are suitable, especially for an element geometry that does not align well with the global `x`, `y`, `z` directions. To add the local axes for a line element such as a beam, the ``'ex'`` axis represents the cross-section's major axis, ``'ey'`` the cross-section's minor axis, and ``'ez'`` the axis along the element. For surface elements, the ``'ex'`` and ``'ey'`` axes represent the in-plane local axes, with ``'ez'`` then representing the positive normal vector. The CAD functions (described in the CAD topic) that add elements to the **Structure** from geometry in the workspace, will automate some of these axis definitions.

.. code-block:: python

    mdl.add_element(nodes=[0, 1, 4], type='ShellElement', axes={'ex': [1, 1, 0], 'ey': [-1, 1, 0], 'ez': [0, 0, 1]})


========
Elements
========

-----------
1D elements
-----------

One dimensional elements such as truss and beam elements are currently first order (linear) defined by two nodes, which are the start (**n1**) and end (**n2**) points of a straight line. An internal node is currently not supported for second order (parabolic) elements. For the modelling of a curved shaped beam, use many straight segments. The single integration point (**ip1**) is at the midpoint of the line element.

.. image:: /_images/truss-element.png
   :scale: 50 %

-----------
2D elements
-----------

Two dimensional elements such as membrane and shell elements are currently first order (linear) defined by either three (**n1**, **n2**, **n3**) or four (**n1**, **n2**, **n3**, **n4**) nodes. These nodes are the corners of straight-sided elements, intermediate edge nodes are currently not supported for second order (parabolic) elements. For modelling a curved edge, use many straight segments. There are three or four internal integration points (**ip1** through to **ip3** or **ip4**).

.. image:: /_images/shell-element.png
   :scale: 50 %

-----------
3D elements
-----------

Three dimensional solid elements are also currently first order (linear), they are defined by four nodes (**TetrahedronElement** with four sides **S1** to **S4**), six nodes (**PentahedronElement** with five sides **S1** to **S5**) or eight nodes (**HexahedronElement** with six sides **S1** to **S6**). The nodes are the corners of flat-faced elements and should be added in the order shown below. Intermediate edge nodes are currently not supported for second order (parabolic) elements. For a curved edge/face, use many straight segments/faces for modelling. There is one internal integration point for a **TetrahedronElement** (**ip1**). two for a **PentahedronElement** (**ip1** and **ip2**) and eight for a **HexahedronElement** (**ip1** to **ip8**).

.. image:: /_images/solid-element.png
   :scale: 50 %
