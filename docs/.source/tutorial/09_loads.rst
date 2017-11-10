********************************************************************************
Loads
********************************************************************************


This page shows how **Load** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``.

.. contents::


============
Adding loads
============

Loads can be applied directly to nodes or distributed across elements. To do this, a variety of **Load** classes can be imported from **compas_fea.structure.load** including **PrestressLoad**, **PointLoad**, **LineLoad**, **AreaLoad**, **GravityLoad** and **TributaryLoad**. The objects are instantiated and stored within the ``.loads`` dictionary of the **Structure** object with the ``add_load()`` method using ``name`` as the string key. An example of applying concentrated loads to nodes is shown below with **PointLoad**. The **PointLoad** object requires the nodes to apply the point loads to, taken as the string name of the node set.

.. code-block:: python

   from compas_fea.structure import PointLoad

   mdl.add_load(PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000))


===============
Accessing loads
===============

The **Load** objects can be inspected and edited via their string keys and attributes, showing both the input data given at instantiation and any default zero component values.

.. code-block:: python

   >>> mdl.loads['load_point'].components
   {'x': 10000, 'y': 0, 'z': -10000, 'xx': 0, 'yy': 0, 'zz': 0}

   >>> mdl.loads['load_point'].nodes
   'nset_top'

In the example above are the input components of the load ``x=10000`` and ``z=-10000`` with the ``y`` component and concentrated moments ``xx``, ``yy`` and ``zz`` all defaulted to zero.


==========
Point load
==========

The **PointLoad** object applies concentrated loads (forces ``x``, ``y``, ``z`` and/or moments ``xx``, ``yy``, ``zz``) directly to ``nodes``. The ``nodes`` to apply the load to is given as either the string name of the node set or a list of nodes. The ``name`` of the **PointLoad** is also required. **PointLoad** objects currently only utilise the global co-ordinate system.

.. code-block:: python

   from compas_fea.structure import PointLoad

   mdl.add_load(PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000, yy=1000))


=========
Line load
=========

The **LineLoad** object applies distributed loads per unit length (forces / metre ``x``, ``y``, ``z``) along line ``elements``. The ``elements`` to apply the load to is given as either the string name of the element set or a list of elements. The ``name`` of the **LineLoad** is also required. If ``axis='global'``, the ``x``, ``y`` and ``z`` components will be in-line with the global co-ordinate system, while ``axis='local'`` takes ``x`` and ``y`` as the local cross-section axes.

.. code-block:: python

   from compas_fea.structure import LineLoad

   mdl.add_load(LineLoad(name='load_line', nodes='elset_beams', y=-10000, axes='local'))


=========
Area load
=========

The **AreaLoad** object applies distributed loads per unit area (pressures ``x``, ``y``, ``z``) on ``elements``. The ``elements`` to apply the load to is given as either the string name of the element set or a list of elements. The ``name`` of the **AreaLoad** is also required. Only ``axis='local'`` is currently supported, whereby ``x`` and ``y`` are local surface shears and ``z`` is the local normal pressure.

.. code-block:: python

   from compas_fea.structure import AreaLoad

   mdl.add_load(AreaLoad(name='load_pressure', nodes='elset_shells', z=-10000, axes='local'))


============
Gravity load
============

Gravitational loading to elements is through the **GravityLoad** class and object. The **GravityLoad** object records the ``elements`` to apply gravitational acceleration to either via the element set name string, or a list of elements. The default gravitational acceleration is ``g=-9.81`` and applied in ``z``, but this can be varied in magnitude and for directions ``x`` and ``y``. The elements for the gravity loading in the example below are those in the element set named ``elset_all``.

.. code-block:: python

   from compas_fea.structure import GravityLoad

   mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

   >>> mdl.loads['load_gravity'].components
   {'x': False, 'y': False, 'z': True}

   >>> mdl.loads['load_gravity'].g
   -9.81


==============
Tributary load
==============

The **TributaryLoad** can be used to distribute an area load applied to a mesh, as concentrated loads to the nodes of the **Structure** object. The class first takes the ``structure`` to apply the loads to, then the ``name`` of the tributary load, a **Mesh** datastructure object with ``mesh``, and finally components``x``, ``y`` and ``z``. The **Mesh** datastructure will be taken with the area pressure loads ``x``, ``y`` and ``z`` to calculate the tributary area of each vertex, and multiply this area by the pressure to get a concentrated load in the component direction. The ``.components`` attribute of the **TributaryLoad** object will then be a dictionary of node keys and for a dictionary of concentrated forces. The global co-ordinate directions (``axis='global'`` by default) are used for the components of the pressures and final forces. The class could be used in the following manner:

.. code-block:: python

   from compas_fea.structure import TributaryLoad

   mdl.add_load(TributaryLoad(structure=mdl, name='load_tributary', mesh=mesh, z=-2000))


===================
Harmonic point load
===================

The **HarmonicPointLoad** object applies concentrated loads (forces ``x``, ``y``, ``z`` and/or moments ``xx``, ``yy``, ``zz``) directly to ``nodes`` in a harmonic analysis. The ``nodes`` to apply the load to is given as either the string name of the node set or a list of nodes. The ``name`` of the **HarmonicPointLoad** is also required. **HarmonicPointLoad** objects currently only utilise the global co-ordinate system.

.. code-block:: python

   from compas_fea.structure import HarmonicPointLoad

   mdl.add_load(HarmonicPointLoad(name='load_point-harmonic', nodes='nset_top', z=-10000))
