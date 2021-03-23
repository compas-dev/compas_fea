********************************************************************************
Steps
********************************************************************************

This page shows how **Step** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``. **Step** objects are the means to instruct what is required for an analysis stage, in terms of the applied loads, displacements and parameters for the finite element solver.

============
Adding steps
============

**Step** objects are used to define the type and order of analysis stages by bringing together all of the **Displacement** and **Load** objects. In the same way that **Material** and **Section** objects require **ElementProperties** objects to be activated, **Load** and **Displacement** objects need **Step** objects to be activated, as without them they will not impose any effect on the structure. **Step** objects are created from classes in module **compas_fea.structure.step**, for which the most commonly used **GeneralStep** is shown in a simple example below. A **Step** is added to the ``.steps`` dictionary of the **Structure** object with its string key ``name``, as well as lists of the string key names of the **Load** and **Displacement** objects to apply.

.. code-block:: python

    from compas_fea.structure import GeneralStep

    mdl.add([
       GeneralStep(name='step_bc', displacements=['disp_pinned']),  # add disp_pinned to step_bc
       GeneralStep(name='step_loads', loads=['load_point', 'load_gravity'])  # add load_point load_gravity to step_loads
    ])

   mdl.set_steps_order(['step_bc', 'step_loads'])  # set the order of the Step objects

In the above example, **Step** objects with string keys ``'step_bc'`` and ``'step_loads'`` are added to the **Structure** named **mdl**, to be analysed in the order given by the list stored in ``.steps_order`` via the method ``.set_steps_order()``. That is, ``'disp_pinned'`` will be completed first in ``'step_bc'``, followed by ``'load_point'`` and ``'load_gravity'`` of ``'step_loads'``. The order of the **Step** objects can be seen at any time, and modified if needed, through:

.. code-block:: python

    >>> mdl.steps_order  # check the order Step objects will be analysed
    ['step_bc', 'step_loads']

**Note**: a boundary condition step such as ``'step_bc'`` above, should always be applied as the first step to prevent rigid body motion. Printing a **Step** object will show a summary to the terminal.

.. code-block:: python

    >>> mdl.steps['step_loads']
    GeneralStep(step_loads)

    >>> print(mdl.steps['step_loads'])

    compas_fea GeneralStep object
    ---------------------
    name          : step_loads
    increments    : 100
    iterations    : 100
    factor        : 1.0
    nlgeom        : True
    nlmat         : True
    displacements : []
    loads         : ['load_point', 'load_gravity']
    type          : static
    tolerance     : 0.01
    modify        : True


==========
Step types
==========

-----------
GeneralStep
-----------

The most general **Step** type available is the **GeneralStep** object, it requires the string ``name`` and the lists of string names of the **Load** and **Displacement** objects to apply.

.. code-block:: python

    from compas_fea.structure import GeneralStep

    mdl.add(GeneralStep(name='step_combined', displacements=['disp_bc'], loads=['load_applied']))

There are additionally other useful arguments that can be passed, which require the following explanations:

* ``increments`` (default ``100``) is the integer number of increments the analysis step can take to complete, a higher number of increments may be needed for a model that shows highly non-linear behaviour due to material and/or geometric effects. A stiff linear analysis will often use only a few or even one of these increments. If the analysis does not converge for even a high number of increments, it may mean that the structure is struggling to find equilibrium for the given applied actions. This may indicate that the structure needs to be stiffer or stronger, that the loads need to be reduced, or that there may be mechanisms or modelling problems in the structure.

* ``iterations`` (default ``100``) is the integer number of iterations that is allowed for each increment, used for some finite element solvers.

* ``tolerance`` (default ``0.01``) is a float relative tolerance used to check for convergence for some finite element solvers.

* ``factor`` (default ``1.0``) is either a float proportionality factor on the loads and displacements in the **Step**, or a dictionary that defines the factor to use on each **Load** or **Displacement**. By default, no scaling of the load and displacement components will occur. Defining a value other than unity or giving a dictionary, is useful for creating **Step** objects that represent load combinations for design code checks, without having to change the base **Load** and **Displacement** objects. For instance, factors of 1.35 and 1.50 might be applied to represent dead and live loads.

* ``nlgeom`` (default ``True``) is a boolean to toggle on or off the effects of non-linear geometry in the analysis. If the structure is relatively stiff, meaning that it does not displace significantly under the applied actions, then it is likely that the deformed geometry does not affect the internal forces and moments in any notable way. However, a coupling of large forces and deformations can lead to second order effects, which can lead to further deformations and potentially structural instability. To incorporate these and other non-linear geometric effects, keep this to ``True`` and a higher order analysis will be performed. If this is not needed, then a first order analysis with ``nlgeom=False`` can be used. **Note**: turning off ``nlgeom`` just to get the analysis to run can be misleading and dangerous, as non-convergence in a ``nlgeom=True`` analysis can be a warning signal for structural instability.

* ``type`` (default ``'static'``) the default ``'static'`` analysis type will incrementally increase the loads (and/or displacements) until equilibrium is ideally achieved for the requested load and/or displacement level. The loads in a ``'static'`` analysis are generally increased from zero, and the structure follows its load--displacement curve up until a peak load. This is performed in increments related to the tangent stiffness (gradient) at any point on the load--displacement curve. If the applied load exceeds the peak load of the structure, it cannot be in equilibrium and will fail prematurely. A monotonically increasing load controlled analysis will not give information on the post-peak load behaviour on the load--displacement curve, as loads are now decreasing. For this post-peak load information, it is required to use either a displacement controlled analysis or to change the ``type``, such as the ``'static,riks'`` in Abaqus, which is an arc-length based analysis process.

* ``modify`` (default ``True``) is a boolean that is targeted specifically at Abaqus for the ``OP`` load flag for modifying previous load components. If it is set to ``True``, then ``OP=MOD`` will be set in Abaqus.

------------
BucklingStep
------------

The **BucklingStep** object shares many of the same arguments as the **GeneralStep** object, and is used for determining buckling loads and buckling modes for structures that have prescribed loads and boundary conditions. The arguments in common with **GeneralStep** are: the step's string ``name``, the integer number of ``increments`` (default ``100``), the proportionality factor ``factor`` (default ``1.0``), and the ``loads`` and ``displacements`` lists of string object names. The **BucklingStep** is also defined by its ``type`` (default ``'buckle'``) and the number of requested buckling modes ``modes`` (default ``5``).

.. code-block:: python

    from compas_fea.structure import BucklingStep

    mdl.add(BucklingStep(name='step_buckle', displacements=['disp_bc'], loads=['load_point'], modes=10))

---------
ModalStep
---------

The **ModalStep** object shares many of the same arguments as the **BucklingStep** object, and is used for determining modal frequencies and modal shapes for structures that have prescribed boundary conditions (no loads are given). The arguments common with **BucklingStep** are: the step's string ``name``, the integer number of ``increments`` (default ``100``) and the ``displacements`` list of string object names. The **ModalStep** is also similarly defined by its ``type`` (default ``'modal'``) and the number of requested ``modes`` (default ``5``).

.. code-block:: python

    from compas_fea.structure import ModalStep

    mdl.add(ModalStep(name='step_modal', displacements=['disp_bc'], modes=10))

------------
HarmonicStep
------------

The **HarmonicStep** object shares many of the same arguments as the **GeneralStep** object. The common arguments are: the step's string ``name``, the proportionality factor ``factor`` (default ``1.0``), and the ``loads`` and ``displacements`` lists of string object names. The **HarmonicStep** is also defined by its frequency range in a list ``freq_list``, the ``damping`` (default ``None``) and the type which defaults to ``type='harmonic'``.

.. code-block:: python

    from compas_fea.structure import HarmonicStep

    mdl.add(HarmonicStep(name='step_harmonic', displacements=['disp_bc'], loads=['load_harmonic'], damping=0.03,
                         freq_list=[5, 10, 20, 30, 50, 100]))
