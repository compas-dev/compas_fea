********************************************************************************
Sections
********************************************************************************

This page shows how **Section** objects are added to the **Structure** object, here given as ``mdl``. A variety of **Section** objects exist for 1D, 2D and 3D elements.

===============
Adding sections
===============

**Element** objects that are added to the **Structure** do not yet have a complete description of their geometry, and so must have a **Section** object associated with them. **Section** classes are first imported from module **compas_fea.structure.sections** and then objects instantiated and added to the dictionary ``.sections`` of the **Structure** object. This is done with method ``.add_section()`` with ``name`` as the string key. As the section geometry will differ for each class, the input data will vary for the different types of **Section** objects, these inputs are summarised for each section later. In the following example, the radius ``r`` and thickness ``t`` are needed for adding a **CircularSection** object and a **ShellSection** object.

.. code-block:: python

    from compas_fea.structure import CircularSection

    mdl.add_section(CircularSection(name='sec_circ', r=0.010))

.. code-block:: python

    from compas_fea.structure import ShellSection

    mdl.add_section(ShellSection(name='sec_shell', t=0.005))


====================
Geometric properties
====================

Not only will the user input data be available for viewing or editing a **Section** object, but other geometric data will also be automatically calculated, such as the area and second moments of area. The objects are accessed through ``structure.sections`` using the string key to access the **Section** object attributes,

.. code-block:: python

    >>> mdl.sections['sec_circ'].geometry
    {'r': 0.01, 'D': 0.02, 'A': 0.0003141592653, 'Ixx': 7.853981633e-09, 'Iyy': 7.853981633e-09, 'Ixy': 0}

    >>> mdl.sections['sec_circ'].__name__
    'CircularSection'


=====
Types
=====

There are a variety of 1D: **AngleSection**, **SpringSection**, **BoxSection**, **CircularSection**, **GeneralSection**, **ISection**, **PipeSection**, **RectangularSection**, **TrapezoidalSection**, **TrussSection**, 2D: **ShellSection** and 3D: **SolidSection** objects that can be imported and then objects added with the ``.add_section()`` method.

-----
Truss
-----

A **TrussSection** can take only axial forces (no shear forces or bending and torsion moments), and so only requires the cross-section area ``A``.

.. code-block:: python

    from compas_fea.structure import TrussSection

    mdl.add_section(TrussSection(name='sec_truss', A=0.0050))

---
Box
---

A hollow **BoxSection** requires the width ``b``, height ``h``, thickness of web ``tw`` and thickness of flange ``tf``.

.. code-block:: python

    from compas_fea.structure import BoxSection

    mdl.add_section(BoxSection(name='sec_box', b=0.1, h=0.2, tw=0.003, tf=0.005))

.. image:: /_images/box-ip.png
   :scale: 40 %

--------
Circular
--------

A solid **CircularSection** requires the radius ``r``.

.. code-block:: python

    from compas_fea.structure import CircularSection

    mdl.add_section(CircularSection(name='sec_circular', r=0.01))

.. image:: /_images/circ-ip.png
   :scale: 40 %

---
I
---

An **ISection** requires the width ``b``, height ``h``, thickness of web ``tw`` and thickness of flange ``tf``.

.. code-block:: python

    from compas_fea.structure import ISection

    mdl.add_section(ISection(name='sec_I', b=0.1, h=0.2, tw=0.003, tf=0.005))

.. image:: /_images/I-ip.png
   :scale: 40 %

-----
Angle
-----

An unequal **AngleSection** requires the width ``b``, height ``h`` and thickness ``t``.

.. code-block:: python

    from compas_fea.structure import AngleSection

    mdl.add_section(AngleSection(name='sec_angle', b=0.1, h=0.2, t=0.003))

.. image:: /_images/angle-ip.png
   :scale: 40 %

----
Pipe
----

A hollow **PipeSection** requires the radius ``r`` and thickness ``t``.

.. code-block:: python

    from compas_fea.structure import PipeSection

    mdl.add_section(PipeSection(name='sec_pipe', r=0.1, t=0.005))

.. image:: /_images/pipe-ip.png
   :scale: 40 %

-----------
Rectangular
-----------

A solid **RectangularSection** requires the width ``b`` and height ``h``.

.. code-block:: python

    from compas_fea.structure import RectangularSection

    mdl.add_section(RectangularSection(name='sec_rectangular', b=0.1, h=0.2))

.. image:: /_images/rect-ip.png
   :scale: 40 %

-----------
Trapezoidal
-----------

A **TrapezoidalSection** requires the base width ``b1``, top width ``b2`` and height ``h``.

.. code-block:: python

    from compas_fea.structure import TrapezoidalSection

    mdl.add_section(TrapezoidalSection(name='sec_trapezoidal', b1=0.1, b2=0.05, h=0.2))

.. image:: /_images/trap-ip.png
   :scale: 40 %

-------
General
-------

A **GeneralSection** takes explicit cross-section information: area ``A``, second moment of area about axis (ex) ``Ixx``, cross moment of area ``Ixy``, second moment of area about axis (ey) ``Iyy``, torsional rigidity ``J``, sectorial moment ``g0``, warping constant ``gw``.

------
Spring
------

A **SpringSection** can currently take only axial forces (no shear forces or bending and torsion moments). It requires either the ``stiffness``, for which a linear elastic spring will be made, or lists of ``forces`` and ``displacements`` for the definition of a non-linear spring. The ``forces`` and ``displacements`` should be given in order from negative (compression) to positive (tension).

.. code-block:: python

    from compas_fea.structure import SpringSection

    mdl.add_section(SpringSection(name='sec_elastic', stiffness=100000))

    mdl.add_section(SpringSection(name='sec_inelastic', forces=[-1000, 0, 1000], displacements=[-0.1, 0, 0.1]))

-----
Shell
-----

The area of a shell or membrane element is known from the geometry of the element through the co-ordinates of the nodes it connects to. All that is needed for the definition of a **ShellSection** is the thickness ``t``. For a **MembraneElement**, the dimensions will be used to calculate the element cross-section area for membrane forces, while a **ShellElement** will also use the geometry for shear forces, bending moments and torsional moments.

.. code-block:: python

    from compas_fea.structure import ShellSection

    mdl.add_section(ShellSection(name='sec_shell', t=0.005))

-----
Solid
-----

The volume of a solid element is known from the geometry of the element through the co-ordinates of the nodes it connects to. The creation of a **SolidSection** therefore only needs the name of the object.

.. code-block:: python

    from compas_fea.structure import SolidSection

    mdl.add_section(SolidSection(name='sec_solid'))
