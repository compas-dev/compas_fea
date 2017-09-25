********************************************************************************
Loads
********************************************************************************


This page shows how **Load** objects are added to the **Structure** object, here given as ``mdl``.

.. contents::


============
Adding loads
============

Loads can be applied directly to nodes or distributed across elements. A variety of **Load** classes can be imported from **compas_fea.structure.loads** including **PrestressLoad**, **PointLoad**, **LineLoad**, **AreaLoad**, **GravityLoad** and **TributaryLoad**. An example of applying concentrated loads to nodes is shown below. The object is instantiated and stored within the ``.loads`` dictionary of the **Structure** object with the ``add_load()`` method using ``name`` as the string key. The **PointLoad** object requires the nodes to apply the point loads to, taken as the string name of the node set.

.. code-block:: python

   from compas_fea.structure import PointLoad

   mdl.add_load(PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000))


===============
Accessing loads
===============

The **Load** objects can be inspected with their string keys and attributes, showing both the input data and any default zero component values.

.. code-block:: python

   >>> mdl.loads['load_point'].components
   {'x': 10000, 'y': 0, 'z': -10000, 'xx': 0, 'yy': 0, 'zz': 0}

   >>> mdl.loads['load_point'].nodes
   'nset_top'

Given are the input components of the load ``x=10000`` and ``z=-10000``, where the ``y`` component and concentrated moments ``xx``, ``yy`` and ``zz``, as not given, all default to zero.


============
Gravity load
============

Gravitational loading to elements is through the **GravityLoad** class and object. The **GravityLoad** object records the elements to apply gravitational acceleration to, with default acceleration of ``g=-9.81`` and applied in ``z``, but this can be varied in magnitude and for directions ``x`` and ``y``. The elements for the gravity loading in the example below are those in the element set named ``elset_all``.

.. code-block:: python

   from compas_fea.structure import GravityLoad

   mdl.add_load(GravityLoad(name='load_gravity', elements='elset_all'))

   >>> mdl.loads['load_gravity'].components
   {'x': False, 'y': False, 'z': True}

   >>> mdl.loads['load_gravity'].g
   -9.81


=========
Tributary
=========

The **TributaryLoad** can be used to distribute an area load applied to a mesh, as concentrated loads to the nodes of the **Structure** object. The class first takes the ``structure`` to apply the loads to, then the ``name`` of the tributary load, a **Mesh** datastructure object with ``mesh``, and finally ``x``, ``y`` and ``z``. The **Mesh** datastructure will be taken with the area pressure loads ``x``, ``y`` and ``z`` (Pascals), calculate the tributary area of each vertex, and multiply this area by the pressure to get a concentrated load in the component direction. The ``.components`` attribute of the **TributaryLoad** object will then be a dictionary of node keys and for a dictionary of concentrated forces. The class could be used in the following manner:

.. code-block:: python

   from compas_fea.structure import TributaryLoad

   mdl.add_load(TributaryLoad(structure=mdl, name='load_tributary', mesh=mesh, z=-2000))
