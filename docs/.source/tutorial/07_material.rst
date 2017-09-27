********************************************************************************
Materials
********************************************************************************


This page shows how **Material** objects are added to the **Structure** object, here given as ``mdl``.

.. .. contents::


================
Adding materials
================

**Material** classes are first imported from module **compas_fea.structure.materials** and added to the dictionary ``.materials`` of the **Structure** object with ``name`` as its string key using method ``add_material()``. Here, a simple elastic isotropic material is added, requiring the Young's modulus, Poisson's ratio and density.

.. code-block:: python

   from compas_fea.structure import ElasticIsotropic

   mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1500))


===================
Accessing materials
===================

Data are stored and accessed through the attributes of the **Material** object and its string key.

.. code-block:: python

   >>> mdl.materials['mat_elastic'].E
   {'E': 10000000000}

   >>> mdl.materials['mat_elastic'].v
   {'v': 0.3}

   >>> mdl.materials['mat_elastic'].p
   1500


=========
Materials
=========

Classes exist for commonly used materials such as concrete, steel and timber, and will first assume typical values for material parameters, but still allow them to be changed if they should differ. Other classes require all material data to be provided explicitly, used when the standard **Material** classes cannot be used. The following sections detail some of the material models.

----------------
Elastic--plastic
----------------

The **ElasticPlastic** class can be used to make a general isotropic non-linear material object, with the same shape of stress--strain curve in both compression and tension. The elastic input is the same as with the **ElasticIsotropic** class, given by arguments: Young's modulus ``E``, Poisson's ratio ``v`` and density ``p``. For the plastic description of the material, use lists of plastic stresses ``f`` and plastic strains ``e`` (total strain minus yield strain). The first value of ``f`` should be the stress at the end of the elastic region, i.e. the yield stress, and the first value of ``e`` should be zero, i.e. the beginning of plastic straining. Continue to give pairs of plastic stress and plastic strain to define the complete behaviour.

.. code-block:: python

   from compas_fea.structure import ElasticPlastic

   f = [50000, 90000, 120000, 140000, 160000, 180000, 190000, 200000, 210000, 220000]
   e = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

   mdl.add_material(ElasticPlastic(name='mat_plastic', E=5*10**6, v=0.30, p=350, f=f, e=e))

-----
Steel
-----

The following use of the **Steel** class will create an object and add it to **mdl**. The string ``name`` for the material must be given, while the yield stress ``fy``, Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` will default to common values used in design if no user specific values are given. The ``type`` represents what the material behaviour is like after first yield, where ``'elastic-plastic'`` defines a perfectly flat plastic plateau after the initial linear elastic range up to ``fy``.

.. code-block:: python

   from compas_fea.structure import Steel

   mdl.add_material(Steel(name='mat_steel', fy=355, E=210*10**9, v=0.3, p=7850, type='elastic-plastic'))

--------
Concrete
--------

There are currently three material models for concrete, a Eurocode 2 model **Concrete**, a smeared crack model **ConcreteSmearedCrack**, and a damaged plasticity model **ConcreteDamagedPlasticity**. The key features of these three models are described below:

- The easiest concrete material object to add is with the **Concrete** class, which requires the characteristic (5%) 28 day cylinder strength in MPa, up to 90 MPa. Default values of the Poisson's ratio ``v=0.2`` and density ``p=2400`` are taken unless specified otherwise. As per Eurocode 2 Part 1-1 (particularly Table 3.1), key material data is derived from knowing the characteristic cylinder strength ``fck``. The model includes: the compressive stress--strain model of Clause 3.1.5 (Figure 3.2 below), the mean Young's modulus, tensile and compressive stresses from Table 3.1, and will assume a linear elastic response until the tensile cracking stress, followed by a drop to zero tensile stress at 0.1 % strain.

.. code-block:: python

   from compas_fea.structure import Concrete

   mdl.add_material(Concrete(name='mat_concrete', fck=90))

.. image:: /_images/concrete_f-e.png
   :scale: 60 %

- The **ConcreteSmearedCrack** class (based on the Abaqus smeared crack material, see figure below) creates a more general concrete material model object. Cracks are smeared across cracking areas, and not individually modelled. The Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` are all explicitly given, as no defaults are assumed. The compressive stress--strain data are given with plastic stresses ``fc`` in Pascals and plastic strains ``ec``. The first value of ``fc`` is the stress at the end of the elastic region defined by slope ``E``, paired with the first value of ``ec`` of zero. Tension stiffening uses plastic stresses ``fc`` and plastic strains ``et``, where ``ft`` is now not the absolute value of tensile stress in Pa, but the relative tensile stress from the point of cracking. So the first data pairs are ``ft`` as 1 at ``et`` of 0, then dropping to ``ft`` as 0 at another value of ``et`` (0.001 recommended). Before cracking, the tensile stress--strain behaviour is linear, using the same Young's modulus ``E`` as for compression. Finally, the failure ratios ``fr`` are given, which are the ratio of the ultimate bi-axial to uni-axial compressive ultimate stress (default 1.16) and the ratio of uni-axial tensile to compressive stress at failure (default 0.0836), the latter will give a tensile failure stress of 35 * 0.0836 = 2.926 if the concrete fails in compression at 35 MPa.

.. code-block:: python

   from compas_fea.structure import ConcreteSmearedCrack

   E = 40 * 10**9
   v = 0.2
   p = 2400
   fc = [10 * 10**6, 20 * 10**6, 35 * 10**6]
   ec = [0, 0.0020, 0.0035]
   ft = [1, 0]
   et = [0, 0.001]
   fr = fr=[1.16, 0.0836]

   mdl.add_material(ConcreteSmearedCrack(name='mat_concrete', E, v, p, fc, ec, ft, et, fr))

.. image:: /_images/concrete-smeared.png
   :scale: 70 %

- The **ConcreteDamagedPlasticity** material model is used for concrete and other quasi-brittle materials (and is based here and quoted from the Abaqus damaged plasticity material). The class takes the Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` as no defaults are assumed, as well as lists ``damage``, ``hardening`` and ``stiffening``. For ``damage``, a list is given of: the dilation angle in degrees, flow potential eccentricity, the ratio of initial equibiaxial to uni-axial compressive yield stress, the ratio of the second stress invariant on the tensile meridian to that on the compressive meridian, and the viscosity parameter.. For the input ``hardening``, a list is given of: the compressive yield stress, inelastic crushing strain, inelastic crushing strain rate, and  temperature. Finally, for ``stiffening``, a list of: remaining direct stress after cracking, direct cracking strain, direct cracking strain rate, and temperature.
