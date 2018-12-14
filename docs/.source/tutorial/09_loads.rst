********************************************************************************
Loads
********************************************************************************

This page shows how **Load** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``. **Load** objects can be applied to either nodes or elements, and are activated during steps.

============
Adding loads
============

Loads can be applied directly to nodes or distributed (currently only uniformly) across elements. For this, a variety of **Load** classes can be imported from **compas_fea.structure.load** including types such as **PrestressLoad**, **PointLoad**, **LineLoad**, **AreaLoad**, **GravityLoad** and **TributaryLoad**. The **Load** objects are instantiated with these classes and stored within the ``.loads`` dictionary of the **Structure** object with the ``.add()`` method, and using ``name`` as the string key. An example of applying concentrated loads in the ``x`` and ``z`` directions directly to nodes in a node set, is shown with the **PointLoad** example below. The **PointLoad** class requires the components of the load and the ``nodes`` to apply the point loads to, taken as the string name of the node set (``'nset_top'`` in this case) or a list of individual node numbers.

.. code-block:: python

    from compas_fea.structure import PointLoad

    mdl.add(PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000))  # adding a PointLoad to 'nset_top'


===========================
Accessing and editing loads
===========================

The **Load** objects can be inspected, printed and edited at any time via their string keys and attributes, and will show both the input data given at the time of instantiation and any default zero component values. If there are no  non-zero components given at the time of creating the object, then the **Load** object effectively doesn't do anything, as all components are zero. In the example below are the input components of the load ``x=10000`` and ``z=-10000`` (both are forces with units N) with the ``y`` component and concentrated moments (units Nm) ``xx``, ``yy`` and ``zz`` all set to the default value of zero.

.. code-block:: python

    >>> mdl.loads['load_point'].components
    {'x': 10000, 'y': 0, 'z': -10000, 'xx': 0, 'yy': 0, 'zz': 0}  # show or edit the load components

    >>> mdl.loads['load_point'].nodes  # examine the nodes the load is applied to
    'nset_top'

    >>> mdl.loads['load_point']  # PointLoad object 'load_point'
    PointLoad(load_point)

    >>> print(mdl.loads['load_point'])  # print a summary of the load

    compas_fea PointLoad object
    -------------------
    name       : load_point
    axes       : global
    components : {'x': 10000, 'y': 0, 'z': -10000, 'xx': 0, 'yy': 0, 'zz': 0}
    nodes      : nset_top
    elements   : []


=============
PrestressLoad
=============

A **PrestressLoad** is currently used to add an axial pre-stress, other components of stress will be added as additional functionality at a later date. A **PrestressLoad** is created with the string ``name`` of the object, the ``elements`` that it applies to, and the ``sxx`` (axial) stress component in Pa, which acts along the local `x` axis for shells and along the length for beams and trusses. This object can be created and added as follows:

.. code-block:: python

    from compas_fea.structure import PrestressLoad

    >>> mdl.add(PrestressLoad(name='load_prestress', elements='elset_ties', sxx=50*10**6))


=========
PointLoad
=========

The **PointLoad** object applies concentrated loads (forces in units N for ``x``, ``y``, ``z`` and/or moments in units Nm for ``xx``, ``yy``, ``zz``) directly to ``nodes`` of the **Structure**. The ``nodes`` to apply the load to is given as either the string name of the node set or as a list of nodes. The ``name`` of the **PointLoad** is also required for its key. **PointLoad** objects currently only utilise the global co-ordinate system, they do not yet use the local nodal co-ordinate system (`ex`, `ey`, `ez`).

.. code-block:: python

    from compas_fea.structure import PointLoad

    mdl.add(PointLoad(name='load_point', nodes='nset_top', x=10000, z=-10000, yy=1000))


==========
PointLoads
==========

The **PointLoads** object applies different values of concentrated loads (forces in units N for ``x``, ``y``, ``z`` and/or moments in units Nm for ``xx``, ``yy``, ``zz``) directly to different nodes of the **Structure**. The nodes to apply the loads to are the keys of the ``components`` dictionary, with the values of this dictionary as the components of each individual point load. The ``name`` of the **PointLoads** is required for its own key. **PointLoads** objects currently only utilise the global co-ordinate system, they do not yet use the local nodal co-ordinate system (`ex`, `ey`, `ez`).

.. code-block:: python

    from compas_fea.structure import PointLoads

    components = {
        4: {'x': 1000, 'y': -500},  # apply a load in x of 1000 and y of -500 to node 4
        9: {'zz': 200},  # apply a moment about zz of 200 to node 9
    }
    mdl.add(PointLoads(name='load_points', components=components))


========
LineLoad
========

The **LineLoad** object applies distributed loads per unit length (forces in units of N/m in ``x``, ``y``, ``z``) uniformly along line elements such as beams. The ``elements`` to apply the load to is given as either the string name of the element set or as a list of elements. The ``name`` of the **LineLoad** is also required as is key. If ``axis='global'``, the ``x``, ``y`` and ``z`` components will be in-line with the global co-ordinate system, while ``axis='local'`` takes ``x`` and ``y`` as the local cross-section axes `ex` and `ey`, i.e. positive ``y`` would be away from the centroid of the cross-section, not towards it.

.. code-block:: python

    from compas_fea.structure import LineLoad

    mdl.add(LineLoad(name='load_line', elements='elset_beams', y=-10000, axes='local'))


========
AreaLoad
========

The **AreaLoad** object applies distributed loads per unit area (pressures ``x``, ``y``, ``z`` in units of Pa) on elements such as **ShelElement** objects. The ``elements`` to apply the load to is given as either the string name of the element set or as a list of elements, and the ``name`` of the **AreaLoad** is required for its key. Only ``axis='local'`` is currently supported for Abaqus, whereby ``x`` and ``y`` are local surface shears and ``z`` is the local normal pressure.

.. code-block:: python

    from compas_fea.structure import AreaLoad

    mdl.add(AreaLoad(name='load_pressure', elements='elset_shells', z=-10000, axes='local'))


===========
GravityLoad
===========

Gravity loading to elements is through the **GravityLoad** class and object. The **GravityLoad** object records the ``elements`` to apply gravitational acceleration to either via the element set name as a string, or as a list of elements. The default gravitational acceleration is ``g=-9.81`` and applied in ``z``, but this can be varied in magnitude and for directions ``x`` and ``y`` (which is useful if a model isn't using ``z`` as the vertical direction). The ``elements`` for the gravity loading in the example below are those in the element set named ``'elset_all'``. Gravity loads are always automatically calculated and applied knowing the material density, element type and cross-section geometry, so only the reference to the elements is needed to apply the load, as all other data will be known.

.. code-block:: python

    from compas_fea.structure import GravityLoad

    mdl.add(GravityLoad(name='load_gravity', elements='elset_all'))

    >>> mdl.loads['load_gravity'].components  # check the gravity components
    {'x': 0.0, 'y': 0.0, 'z': 1.0}

    >>> mdl.loads['load_gravity'].g  # see magnitude of gravitational acceleration
    -9.81


=============
TributaryLoad
=============

The **TributaryLoad** class can be used to distribute a uniform area load (in units of Pa) that is applied to a **Mesh** datastructure, as equivalent point loads (in units of N) to the nodes of the **Structure** object. The class first takes the ``structure`` to apply the point loads to, then the ``name`` of the **TributaryLoad**, then a **Mesh** datastructure object with ``mesh``, and finally component pressures ``x``, ``y`` and ``z``. The class would be used in the following manner:

.. code-block:: python

    from compas_fea.structure import TributaryLoad

    mdl.add(TributaryLoad(structure=mdl, name='load_tributary', mesh=mesh, z=-2000))

The **Mesh** datastructure will be combined with the pressures ``x``, ``y`` and ``z`` to calculate the tributary area of each vertex and multiply this area by the pressure to get a point load in the component direction. The ``.components`` attribute of the **TributaryLoad** object will be a dictionary with **Structure** node keys, and the values of these keys are dictionaries of point loads data in ``x``, ``y`` and ``z`` (see below). The global co-ordinate directions ``axis='global'`` are used for the components of the pressures and final point loads.

.. code-block:: python

    mdl.loads['load_tributary'].components

    {2: {'z':  -66.28091, 'y': 0.0, 'x': 0.0},
     3: {'z':  -86.36518, 'y': 0.0, 'x': 0.0},
     4: {'z': -121.55623, 'y': 0.0, 'x': 0.0},
     ...
     25: {'z':  -79.5333, 'y': 0.0, 'x': 0.0},
     26: {'z': -283.3817, 'y': 0.0, 'x': 0.0}}


=================
HarmonicPointLoad
=================

The **HarmonicPointLoad** object applies concentrated loads (forces ``x``, ``y``, ``z`` and/or moments ``xx``, ``yy``, ``zz``) directly to ``nodes`` in a harmonic analysis. The ``nodes`` to apply the load to is given as either the string name of the node set or a list of nodes. The ``name`` of the **HarmonicPointLoad** is also required to act as its key. **HarmonicPointLoad** objects currently only utilise the global co-ordinate system.

.. code-block:: python

    from compas_fea.structure import HarmonicPointLoad

    mdl.add(HarmonicPointLoad(name='load_point-harmonic', nodes='nset_top', z=-10000))
