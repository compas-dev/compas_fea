********************************************************************************
Elements
********************************************************************************

This page shows how different types of **Element** objects are added and edited with the **Structure** object, here the example **Structure** object is given as ``mdl``. The **Element** objects represent linear, surface and solid finite elements connecting different nodes of the structure.

===============
Adding elements
===============

**Element** objects are added to the **Structure** object with the ``.add_element()`` and ``.add_elements()`` methods, by giving the list(s) of nodes that the element(s) connect to, as well as the element type as a string. The **Element** objects are added to the ``.elements`` dictionary, from the classes found in module **compas_fea.structure.element**, where the class names match the string entered for the element type ``type``. The element types include, amongst others, 1D elements: **SpringElement**, **BeamElement**, **TrussElement**, 2D elements: **ShellElement**, **MembraneElement**, and 3D elements: **PentahedronElement**, **TetrahedronElement**, **HexahedronElement**.

As with nodes, the elements will be added with integer keys numbered sequentially starting from 0. **Note**: currently no more than one element can exist for the same collection of nodes, i.e. no overlapping elements are allowed. If you use ``.add_element()`` and an element already exists, nothing else will be added.

.. code-block:: python

    mdl.add_elements(elements=[[0, 4], [1, 4], [2, 4], [3, 4]], type='BeamElement')

    mdl.add_element(nodes=[0, 1, 4], type='ShellElement')

For Abaqus, adding elements will also create a set for each individual element. So for example when element 4 is written to the input file, an element set named **element_4** will also be created. The utility of this is that individual elements can be referenced to, which is useful for individually assigning a thickness, material, section or orientation to specific elements by way of their number.


================
Viewing elements
================

The **Element** objects can be viewed through their integer key and their attributes ``.__name__``, ``.axes``, ``.nodes``, ``.number``, ``.acoustic``, ``.thermal``.

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

Giving a dictionary for the argument ``axes`` when adding the element will store ``{'ex': [], 'ey': [], 'ez': []}`` in the **Element** object's ``.axes`` attribute. The ``'ex'``, ``'ey'`` and ``'ez'`` lists are the element's local `x`, `y` and `z` axes, and are used for example, when orientating cross-sections, using anisotropic materials, or for aligning rebar in concrete shells. If no ``axes`` data are given, it is left up to the finite element solver to determine default local axes values. This default alignment, if supported by the software, is often based on the global axes of the model, thus it is important to understand if these defaults are suitable, especially for an element geometry that does not align well with the global `x`, `y`, `z` directions. If for example you create a **BeamElement** for Abaqus that is perfectly vertical, you will get an error from Abaqus that it was not able to work out a local orientation, OpenSees demands explicitly a local orientation for beams, so this cannot be skipped.

To add the local axes for a line element such as a beam, the ``'ex'`` axis represents the cross-section's major axis, ``'ey'`` the cross-section's minor axis, and ``'ez'`` the axis along the element. For surface elements, the ``'ex'`` and ``'ey'`` axes represent the in-plane local axes, with ``'ez'`` then representing the positive normal vector. The CAD functions (described in the CAD topic) that add elements to the **Structure** from geometry in the workspace, will automate some of these axis definitions/tasks.

.. code-block:: python

    mdl.add_element(nodes=[1, 3], type='BeamElement', axes={'ex': [0, -1, 0]})

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


=======
Meshing
=======

-----------
2D elements
-----------

-----------
3D elements
-----------

When discretising a solid volume into finite elements, the first step is usually to create a mesh that represents the outer-surface of the solid. This mesh can be represented as a triangulated mesh with somewhat equally sized triangles, as there are many algorithms for creating tetrahedron elements from this surface and adding them across the internal volume. The **compas_fea** package supports the use of `TetGen <http://wias-berlin.de/software/index.jsp?id=TetGen&lang=1>`_ via the Python wrapper `MeshPy <https://mathema.tician.de/software/meshpy/>`_, and is independent of any CAD environment. **MeshPy** can easily be installed via ``pip`` on Linux systems, while a ``.whl`` file is recommended for Windows from the excellent resource page `here <https://www.lfd.uci.edu/~gohlke/pythonlibs/#meshpy>`_ .

A function has been set-up to facilitate converting a collection of triangles and vertices data representing the outer-surface, into tetrahedron elements. This is the function ``tets_from_vertices_faces()``, found in **compas_fea.utilities.functions**, where the ``vertices`` co-ordinates, the triangle ``faces``, and a ``volume`` constraint (optional) are given. The outputs of using the function are the points and indices of the tetrahedron corners. If you are in a CAD environment, you can use a previously constructed triangulated outer-surface mesh to create and automatically add tetrahedron elements to your **Structure** object. In Rhino, use **compas_fea.cad.rhino.add_tets_from_mesh()**, and in Blender, use **compas_fea.cad.blender.add_tets_from_mesh()**. These functions effectively wrap around ``tets_from_vertices_faces()`` and add the elements to the **Structure** object. These function calls could look like:

.. code-block:: python

    from compas_fea.cad import rhino

    import rhinoscriptsyntax as rs

    mesh = rs.ObjectsByLayer('mesh')[0]

    rhino.add_tets_from_mesh(structure=mdl, name='elset_tets', mesh=mesh, draw_tets=True, layer='tets', volume=0.1)

.. code-block:: python

    from compas_fea.cad import blender

    from compas_blender.utilities import get_objects

    blender.add_tets_from_bmesh(structure=mdl, name='elset_tets', bmesh=get_objects(layer=0)[0], draw_tets=False, volume=0.002)

For both cases the following must be given: 1) the **Structure** object via ``structure``, 2) the ``name`` of the element set to make after adding the tetrahedrons, and 3) whether to draw mesh representations of the tetrahedrons with the boolean ``draw_tets`` (they will be drawn on layer ``layer``). For the Rhino case above, a mesh was gathered from layer ``'mesh'``, and for Blender the layer number 0. The tetrahedrons will have been added to ``structure.elements``, and the created element set stored under ``structure.sets``. **Note**: take care when plotting a dense collection of tetrahedrons with ``draw_tets=True``, as it can easily consume system memory. An example of some generated and plotted tetrahedrons is shown below.

.. image:: /_images/tets.png
   :scale: 50 %
