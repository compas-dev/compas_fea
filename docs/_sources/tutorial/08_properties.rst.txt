********************************************************************************
Properties
********************************************************************************


This page shows how **ElementProperties** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``.

.. .. contents::


=================
Adding properties
=================

To associate **Material** and **Section** objects to specific elements, an **ElementProperties** object is used. Without this association between objects, the materials and sections will still exist as objects in the main **Structure** object, but are unassigned to any elements and so not active. The **ElementProperties** class is first imported from  module **compas_fea.structure.element_properties** and then an object added to the ``.element_properties`` dictionary of the **Structure** object with ``name`` as the string key using the method ``add_element_properties()``. The arguments ``elsets`` or ``elements`` of the method can be a list of element sets or elements for multiple assignments of the properties, while ``material`` and ``section`` are the string names of the respective **Material** and **Section** objects to link.

.. code-block:: python

   from compas_fea.structure import ElementProperties

   ep = ElementProperties(material='mat_elastic', section='sec_circ', elsets='elset_beams')
   mdl.add_element_properties(ep, name='ep_circ')

Note: A **SpringElement** does not require a material to be defined, and can be handed ``None``. A spring will define itself through its **SpringSection**.


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


=============
Reinforcement
=============

Reinforcement layers can be added to an **ElementProperties** object through dictionary ``reinforcement``. This dictionary has the key as the name of each reinforcement layer, and the item as a dictionary with the following: ``pos`` the float position of the reinforcement layer above or below the section's middle, ``spacing`` the float spacing between the reinforcing bars for that layer, ``material`` string name of the **Material** object, ``dia`` the equivalent float diameter of each bar, and ``angle`` the float angle the reinforcement layer makes with the orientation of the section's local axes. A call to the **ElementProperties** class could then look like:

.. code-block:: python

    rebar = {
        'layer_2': {'pos': -0.045, 'spacing': 0.150, 'material': 'mat_steel', 'dia': 0.010, 'angle': 90},
        'layer_1': {'pos': -0.050, 'spacing': 0.150, 'material': 'mat_steel', 'dia': 0.010, 'angle': 0}}

    ep = ElementProperties(material='mat_concrete', section='sec_concrete', elsets='elset_slab', reinforcement=rebar)
    mdl.add_element_properties(ep, name='ep_reinforced_concrete')

