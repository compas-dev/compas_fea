********************************************************************************
Properties
********************************************************************************

This page shows how **ElementProperties** objects are added to the **Structure** object, here given as a **Structure** named ``mdl``. This type of object ties together **Element**, **Material** and **Section** objects to fully define structural elements.

=================
Adding properties
=================

To associate **Material** and **Section** objects to specific elements, an **ElementProperties** object is used. Without creating an association between these objects, the materials and sections will exist as objects in the main **Structure** object, but they will be unassigned to any of the structure's elements. The **ElementProperties** class is first imported from  module **compas_fea.structure.element_properties**, and then an object is created and added to the ``.element_properties`` dictionary of the **Structure** object with method ``.add()``. The argument ``elset`` or ``elements`` can be an element set string name or a list of elements for assigning the properties to many similar elements (either ``elements`` or ``elset`` should be given, not both.). The ``material`` and ``section`` arguments are the string names of the respective **Material** and **Section** objects to link together, while the ``name`` is the key used to store and represent the **ElementProperties** object.

.. code-block:: python

    from compas_fea.structure import ElementProperties as Properties

    mdl.add(Properties(name='ep_circ', material='mat_elastic', section='sec_circ', elset='elset_beams'))

**Note**: A **SpringElement** does not require a material to be defined, and is handed ``None`` by default. A spring will define itself through its **SpringSection** and the elements it is linked to.


================================
Accessing and editing properties
================================

At any time, the input data of an **ElementProperties** object can be viewed or manipulated as usual through the object's string key and attributes, and also by printing the object to the terminal.

.. code-block:: python

    >>> mdl.element_properties['ep_circ']  # ElementProperties object `ep_circ`
    ElementProperties(ep_circ)

    >>> print(mdl.element_properties['ep_circ'])  # print a summary


    compas_fea ElementProperties object
    -----------------------------------
    name          : ep_circ
    material      : mat_elastic
    section       : sec_circ
    elset         : elset_beams
    elements      : None
    rebar         : {}

    >>> mdl.element_properties['ep_circ'].section  # view section attribute
    'sec_circ'

    >>> mdl.element_properties['ep_circ'].material  # view material attribute
    'mat_elastic'

    >>> mdl.element_properties['ep_circ'].elset  # view associated element set
    'elset_beams'


=============
Reinforcement
=============

Reinforcement layers for shell and membrane elements can be added to an **ElementProperties** object through the dictionary ``rebar``. This dictionary has the keys as the name of each reinforcement layer, and the item as a dictionary with the following data: ``pos`` the float position of the reinforcement layer above or below the section's middle axis, ``spacing`` the float spacing between the reinforcing bars for that layer, ``material`` string name of the **Material** object, ``dia`` the float diameter of each bar, and ``angle`` the float angle the reinforcement layer makes with the orientation of the section's local axes. A call to the **ElementProperties** class could then look like:

.. code-block:: python

    rebar = {
        'layer_2': {'pos': -0.045, 'spacing': 0.150, 'material': 'steel', 'dia': 0.010, 'angle': 90},
        'layer_1': {'pos': -0.050, 'spacing': 0.150, 'material': 'steel', 'dia': 0.010, 'angle': 0},
    }

    mdl.add(ElementProperties(name='ep_rc', material='concrete', section='shell', elset='slab', rebar=rebar))
