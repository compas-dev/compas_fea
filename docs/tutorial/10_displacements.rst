********************************************************************************
Displacements
********************************************************************************

This page shows how **Displacement** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``. **Displacement** objects can be used to describe boundary conditions or imposed displacements.

====================
Adding displacements
====================

**Displacement** objects are used to apply boundary conditions to the model as well as to impose movements directly at selected nodes. Along with **Load** objects, they form the main actions acting on a structural model during the analysis, to do so, they are combined with **Step** objects (see next topic). It is necessary for the first **Step** in the **Structure** to be associated with the boundary conditions represented by **Displacement** objects, these are those that do not change throughout the entire analysis. The following example shows how a **PinnedDisplacement** class is first imported, an object instantiated, and then this object added to the ``.displacements`` dictionary of the **Structure** object. All **Displacement** objects currently use only the global co-ordinate system with ``axes='global'``, this will be improved later with the optional use of the ``'local'`` nodal system. The ``nodes`` that the displacement is applied to, should be the string name of the node set, or a list of node numbers.

.. code-block:: python

    from compas_fea.structure import PinnedDisplacement

    mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))  # add a PinnedDisplacement to 'nset_base'


===================================
Accessing and editing displacements
===================================

To access or edit the data stored on a **Displacement** object, use its string key and view or edit its attributes as needed from the ``.displacements`` dictionary. Like all other objects, printing a **Displacement** will show a summary to the terminal.

.. code-block:: python

   >>> mdl.displacements['disp_pinned'].components  # show the components of Displacement 'disp_pinned'
   {'x': 0, 'y': 0, 'z': 0, 'xx': None, 'yy': None, 'zz': None}

   >>> mdl.displacements['disp_pinned'].nodes  # show the nodes that 'disp_pinned' applies to
   'nset_base'

   >>> mdl.displacements['disp_pinned']  # Displacement object name 'disp_pinned'
   PinnedDisplacement(disp_pinned)

   >>> print(mdl.displacements['disp_pinned'])  # Summary of PinnedDisplacement(disp_pinned)

   compas_fea PinnedDisplacement object
   ------------------------------------
   name       : disp_pinned
   nodes      : nset_base
   components : {'x': 0, 'y': 0, 'z': 0, 'xx': None, 'yy': None, 'zz': None}
   axes       : global

The example **PinnedDisplacement** object above restrains translations in all directions but allows rotations about any axis, as indicated by the automatic assignment of zero for ``x``, ``y`` and ``z`` for the translational degrees-of-freedom, and ``None`` for the rotational degrees-of-freedom ``xx``, ``yy`` and ``zz``. Non-zero values for any of the six components could be given to simulate support settlements or to perform a displacement controlled analysis, this is best performed with a **GeneralDisplacement** object.


=====
Types
=====

Different **Displacement** object types are available from the classes in **compas_fea.structure.displacement**, these are detailed below:

-------
General
-------

A **GeneralDisplacement** object is used for manually defining all six spatial translational and rotational degrees-of-freedom, and so is the most general type of **Displacement** object. The object has components ``x``, ``y``, ``z``, ``xx``, ``yy`` and ``zz`` all equal to ``None`` by default. The ``name`` of the object, and the nodes it should act on must both be given.

.. code-block:: python

   from compas_fea.structure import GeneralDisplacement

   mdl.add(GeneralDisplacement(name='disp_general', nodes='nset_base', x=0.1, zz=0.05, z=0))  # define x, z, zz

------
Pinned
------

A **PinnedDisplacement** object is used for restraining all spatial translations, but still allowing rotations to occur. The object has components ``x``, ``y``, ``z`` as 0 and ``xx``, ``yy``, ``zz`` as ``None``, which are all defined automatically. The ``name`` of the object, and the nodes it should act on must both be given.

.. code-block:: python

   from compas_fea.structure import PinnedDisplacement

   mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))  # x, y and z are equal to 0 for 'nset_base'

-----
Fixed
-----

A **FixedDisplacement** object is used for restraining all spatial translations and all rotations. The object has all components ``x``, ``y``, ``z``, ``xx``, ``yy``, ``zz`` as 0, which are all defined automatically. The ``name`` of the object, and the nodes it should act on must both be given.

.. code-block:: python

   from compas_fea.structure import FixedDisplacement

   mdl.add(FixedDisplacement(name='disp_fixed', nodes='nset_base'))  # x, y, z, xx, yy, zz are all 0 for 'nset_base'

There are additionally three other types of fixed displacement objects, **FixedDisplacementXX**, **FixedDisplacementYY** and **FixedDisplacementZZ**, which all assert zero translations ``x``, ``y``, ``z`` as 0, but with the rotations also fixed for the indicated axis. So, **FixedDisplacementXX** additionally clamps ``xx=0``, **FixedDisplacementYY** clamps ``yy=0`` and **FixedDisplacementZZ** ``zz=0``. These objects are created in the same way, for example like:

.. code-block:: python

   from compas_fea.structure import FixedDisplacementXX

   mdl.add(FixedDisplacementXX(name='disp_fixedxx', nodes='nset_base'))  # x, y, z and xx are all 0 for 'nset_base'

-------
Rollers
-------

There are six types of roller displacement objects, **RollerDisplacementX**, **RollerDisplacementY**,   **RollerDisplacementZ**, **RollerDisplacementXY**, **RollerDisplacementYZ** and **RollerDisplacementXZ**. These are all based on a **PinnedDisplacement** object, with the indicated translational degree(s)-of-freedom released.  So for example, **RollerDisplacementX** is released in `x` with ``x=None``, and so has ``y`` and ``z`` as 0, while **RollerDisplacementXY** is released in both `x` and `y` with ``x`` and ``y`` as ``None``, leaving only ``z=0``.

.. code-block:: python

   from compas_fea.structure import RollerDisplacementXY

   mdl.add(RollerDisplacementXY(name='disp_roller', nodes='nset_base'))  # only z equals 0 for 'nset_base'
