********************************************************************************
CAD
********************************************************************************

This page shows how to benefit from using computer aided design and graphics software with the compas_fea package. It will assume that either the ``blender`` or ``rhino`` module of the compas_fea package has been imported to have access to the described functions:

.. code-block:: python

   from compas_fea.cad import rhino

.. code-block:: python

   from compas_fea.cad import blender

.. contents::


========
Geometry
========

------
Layers
------

In Rhino, the function ``add_nodes_elements_from_layers()`` is used to extract Rhino geometry data from the model workspace and place it in the **Structure** object. The function takes a list ``layers`` of layer string names, or a single string for one layer. The Rhino geometry in these layers will be given the same ``line_type`` element or ``mesh_type`` element. The ``line_type`` and ``mesh_type`` are the string names of the element for the classes in **compas_fea.structure.element**. All needed nodes will be added automatically, there is no need to add Rhino points for these. For example, to add lines that are contained in Rhino layer ``'elset_elements'`` to **mdl** as **TrussElement** objects, use the code below. The **TrussElement** objects will be sent to ``mdl.elements`` and nodes (the line endpoints) added to ``mdl.nodes``.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, line_type='TrussElement', layers='elset_elements')

If ``mesh_type`` is given, such as ``'ShellElement'`` or ``'MembraneElement'``, Rhino meshes on the given layers will have their faces individually added as elements to the **Structure**.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, mesh_type='ShellElement', layers='elset_shells')

If ``mesh_type`` is one of the solid element types ``'HexahedronElement'``, ``'TetrahedronElement'``, ``'SolidElement'`` or ``'PentahedronElement'``, Rhino meshes on the layers will be treated as a solid and not broken into faces.

.. code-block:: python

    rhino.add_nodes_elements_from_layers(structure=mdl, mesh_type='HexahedronElement', layers='elset_solids')

In Blender, the function with the same name is used slightly differently, as there are no clear line type objects. Instead, Blender meshes should exist in the given ``layers`` (use the function ``add_nodes_elements_from_bmesh()`` to explicitly give a Blender mesh ``bmesh`` rather than layer numbers). Once the meshes are picked up, the vertices of the Blender meshes will be added to the **Structure** object as nodes, along with: line elements represented by the edges of the mesh and added as element type ``line_type`` and shell elements represented by the faces of the mesh and added as element type ``mesh_type``. If the entire Blender mesh is to be used as a solid element, similar to the Rhino procedure above, then give a solid element type in ``mesh_type``.

.. code-block:: python

  blender.add_nodes_elements_from_layers(structure=mdl, line_type='TrussElement', mesh_type='ShellElement', layers=0)

----------
Local axes
----------

When adding line geometry from layers to the **Structure** object as **Element** objects, the function ``add_nodes_elements_from_layers()`` will also attempt to store the element's local axis in the dictionary ``.axes`` of the **Element** object. This dictionary takes keys ``'ex'``, ``'ey'`` and ``'ez'`` to store a list (the vector) of each element's local axis direction. The function will look at the name of the layer object (``rs.ObjectName()`` in Rhino, ``object.name`` in Blender), check that it is in a ``.json`` dictionary type format, and then attempt to extract lists from keys ``'ex'``, ``'ey'`` and ``'ez'``. The ``'ez'`` direction is not explicitly needed for lines, as it is the direction the line passes through from start to end point. While ``'ex'`` and ``'ey'`` correspond to the local `x` (major) and `y` (minor) axes, looking along the line element from start to finish (i.e. along ``'ez'``). Orientations ``'ex'`` and ``'ey'`` are important for getting the correct local orientation of beam cross-sections.

For shell elements ...


===========
Adding sets
===========

To add Rhino geometry held in layers as sets of the **Structure** object, use the ``add_sets_from_layers()`` function. This function requires the ``structure`` to add to, and the ``layers`` to extract Rhino geometry from. Each layer in the list ``layers``, should exclusively contain Rhino points or Rhino line/mesh objects, otherwise it is not possible to assign that all `guids` in that layer contribute to a node or element set. The name of the set does not need be given, as the function will ensure that added sets inherit the layer names as their keys. If the layer is nested such that it has a name ``'a::b::c'``, then only the last part of the string, i.e. ``'c'``, will be used as the name .

.. code-block:: python

    rhino.add_sets_from_layers(structure=mdl, layers=['nset_pins', 'nset_load', 'elset_elements'])

The Blender equivalent functions are ``add_nset_from_bmeshes()`` and ``add_elset_from_bmeshes()``, where the former function will add vertices from Blender meshes as a node set, and the latter function will add an element set from edges and faces. Either a list of the Blender mesh objects is given directly with ``bmeshes`` or the meshes are extracted from the layer number given by ``layer``. The function ``add_nset_from_objects()`` can be used to add objects' locations as a node set. The ``name`` of the sets must be given, as Blender layers cannot currently be named, as they are only numbered.

.. code-block:: python

  blender.add_nset_from_bmeshes(structure=mdl, layer=0, name='nset_supports')

  blender.add_elset_from_bmeshes(structure=mdl, layer=1, name='elset_elements')

  blender.add_nset_from_objects(structure=mdl, layer=2, name='nset_pins')


=============
Plotting data
=============

Once the **Structure** object has been analysed (see the Analysis topic) and the data stored in ``.results``, it can be plotted in the CAD environment after a small amount of post-processing (see Processing subsection below). The plotting of these data uses the ``plot_data()`` function, which requires the ``structure``, the ``step`` to plot and the ``field`` of interest. For element based data, the ``iptype`` and ``nodal`` string arguments need to be given. Data are currently plotted on simple meshes representing the original geometry. These are simple tubular meshes of given ``radius`` to represent 1D elements, 2D meshes to represent shells and membranes, and voxel based viewers for 3D solid elements.

For Rhino, the meshes will be plotted in either the given ``layer`` name string, or a default layer named **step-field**, for which the layer will first be cleared. This function call could look like the following, where a print will afterwards show how much time the post-processing took:

.. code-block:: python

    rhino.plot_data(mdl, step='step_load', field='um', radius=0.1)

    ***** Data processed : 0.211 s *****

.. code-block:: python

    rhino.plot_data(mdl, step='step_load', field='sxx', nodal='max', iptype='mean')

    ***** Data processed : 4.539 s *****

The Blender function works in exactly the same way, with ``layer`` being the integer layer number and not a string as with Rhino:

.. code-block:: python

  blender.plot_data(mdl, step='step_load', field='um', layer=3)

----------
Processing
----------

A degree of data post-processing is performed before plotting, through the function ``postprocess()`` of the **compas_fea.utilities.functions** module. This post-processing requires NumPy and SciPy, and so is carried out in a subprocess (via compas XFunc) for non-CPython based CAD environments like Rhino. The function calls a selection of other functions which do the following:

- Calculate the deformed nodal co-ordinates with given ``scale`` factor, which become the plot meshes vertices.

- Process element data based on the ``iptype`` and ``nodal`` strings, see below for explanation.

- Normalise the data between -1 and 1, using the largest absolute value in the data.

- Calculate the colour to plot each nodal data value from a consistent colour spectrum.

- Cap colour values based on the minimum and maximum values given in ``cbar``.

Because the raw nodal data contains single float values for each node, these values can be plotted directly as vertex colours on the plotting meshes. However as there are in general multiple data values for each element, some processing must be done to convert elemental data to suitable colour values at the nodes. The first step that the ``postprocess()`` function will do for elemental data, is convert all of the integration and section point data for an element to a user-directed single value with ``iptype``. The string ``iptype`` can be ``'mean'``, ``'max'`` or ``'min'``, to take the average, maximum positive or minimum negative value of the element data. The next step is to use this data and convert it a nodal value, as each node will connect to many elements and so have many adjacent element data values. Either ``'mean'``, ``'max'`` or ``'min'`` is given as a string for ``nodal``, giving then a value at each node based on all elements that connect to it. So for example, to find conservatively the most heavily loaded nodal Von Mises stress value from elemental data, one would use:

.. code-block:: python

    plot_data(mdl, step='step_load', field='smises', iptype='max', nodal='max')

and to plot the most compressive axial stress values use (with compression negative and local 'x' axis):

.. code-block:: python

    plot_data(mdl, step='step_load', field='sxx', iptype='min', nodal='min')

**Note**: using ``nodal='mean'`` with a coarse finite element mesh could give unexpected results. This is because element data can change suddenly across elements in coarse meshes, leading to a mean value at a shared node that is somewhat poorly representative. This effect can be resolved by refining the mesh in the areas where stresses may change quickly or form concentrations, such as near supports, applied loads or areas of peak internal forces and moments.

--------
Colorbar
--------

A colorbar to the data will be plotted by default in each plotting layer and to the right of the model, the size of which can be controlled by ``'colorbar_size'``. The colorbar limits will range from negative to positive of the maximum data value of the field, even if the results are all positive or negative. The advantage of this, as opposed to using the minimum to maximum range, is that positive values will always be red, orange and yellow, neutral values green, and negative values blue, indigo and violet. The extremes of the plotted data, as well as some intermediate values, will be written as text boxes, along with the zero point in the middle. If minimum and maximum values of the colorbar are given in ``cbar`` when calling ``plot_data()``, for example a maximum ``cbar[1]`` of 3 MPa, then the colorbar ends will cap at 3 MPa, and plot red values for all data above 3 MPa. The step and field will also be displayed as a title to the colorbar, and any mode or frequencies placed at the bottom.

.. image:: /_images/colorbar.png
   :scale: 30 %

------------------
Principal stresses
------------------

As stress is a tensor, any material point has a local axes orientation where maximum and minimum normal stresses occur orthogonally and with zero shear stress. These are the principal stress components ``'smaxp'`` and ``'sminp'``. From knowing (for shell elements) the ``'sxx'`` (normal stress in `x`), ``'syy'`` (normal stress in `y`) and ``'sxy'`` (shear stress) values at integration points, the orientation of the principal stresses can be determined relative to the element's local axes (component ``'axes'``). This calculation is based on elementary material mechanics (see Mohr Circles for reference) and has been performed in a plotting function ``plot_principal_stresses()``, which takes argument ``ptype`` as a string ``'sminp'`` or ``'smaxp'``, and then a relative ``scale`` to draw the length of vector lines. A call of the Rhino function plots the following lines below, where red and blue lines are drawn to show tension (max principal) and compression (min principal):

.. code-block:: python

   rhino.plot_principal_stresses(structure=mdl, step='step_loads', ptype='sminp', scale=0.2)

   rhino.plot_principal_stresses(structure=mdl, step='step_loads', ptype='smaxp', scale=0.2)

.. image:: /_images/principals.png
   :scale: 70 %
