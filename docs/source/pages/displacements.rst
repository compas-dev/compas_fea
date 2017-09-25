********************************************************************************
Displacements
********************************************************************************


This page shows how **Displacement** objects are added to the **Structure** object, here given as ``mdl``.

.. contents::


====================
Adding displacements
====================

**Displacement** objects are used to apply boundary conditions as well as impose movements directly at nodes. Along with **Load** objects, they form the main actions acting on a structure. The following example shows how a **PinnedDisplacement** class is first imported, an object instantiated and then added to the dictionary ``.displacements`` of the **Structure** object.

.. code-block:: python

   from compas_fea.structure import PinnedDisplacement

   mdl.add_displacement(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))


=======================
Accessing displacements
=======================

To access a **Displacement** object, use its string key:

.. code-block:: python

   >>> mdl.displacements['disp_pinned'].components
   {'x': 0, 'y': 0, 'z': 0, 'xx': None, 'yy': None, 'zz': None}

   >>> mdl.displacements['disp_pinned'].nodes
   'nset_base'

A **PinnedDisplacement** object restrains translations in all directions but allows rotations about any axis, as indicated by the automatic assignment of zero for ``x``, ``y`` and ``z``, and ``None`` values for ``xx``, ``yy`` and ``zz``. Non-zero values for the six components could be given to simulate support settlements or to perform a displacement controlled analysis.


=====
Types
=====

Different support types are available from the classes in **compas_fea.structure.displacements** including a **GeneralDisplacement** object to define all components individually, a **FixedDisplacement** object to restrain all six degrees-of-freedom to zero, and a selection of fixed and roller displacements (**FixedDisplacementXX**, **FixedDisplacementYY**, **FixedDisplacementZZ**, **RollerDisplacementX**, **RollerDisplacementY**, **RollerDisplacementZ**, **RollerDisplacementXY**, **RollerDisplacementYZ**, **RollerDisplacementXZ**) for all combinations in-between.
