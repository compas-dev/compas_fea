********************************************************************************
Materials
********************************************************************************


This page shows how **Material** objects are added to the **Structure** object, here given as ``mdl``.

.. contents::


================
Adding materials
================

**Material** classes are first imported from module **compas_fea.structure.material** and added to the dictionary ``.materials`` of the **Structure** object with ``name`` as its string key and by using the method ``add_material()``. Here, a simple elastic and isotropic material is added as an example, requiring the Young's modulus, Poisson's ratio and density.

.. code-block:: python

   from compas_fea.structure import ElasticIsotropic

   mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1500))


===================
Accessing materials
===================

Data are stored and accessed through the attributes of the **Material** object and its string key. Data on any **Material** object can be changed as needed.

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

Classes exist for commonly used materials such as concrete, steel and timber, which will first assume typical design values for the material parameters, but still allow them to be changed by the user. Other classes require all material data to be provided explicitly. The following section details the available material models.

-------
Elastic
-------

The simplest material model is the elastic, isotropic and homogeneous material, called **ElasticIsotropic**. This takes the Young's modulus ``E``, Poisson's ratio ``v`` and density ``p``. Additionally, it can be stated if the material should allow ``tension`` or ``compression``, given as booleans.

.. code-block:: python

   from compas_fea.structure import ElasticIsotropic

   mdl.add_material(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1500, tension=True, compression=True))

.. image:: /_images/material-elastic.png
   :scale: 40 %

.. image:: /_images/material-elastic-no-tension.png
   :scale: 40 %

To allow only compression, set ``tension=False``.

.. image:: /_images/material-elastic-no-compression.png
   :scale: 40 %

To allow only tension, set ``compression=False``.

----------------
Elastic--plastic
----------------

The **ElasticPlastic** class can be used to make a general isotropic non-linear material object, with the same shape of stress--strain curve in both compression and tension. The elastic input data is the same as with the **ElasticIsotropic** class, given by arguments: Young's modulus ``E``, Poisson's ratio ``v`` and density ``p``. For the plastic description of the material, use lists of plastic stresses ``f`` and plastic strains ``e`` (total strain minus yield strain). The first value of ``f`` should be the stress at the end of the elastic region, i.e. the yield stress, and the first value of ``e`` should be zero, i.e. the beginning of plastic straining. Continue to give pairs of plastic stress and plastic strain to define the complete behaviour. To add the general elastic--plastic stress--strain data curve below as data to the **ElasticIsotropic** class, the input (with variables representing numbers) would look like:

.. code-block:: python

   from compas_fea.structure import ElasticPlastic

   f = [fy, f1, f2, f3]
   e = [0, e1 - ey, e2 - ey, e3 - ey]

   mdl.add_material(ElasticPlastic(name='mat_plastic', E=E, v=v, p=p, f=f, e=e))


.. image:: /_images/material-elastic-plastic.png
   :scale: 40 %

-----
Steel
-----

The following use of the **Steel** class will create an object and add it to the **Structure** named **mdl**. The string ``name`` for the material must be given, while the yield stress ``fy``, Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` will default to common values used in design if no user specific values are given. The ``type`` represents what the material behaviour is like after first yield, where ``'elastic-plastic'`` defines a perfectly flat plastic plateau after the initial linear elastic range up to ``fy``.

.. code-block:: python

   from compas_fea.structure import Steel

   mdl.add_material(Steel(name='mat_steel', fy=355, E=210*10**9, v=0.3, p=7850, type='elastic-plastic'))

.. image:: /_images/material-steel-perfect.png
   :scale: 40 %

--------
Concrete
--------

There are currently three material models for concrete, a Eurocode 2 model with class **Concrete**, a smeared crack model **ConcreteSmearedCrack**, and a damaged plasticity model **ConcreteDamagedPlasticity**. The key features of these three models are described below:

- The easiest concrete material object to create is with the **Concrete** class, which requires the characteristic (5%) 28 day cylinder strength in MPa, up to 90 MPa. Default values of the Poisson's ratio ``v=0.2`` and density ``p=2400`` are taken unless specified otherwise. As per Eurocode 2 Part 1-1 (particularly Table 3.1), key material data is derived from knowing the characteristic cylinder strength ``fck``. The **Concrete** model includes: 1) the compressive stress--strain model of Clause 3.1.5, 2) the mean Young's modulus, tensile and compressive stresses from Table 3.1, and 3) will assume a linear elastic response until the tensile cracking stress, followed by a drop to zero tensile stress at 0.1 % strain.

.. code-block:: python

   from compas_fea.structure import Concrete

   mdl.add_material(Concrete(name='mat_concrete', fck=90))

.. image:: /_images/concrete_f-e.png
   :scale: 40 %

- The **ConcreteSmearedCrack** class (based on the Abaqus smeared crack material) creates a more general concrete material model object. Cracks are smeared across cracking areas, not individually modelled. The Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` are all explicitly given, as no defaults are assumed. The compressive stress--strain data are given with (positive) plastic stresses ``fc`` in Pascals and (positive) plastic strains ``ec`` in exactly the same way as **ElasticPlastic**. The first value of ``fc`` is the stress at the end of the elastic region defined by slope ``E``, paired with the first value of ``ec`` of zero. For the tensile stresses, tension stiffening uses ``ft`` and ``et``, where ``ft`` are not the absolute values of tensile stress, but the relative tensile stress from the point of cracking. So the first data pairs are ``ft`` as 1 at ``et`` of 0, then dropping to ``ft`` as 0 at another value of ``et`` (0.001 recommended). Before cracking, the tensile stress--strain behaviour is linear, using the same Young's modulus ``E`` as for compression. Finally, the failure ratios ``fr`` are given, which are the ratio of the ultimate bi-axial to uni-axial compressive ultimate stress (default 1.16) and the ratio of uni-axial tensile to compressive stress at failure (default 0.0836), the latter will give a tensile failure stress of 35 * 0.0836 = 2.926 if the concrete maximum compressive stress is 35 MPa. To add the general concrete stress--strain data curve below as data to the **ConcreteSmearedCrack** class, the input (with variables representing numbers, and the cracking stress as 10% of peak stress f3) would look like:

.. code-block:: python

   from compas_fea.structure import ConcreteSmearedCrack

   fc = [fy, f1, f2, f3]
   ec = [0, e1 - ey, e2 - ey, e3 - ey]
   ft = [1, 0]
   et = [0, etu]
   fr = fr=[1.16, 0.10]

   mdl.add_material(ConcreteSmearedCrack(name='mat_concrete', E, v, p, fc, ec, ft, et, fr))

.. image:: /_images/smeared-crack.png
   :scale: 40 %

- The **ConcreteDamagedPlasticity** material model is used for concrete and other quasi-brittle materials (and is based here and quoted from the Abaqus damaged plasticity material). The class takes the Young's modulus ``E``, Poisson's ratio ``v`` and density ``p`` as no defaults are assumed, as well as lists ``damage``, ``hardening`` and ``stiffening``. For ``damage``, a list is given of: the dilation angle in degrees, flow potential eccentricity, the ratio of initial equibiaxial to uni-axial compressive yield stress, the ratio of the second stress invariant on the tensile meridian to that on the compressive meridian, and the viscosity parameter.. For the input ``hardening``, a list is given of: the compressive yield stress, inelastic crushing strain, inelastic crushing strain rate, and  temperature. Finally, for ``stiffening``, a list of: remaining direct stress after cracking, direct cracking strain, direct cracking strain rate, and temperature.
