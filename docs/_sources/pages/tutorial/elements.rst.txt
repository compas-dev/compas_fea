********************************************************************************
Elements
********************************************************************************


This page shows how **Element** objects are added and inspected with the **Structure** object, here given as ``mdl``.

.. contents::


===============
Adding elements
===============

**Element** objects are added to the **Structure** object with the ``add_element()`` method, by giving the list of nodes that the element connects to and the element type as a string. The **Element** objects are added to the ``.elements`` dictionary, from the classes found in module **compas_fea.structure.elements**, where the class names match the string entered for ``type``. The element types include, amongst others, 1D elements: **BeamElement**, **TrussElement**, 2D elements: **ShellElement**, **MembraneElement**, and 3D elements: **PentahedronElement**, **TetrahedronElement**, **HexahedronElement**. As with nodes, the elements will be added with integer keys numbered sequentially starting from 0 (Python based).

.. code-block:: python

   for uv in [[0, 4], [1, 4], [2, 4], [3, 4]]:
       mdl.add_element(nodes=uv, type='BeamElement')

   mdl.add_element(nodes=[0, 1, 4], type='ShellElement')


==================
Accessing elements
==================

The **Element** objects can be accessed through their integer key to get their attributes.

.. code-block:: python

   >>> mdl.elements[3].nodes
   [3, 4]

The number of elements in the **Structure** can be returned with ``element_count()`` and an element centroid determined by the method ``element_centroid()``.

.. code-block:: python

   >>> mdl.element_count()
   5

.. code-block:: python

   >>> mdl.element_centroid(element=3)
   (-2.5, 2.5, 2.5)


=============
Element index
=============

A geometric key to integer key index dictionary is accessed through ``element_index``, where the geometric key is taken as the element centroid as above.

.. code-block:: python

   >>> mdl.element_index
   {'-2.500,-2.500,2.500': 0,
    '2.500,-2.500,2.500':  1,
    '2.500,2.500,2.500':   2,
    '-2.500,2.500,2.500':  3,
    '0.000,-3.333,1.667':  4}

It can be checked if an element is already present in the **Structure** object by a query with the method ``check_element_exists()`` by giving the list of nodes the element would be connected to. As the check is based on the centroid of the element, it does not matter the order that the nodes are given in the list. **Note**: no more than one element can exist for the same nodes, i.e. no overlapping elements are allowed. If an element exists, the method will return the integer key, if not, ``None`` will be returned.

.. code-block:: python

   >>> mdl.check_element_exists([1, 4])
   1

   >>> mdl.check_element_exists([1, 2, 3])
   None


====
Axes
====

Giving a dictionary ``axes`` when adding the element can be used to store ``{'ex': [], 'ey': [], 'ez': []}`` in the **Element** object's ``.axes`` attribute. The ``'ex'``, ``'ey'`` and ``'ez'`` lists are the element's local `x`, `y` and `z` axes, and are used for example, when orientating cross-sections or for aligning rebar in concrete. If no ``axes`` data are given, it is left up to the finite element solver to determine default local axes values. This default alignment is often based on the global axes of the model, thus it is important to check these defaults are suitable, especially for element geometry that does not align well with the global `x`, `y`, `z` directions.


========
Elements
========

Additional information when defining elements s given below, with image reference from the Abaqus Documentation:

-----------
1D elements
-----------

One dimensional elements such as truss and beam elements are currently first order (linear), they are defined by two nodes, the start and end points of a straight line. An internal node is currently not supported for second order (parabolic) elements. For modelling a curved beam, use many straight segments. The single integration point is at the middle of the line element.

.. image:: /_images/truss-element.png
   :scale: 50 %

-----------
2D elements
-----------

Two dimensional elements such as membrane and shell elements are currently first order (linear), they are defined by three or four nodes. These nodes are the corners of straight-sided elements, intermediate edge nodes are currently not supported for second order (parabolic) elements. For modelling a curved edge, use many straight segments. There are three or four internal integration points.

.. image:: /_images/shell-element.png
   :scale: 50 %

-----------
3D elements
-----------

Three dimensional solid elements are also currently first order (linear), they are defined by four nodes (**TetrahedronElement** with four sides), six nodes (**PentahedronElement** with five sides) or eight nodes (**HexahedronElement** with six sides). The nodes are the corners of flat-faced elements and should be added in the order shown below. Intermediate edge nodes are currently not supported for second order (parabolic) elements. For a curved edge/face, use many straight segments/faces for modelling. There is one internal integration point for a **TetrahedronElement**. two for a **PentahedronElement** and eight for a **HexahedronElement**.

.. image:: /_images/solid-element.png
   :scale: 50 %
