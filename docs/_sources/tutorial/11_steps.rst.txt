********************************************************************************
Steps
********************************************************************************


This page shows how **Step** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``.

.. contents::


============
Adding steps
============

**Step** objects are used to define the type of analysis stages by bringing together all of the **Displacement** and **Load** objects. Like with **Material** and **Section** objects requiring **ElementProperties** objects to be activated, **Load** and **Displacement** objects use **Step** objects to be activated, as without them they will not impose any effect on the structure. **Step** objects are created from classes in module **compas_fea.structure.steps** for which the most commonly used **GeneralStep** is shown below. It is added to the ``.steps`` dictionary of the **Structure** object with string keys and lists of the string key names of the **Load** and **Displacement** objects to apply.

.. code-block:: python

   from compas_fea.structure import GeneralStep

   mdl.add_step(GeneralStep(name='step_bc', displacements=['disp_pinned']))

   mdl.add_step(GeneralStep(name='step_loads', loads=['load_point', 'load_gravity']))

   mdl.set_steps_order(['step_bc', 'step_loads'])

Here, **Step** objects with string keys ``'step_bc'`` and ``'step_loads'`` are added, to be analysed in the order given by the list stored in *.steps_order*. That is, ``'disp_pinned'`` will be completed first in ``'step_bc'``, followed by ``'load_point'`` and ``'load_gravity'`` of ``'step_loads'``. The order of the **Step** objects can be seen at any time, and modified, through.

.. code-block:: python

   >>> mdl.steps_order
   ['step_bc', 'step_loads']


==========
Step types
==========

-----------
GeneralStep
-----------

The most general **Step** available is the **GeneralStep** object, it requires the string ``name`` and the lists of string names of the **Load** and **Displacement** objects to apply.

.. code-block:: python

   from compas_fea.structure import GeneralStep

   mdl.add_step(GeneralStep(name='step_combined', displacements=['disp_bc'], loads=['load_applied']))

There are additionally other useful arguments to pass which require the following explanations:

* ``increments`` (default ``200``) is the integer number of increments the analysis step can take to complete, a higher number of increments may be needed for a model that shows highly non-linear behaviour due to material and/or geometric effects. A stiff linear analysis will often use only a few or even one of these increments. If the analysis does not converge for even a high number of increments, it may mean that the structure is struggling to find equilibrium for the given applied actions. This may indicate that the structure needs to be stiffer or stronger, that the loads need to be reduced, or that there may be mechanisms or modelling problems in the structure.

* ``factor`` (default ``1.0``) is the float proportionality factor on the loads and displacements. By default, no scaling of the load and displacement components will occur. Defining a value other than unity is useful for creating **Step** objects that represent load combinations for design code checks, without having to change the base **Load** and **Displacement** objects. For instance, factors of 1.35 and 1.5 might be applied to dead and live loads.

* ``nlgeom`` (default ``True``) is a boolean to toggle on or off the effects of non-linear geometry in the analysis. If the structure is relatively stiff, meaning that it does not displace significantly under the applied actions, then it is likely that the deformed geometry does not affect significantly the internal forces and moments. However, a coupling of large forces and deformations can lead to second order effects, which can lead to further deformations and potential structural instability. To incorporate these and other non-linear geometric effects, keep this to ``True`` and a second order analysis will be performed. If this is not needed, then a first order analysis with ``nlgeom=False`` can be used. **Note**; turning off ``nlgeom`` just to get the analysis to run can be misleading and dangerous, as non-convergence in a ``nlgeom=True`` analysis can be a warning signal for local or global instability.

* ``type`` (default ``'static'``) the default ``'static'`` analysis type will incrementally increase the loads (or displacements) until equilibrium is ideally achieved for the requested load/displacement level. The loads are generally increased from zero, and the structure follows its load--displacement curve up until a peak load, in increments related to the tangent stiffness (gradient) at any point on the curve. If the applied load exceeds the peak load of the structure, it cannot be in equilibrium and will fail prematurely. A monotonically increasing load controlled analysis will not give information on the post-peak load behaviour on the load--displacement curve, as loads are now decreasing. For this post-peak load information, it is required to use either a displacement controlled analysis or to change the ``type`` to ``'static,riks'``, which is an arc-length based analysis process.

------------
BucklingStep
------------

The **BucklingStep** object shares many of the same arguments of the **GeneralStep** object, and is used for determining buckling loads and buckling shapes for structures that have prescribed loads and boundary conditions. The common arguments are, the step's string ``name``, the integer number of ``increments`` (default ``200``), the proportionality factor ``factor`` (default ``1.0``), and the ``loads`` and ``displacements`` lists of string names. The **BucklingStep** is also defined by its ``type`` (default ``'buckle'``) and the number of requested ``modes`` (default ``20``).

.. code-block:: python

   from compas_fea.structure import BucklingStep

   mdl.add_step(BucklingStep(name='step_buckle', displacements=['disp_bc'], loads=['load_point'], modes=10))

---------
ModalStep
---------

The **ModalStep** object shares many of the same arguments of the **BucklingStep** object, and is used for determining modal frequencies and modal shapes for structures that have prescribed boundary conditions. The common arguments are, the step's string ``name``, the integer number of ``increments`` (default ``200``) and the ``displacements`` list of string names. The **ModalStep** is also defined by its ``type`` (default ``'modal'``) and the number of requested ``modes`` (default ``20``).

.. code-block:: python

   from compas_fea.structure import ModalStep

   mdl.add_step(ModalStep(name='step_modal', displacements=['disp_bc'], modes=5))

------------
HarmonicStep
------------

The **HarmonicStep** object shares many of the same arguments of the **GeneralStep** object. The common arguments are, the step's string ``name``, the proportionality factor ``factor`` (default ``1.0``), and the ``loads`` and ``displacements`` lists of string names. The **HarmonicStep** is also defined by its minimum and maximum frequency range list ``freq_range``, integer number of frequency steps ``freq_steps``, the ``damping`` (default ``None``) and the default ``type='harmonic'``.

.. code-block:: python

   from compas_fea.structure import HarmonicStep

   mdl.add_step(HarmonicStep(name='step_harmonic', displacements=['disp_bc'], loads=['load_harmonic'], damping=0.03, freq_range=[5, 100], freq_steps=20))
