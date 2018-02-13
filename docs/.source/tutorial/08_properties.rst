********************************************************************************
Properties
********************************************************************************

This page shows how **ElementProperties** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``. This object ties together **Element**, **Material** and **Section** objects to fully define structural elements.

=================
Adding properties
=================

To associate **Material** and **Section** objects to specific elements, an **ElementProperties** object is used. Without creating an association between these objects, the materials and sections will still exist as objects in the main **Structure** object, but are unassigned to any of the elements and so not active. The **ElementProperties** class is first imported from  module **compas_fea.structure.element_properties**, and then an object is created and added to the ``.element_properties`` dictionary of the **Structure** object. This is done using the method ``.add_element_properties()``. The arguments ``elsets`` or ``elements`` of the method can be a list of element sets or elements for assigning the properties to many similar elements. The ``material`` and ``section`` are the string names of the respective **Material** and **Section** objects to link together, while the ``name`` is the key used to store the object.

.. code-block:: python

    from compas_fea.structure import ElementProperties

    ep = ElementProperties(name='ep_circ', material='mat_elastic', section='sec_circ', elsets='elset_beams')
    mdl.add_element_properties(ep)

Giving the list ``elements`` will make an intermediate element set (effectively translating it to an ``elset``) during the file writing with name ``'elset_{element_property name}'``. This is then used as an element set for writing out the elements selection in the file writing process for OpenSees and Abaqus.

.. code-block:: python

    from compas_fea.structure import ElementProperties

    ep = Properties(name='ep_strut', material='mat_elastic', section='sec_truss', elements=[0, 1, 2])
    mdl.add_element_properties(ep)

    mdl.write_input_file(software='abaqus')

    >>> print(mdl.sets['elset_ep_strut'])
    {'selection': [0, 1, 2], 'type': 'element', 'explode': False}

**Note**: A **SpringElement** does not require a material to be defined, and can be handed ``None``. A spring will define itself through its **SpringSection**.


====================
Accessing properties
====================

At any time, the input data of an **ElementProperties** object can be viewed or manipulated as usual through the object's string key and attributes.

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

Reinforcement layers can be added to an **ElementProperties** object through dictionary ``reinforcement``. This dictionary has the keys as the name of each reinforcement layer, and the item as a dictionary with the following data: ``pos`` the float position of the reinforcement layer above or below the section's middle axis, ``spacing`` the float spacing between the reinforcing bars for that layer, ``material`` string name of the **Material** object, ``dia`` the float diameter of each bar, and ``angle`` the float angle the reinforcement layer makes with the orientation of the section's local axes. A call to the **ElementProperties** class could then look like:

.. code-block:: python

    rebar = {
        'layer_2': {'pos': -0.045, 'spacing': 0.150, 'material': 'mat_steel', 'dia': 0.010, 'angle': 90},
        'layer_1': {'pos': -0.050, 'spacing': 0.150, 'material': 'mat_steel', 'dia': 0.010, 'angle': 0}}

    ep = ElementProperties(name='ep_rc', material='mat_concrete', section='sec_concrete', elsets='elset_slab', reinforcement=rebar)
    mdl.add_element_properties(ep)

