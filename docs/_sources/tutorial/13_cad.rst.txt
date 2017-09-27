********************************************************************************
CAD
********************************************************************************

This page shows how to benefit from using computer aided design and graphics software with the compas_fea package. It will assume that either the ``blender`` or ``rhino`` module of the compas_fea package has been imported:

.. code-block:: python

   from compas_fea.cad import rhino

.. code-block:: python

   from compas_fea.cad import blender

.. .. contents::


========
Geometry
========

------
Layers
------

In Rhino, the function ``add_nodes_elements_from_layers()`` is used to extract Rhino geometry data and place it in the **Structure** object. The function takes a list ``layers`` of layer string names, for which each layer should contain only lines or meshes and not a mixture of both, as all 'guids' of the Rhino geometry in these layers will be given the same ``element_type``. The ``element_type`` is the string name of the element for the classes in **compas_fea.structure.elements**. All needed nodes will be added automatically, there is no need to add Rhino points for these.

For example, to add lines that are contained in Rhino layer ``'elset_elements'`` to **mdl** as **TrussElement** objects, use the code below. The **TrussElement** objects will be sent to ``mdl.elements`` and nodes (the line endpoints) added to ``mdl.nodes``.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, element_type='TrussElement', layers=['elset_elements'])

If ``element_type`` is ``'ShellElement'`` or ``'MembraneElement'``, Rhino meshes on the given layers will have their faces individually added as elements to the **Structure**.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, element_type='ShellElement', layers=['elset_shells'])

If ``element_type`` is one of the solid element types ``'HexahedronElement'``, ``'TetrahedronElement'``, ``'SolidElement'`` or ``'PentahedronElement'``, Rhino meshes on the layers will be treated as a solid and not broken into faces.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, element_type='HexahedronElement', layers=['elset_solids'])

In Blender, the equivalent function with the same name is used slightly differently, as there are no clear point and line type objects. Instead, Blender meshes should exist in the given ``layers`` (use the function ``add_nodes_elements_from_bmesh()`` to explicitly give a Blender mesh ``bmesh`` rather than layer numbers). Once the meshes are picked up, the vertices of the Blender meshes will be added to the **Structure** object as nodes, along with: line elements represented by the edges of the mesh and added as element type ``edge_type``, and shell elements represented by the faces of the mesh and added as element type ``face_type``. If the entire Blender mesh is to be used as a solid element, similar to the Rhino procedure above, then give a solid element type in ``block_type``.

.. code-block:: python

  blender.add_nodes_elements_from_layers(structure=mdl, edge_type='TrussElement', face_type='ShellElement', layers=[0])

----------
Local axes
----------

When adding line geometry from layers to the **Structure** object as **Element** objects, the function ``add_nodes_elements_from_layers()`` will also attempt to store the element's local axis in the dictionary ``.axes`` of the **Element** object. This dictionary takes keys ``'ex'``, ``'ey'`` and ``'ez'`` to store a list (the vector) of each element's local axis direction. The function will look at the name of the layer object (``rs.ObjectName()`` in Rhino), check that it is in a ``.json`` dictionary type format, and then attempt to extract lists from keys ``'ex'``, ``'ey'`` and ``'ez'``. The ``'ez'`` direction is not explicitly needed for lines, as it is the direction the line passes through from start to end point. While ``'ex'`` and ``'ey'`` correspond to the local `x` (major) and `y` (minor) axes, looking along the line element from start to finish (i.e. along ``'ez'``). Orientations ``'ex'`` and ``'ey'`` are important for getting the correct local orientation of beam cross-sections.

For shell elements ...


===========
Adding sets
===========

To add Rhino geometry held in layers as sets of the **Structure** object, use the ``add_sets_from_layers()`` function. This function requires the ``structure`` to add to, and the ``layers`` to extract Rhino geometry from. Each layer in the list ``layers``, should exclusively contain Rhino points or Rhino line/mesh objects, otherwise it is not possible to assign that all `guids` in that layer contribute to a node or element set. The name of the set does not need be given, as the function will ensure that added sets inherit the layer names as their keys. If the layer is nested such that it has a name ``'a::b::c'``, then only the last part of the string ``'c'`` will be used as the name .

.. code-block:: python

    rhino.add_sets_from_layers(structure=mdl, layers=['nset_pins', 'nset_load', 'elset_elements'])

The Blender equivalent functions are ``add_nset_from_bmeshes()`` and ``add_elset_from_bmeshes()``, where the former will add vertices from Blender meshes as a node set, and the latter an element set from edges and faces. Either a list of the Blender mesh objects is given directly with ``bmeshes`` or the meshes are extracted from the layer ``layer``. The function ``add_nset_from_objects()`` can be used to add objects' locations as a node set. The ``name`` of the sets must be given, as Blender layers cannot currently be named, as they are only numbered.

.. code-block:: python

  blender.add_nset_from_bmeshes(structure=mdl, layer=0, name='nset_supports')

  blender.add_elset_from_bmeshes(structure=mdl, layer=1, name='elset_elements')

  blender.add_nset_from_objects(structure=mdl, layer=2, name='nset_pins')


=============
Plotting data
=============

Once the **Structure** object has been analysed (see Analysis topic) and the relevant ``.json`` files created, the data can be plotted in the CAD environment. The plotting of these data uses the ``plot_data()`` function, which requires the following input: the ``structure``, the ``path`` and ``name`` of the ``.json`` files, the ``step`` to plot, the ``field`` and ``component`` of the data, and ``iptype`` and ``nodal`` if plotting element data . Data are currently plotted on simple meshes representing the original geometry. These are simple tubular meshes of given ``radius`` to represent line elements, 2D meshes to represent shells and membranes, and voxel based viewers for 3D solid elements.

For Rhino, the meshes will be plotted in either the given ``layer`` name string, or a default layer named **step-field-component**, for which the layer will first be cleared. This function call could look like:

.. code-block:: python

    rhino.plot_data(mdl, path='C:/Temp/', name='simple-truss', step='step_load', field='U', component='magnitude')

A snippet summary will be printed, giving information on how much time the whole analysis (all steps) took, how long the data took to extract from the output data file, and how long the post-processing of that step took (see next section).

.. code-block:: python

    Step summary: step_load
    -----------------------
    Frame description: Increment      1: Step Time =    1.000
    Analysis time: 5.203
    Extraction time: 0.011
    Processing time: 0.008

The Blender function works in exactly the same way, with ``layer`` being the integer layer number and not a string as with Rhino:

.. code-block:: python

  blender.plot_data(mdl, path='C:/Temp/', name='simple-truss', step='step_load', field='U', component='magnitude', layer=3)

----------
Processing
----------

A degree of data post-processing is performed before plotting, through the function ``postprocess()`` of the **compas_fea.utilities.functions** module. This post-processing requires NumPy and SciPy, and so is carried out in a subprocess for non-CPython based CAD environments like Rhino. The function calls a selection of other functions which do the following:

- Load the correct ``.json`` data based on the input arguments to ``plot_data()``.

- Calculate the deformed nodal co-ordinates with given ``scale`` factor, which become the plot meshes vertices.

- Process element data based on the ``iptype`` and ``nodal`` strings, see below for explanation.

- Normalise the data between -1 and 1, using the largest absolute value in the data set.

- Calculate the colour to plot each nodal data value from a consistent colour spectrum.

- Cap colour values based on the minimum and maximum values given in ``cbar``.

---------
Node data
---------

Because the raw node data (e.g. ``'RF'``, ``'RM'``, ``'U'``, ``'UR'``, ``'CF'``, ``'CM'`` ) contains single values for each node, these values can be plotted directly as vertex colours on the plotting meshes.

------------
Element data
------------

As there are in general multiple data values for each element (see Analysis topic), some processing must be done to convert this data (e.g. ``'SF'``, ``'SM'``, ``'SK'``, ``'SE'``, ``'S'``, ``'E'``, ``'PE'``) to suitable colour values at the nodes.

The first action that the ``postprocess()`` function will do, is convert all of the integration and section point data for an element to a user-directed single value with ``iptype``. The string ``iptype`` can be ``'mean'``, ``'max'`` or ``'min'``, to take the average, maximum positive or minimum negative value of the element data.

The next step is to use this data and convert it a ``nodal`` value, as each node will connect to many elements and so be adjacent to many element data values. Either ``'mean'``, ``'max'`` or ``'min'`` is given as a string for ``nodal``, plotting then a value at each node based on all elements that connect to it. So for example, to find conservatively the most heavily loaded nodal Von Mises stress value one would use:

.. code-block:: python

    plot_data(mdl, path, name='simple-truss', step='step_load', field='S', component='mises', iptype='max', nodal='max')

and to plot the most compressive (with compression negative) values use:

.. code-block:: python

    plot_data(mdl, path, name='simple-truss', step='step_load', field='S', component='minPrincipal', iptype='min', nodal='min')

**Note**: using ``'mean'`` for ``nodal`` and with a coarse finite element mesh could give unexpected results. This is because element data, such as stresses, can change suddenly across elements in coarse meshes, leading to a mean value at a shared node that is somewhat poorly representative. This effect can be resolved by refining the mesh in the areas where stresses may change quickly or form concentrations, such as near supports, applied loads or areas of peak internal forces and moments.

--------
Colorbar
--------

A colorbar will be plotted by default in a layer named ``'colorbar'`` in Rhino and layer 19 (i.e. the last layer 20) in Blender. If a mesh (ideally rectangular) in this layer already exists, it will be used as a colorbar, allowing the user to define the size and location of the colorbar mesh. The colorbar limits will range from negative to positive of the maximum data value, even if the results are all positive or negative. The advantage of this, as opposed to using the minimum to maximum range, is that positive values will always be the colours red, orange and yellow, neutral values green, and negative values blue, indigo and violet. The extremes of the plotted data will be written as text boxes at the lower and upper ends, along with the zero point in the middle. If minimum and maximum values of the colorbar are given in ``cbar`` when calling ``plot_data()``, for example a maximum ``cbar[1]`` of 3 MPa, then the colorbar ends will cap at 3 MPa, and plot red values for all data >= 3 MPa.

------------------
Principal stresses
------------------

As stress is a tensor, any material point has a local axes orientation where normal stress is a maximum, and a minimum normal stress is orthogonal with shear stresses zero. These are the principal stress components ``'maxPrincipal'`` and ``'minPrincipal'`` of field ``'S'``. From knowing (for shell elements) the ``'S11'`` (normal stress 1), ``'S22'`` (normal stress 2) and ``'S12'`` (shear stress) values at integration points, the orientation of the principal stresses can be determined relative to the element's local axes (component ``'axes'``). This calculation is based on elementary material mechanics (see Mohr Circles for reference) and has been performed in a plotting function ``plot_principal_stresses()``, which takes the standard folder and file arguments to locate the stress data (``path``, ``name``, ``step``) and argument ``ptype`` as a string ``'min'`` or ``'max'`` for ``'minPrincipal'`` or ``'maxPrincipal'`` stresses, and then a relative ``scale`` to draw the length of vector lines. A call of the Rhino function plots the following lines below, where red and blue lines are drawn to show tension (maxPrincipal) and compression (minPrincipal):

.. code-block:: python

   rhino.plot_principal_stresses(structure=mdl, path='C:/Temp/', name='shell', step='step_loads', ptype='min', scale=0.2)

   rhino.plot_principal_stresses(structure=mdl, path='C:/Temp/', name='shell', step='step_loads', ptype='max', scale=0.2)

.. image:: /_images/principals.png
   :scale: 70 %
