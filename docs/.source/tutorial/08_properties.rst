********************************************************************************
Properties
********************************************************************************


This page shows how **ElementProperties** objects are added to the **Structure** object, here given as ``mdl``.

.. .. contents::


=================
Adding properties
=================

To associate **Material** and **Section** objects to specific elements, an **ElementProperties** object is used. Without this, the materials and sections will still exist in the **Structure** object, but are unassigned and so not active. The **ElementProperties** class is first imported from  module **compas_fea.structure.element_properties** and then an object added to the ``.element_properties`` dictionary of the **Structure** object with ``name`` as the string key using method ``add_element_properties()``. The argument ``elsets`` of the method can be a list of element sets for multiple assignments of the properties, while ``material`` and ``section`` are the string names of the respective **Material** and **Section** objects to associate.

.. code-block:: python

   from compas_fea.structure import ElementProperties

   ep = ElementProperties(material='mat_elastic', section='sec_circ', elsets='elset_beams')
   mdl.add_element_properties(ep, name='ep_circ')


====================
Accessing properties
====================

The input data can be viewed or manipulated as usual through the object's string key and attributes.

.. code-block:: python

   >>> mdl.element_properties['ep_circ'].section
   'sec_circ'

   >>> mdl.element_properties['ep_circ'].material
   'mat_elastic'

   >>> mdl.element_properties['ep_circ'].elsets
   'elset_beams'
