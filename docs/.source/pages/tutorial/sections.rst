********************************************************************************
Sections
********************************************************************************


This page shows how **Section** objects are added to the **Structure** object, here given as ``mdl``.

.. contents::


===============
Adding sections
===============

Elements that are added do not have a complete description of their geometry and must have a **Section** object associated with them. **Section** classes are first imported from module **compas_fea.structure.sections** and added to the dictionary ``.sections`` of the **Structure** object with ``name`` as its string key using method ``add_section()``.  As the section geometry will differ for each class, the input data will vary, in the following example the radius ``r`` and thickness ``t`` are needed.

.. code-block:: python

   from compas_fea.structure import CircularSection

   mdl.add_section(CircularSection(name='sec_circ', r=0.010))

.. code-block:: python

   from compas_fea.structure import ShellSection

   mdl.add_section(ShellSection(name='sec_shell', t=0.005))


==========
Properties
==========

Not only will the input data be available using the string key to access the **Section** object attributes, but other geometric data will also be calculated, such as the area and second moments of area.

.. code-block:: python

   >>> mdl.sections['sec_circ'].geometry
   {'r': 0.01, 'D': 0.02, 'A': 0.0003141592653, 'I11': 7.853981633e-09, 'I22': 7.853981633e-09, 'I12': 0}


=====
Types
=====

There are a variety of 1D: **AngleSection**, **BoxSection**, **CircularSection**, **GeneralSection**, **ISection**, **PipeSection**, **RectangularSection**, **TrapezoidalSection**, **TrussSection**, 2D: **ShellSection** and 3D: **SolidSection** objects that can be added with the ``add_section()`` method.

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

A **BoxSection** requires the width ``b``, height ``h``, thickness of web ``tw`` and thickness of flange ``tf``.

.. code-block:: python

   from compas_fea.structure import BoxSection

   mdl.add_section(BoxSection(name='sec_box', b=0.1, h=0.2, tw=0.003, tf=0.005))

.. image:: /_images/box-ip.png
   :scale: 40 %

--------
Circular
--------

A **CircularSection** requires the radius ``r``.

.. code-block:: python

   from compas_fea.structure import CircularSection

   mdl.add_section(CircularSection(name='sec_circular', r=0.01))

.. image:: /_images/circ-ip.png

---
I
---

An **ISection** requires the width ``b``, height ``h``, thickness of web ``tw`` and thickness of flange ``tf``.

.. code-block:: python

   from compas_fea.structure import ISection

   mdl.add_section(ISection(name='sec_I', b=0.1, h=0.2, tw=0.003, tf=0.005))

.. image:: /_images/I-ip.png

-----
Angle
-----

An **AngleSection** requires the width ``b``, height ``h``, thickness of web ``tw`` and thickness of flange ``tf``.

.. code-block:: python

   from compas_fea.structure import AngleSection

   mdl.add_section(AngleSection(name='sec_angle', b=0.1, h=0.2, tw=0.003, tf=0.005))

.. image:: /_images/angle-ip.png

----
Pipe
----

A **PipeSection** requires the radius ``r`` and thickness ``t``.

.. code-block:: python

   from compas_fea.structure import PipeSection

   mdl.add_section(PipeSection(name='sec_pipe', r=0.1, t=0.005))

.. image:: /_images/pipe-ip.png

-----------
Rectangular
-----------

A **RectangularSection** requires the width ``b`` and height ``h``.

.. code-block:: python

   from compas_fea.structure import RectangularSection

   mdl.add_section(RectangularSection(name='sec_rectangular', b=0.1, h=0.2))

.. image:: /_images/rect-ip.png

-----------
Trapezoidal
-----------

An **TrapezoidalSection** requires the base width ``b1``, top width ``b2`` and height ``h``.

.. code-block:: python

   from compas_fea.structure import TrapezoidalSection

   mdl.add_section(TrapezoidalSection(name='sec_trapezoidal', b1=0.1, b2=0.05, h=0.2))

.. image:: /_images/trap-ip.png

-------
General
-------

A **GeneralSection** takes explicit cross-section information: area ``A``, second moment of area about axis 1-1 (ex) ``I11``, cross moment of area ``I12``, second moment of area about axis 2-2 (ey) ``I22``, torsional rigidity ``J``, sectorial moment ``g0``, warping constant ``gw``.

-----
Shell
-----

The area of a shell or membrane element is known from the geometry of the element through the co-ordinates of the nodes it connects to. All that is needed for the definition of a **ShellSection** is the thickness ``t``. For a **MembraneElement**, the dimensions will be used to calculate the element area for membrane forces, while a **ShellElement** will also use the geometry for shear forces, bending moments and torsional moments.

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
