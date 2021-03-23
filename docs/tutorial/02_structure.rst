********************************************************************************
Structure
********************************************************************************

================
Structure object
================

The central container for all model and analysis data is the **Structure** object, created from the **Structure** class.
All of the attributes and methods of this class can be found at **compas_fea.structure.structure** and **compas_fea.structure.mixins**, with the most important methods demonstrated here and throughout the other topics of the tutorial. So please see the various topics on the other tutorial pages to understand how to add all the various data and objects to the **Structure** object. The following code creates an empty **Structure** object named ``mdl`` (used in all of the tutorials and examples as a short-cut handle).

.. code-block:: python

    from compas_fea.structure import Structure

    mdl = Structure(name='simple-truss', path='/home/al/Temp/')  # create an empty Structure with name and path

The files that are generated when using the **compas_fea** package will all be saved in a folder named ``path``, with many temporary files stored within this location under another folder called ``path/name``. These arguments can be passed when instantiating the **Structure** object like above, or by changing the attributes directly at a later time.

.. code-block:: python

    mdl.name = 'new-truss'  # change the name
    mdl.path = '/home/al/Folder/'  # change the path

The above pairing will later produce files such as **/home/al/Folder/new-truss.inp** (an Abaqus input file) and **/home/al/Folder/new-truss.obj** (a hard copy of the structure). Additional temporary files, including output **.json** data and analysis output databases such as an Abaqus **.odb** file will be stored in **/home/al/Folder/new-truss/**, this is to keep things organised in one folder as an analysis will often generate many output files that would clutter the ``path`` folder.


=======
Summary
=======

Once constructed, a top-down summary of the **Structure** object can be printed with the method ``.summary()`` or by printing the object with ``print(mdl)``. This will print information to the terminal such as the number of nodes and elements, the name of sets and how many items in their selection, and the name and type of added objects such as **Materials**, **Sections**, **Loads**, **Displacements** and **Steps** (all of these are described on other tutorial pages). This summary is useful for checking that nodes, elements and objects have been added correctly before any analysis is performed. If no objects of a particular type are present in that attribute of the **Structure**, then **n/a** is printed. The summary of a populated **Structure** could look like:

.. code-block:: python

    >>> mdl.summary()

    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    compas_fea Structure: truss_frame
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    Nodes
    -----
    56

    Elements
    --------
    158

    Sets
    ----
      elset_diag : Set
      elset_main : Set
      nset_load_v : Set
      elset_stays : Set
      nset_load_h : Set
      nset_pins : Set

    Materials
    ---------
      mat_steel : Steel

    Sections
    --------
      sec_diag : TrussSection
      sec_main : TrussSection
      sec_stays : TrussSection

    Loads
    -----
      load_v : PointLoad
      load_h : PointLoad
      load_gravity : GravityLoad

    Displacements
    -------------
      disp_pinned : PinnedDisplacement

    Constraints
    -----------
    n/a

    Interactions
    ------------
    n/a

    Misc
    ----
    n/a

    Steps
    -----
      step_bc : GeneralStep
      step_loads : GeneralStep


==================
Loading and saving
==================

The methods to save and load a **Structure** object are ``.save_to_obj()`` and ``.load_from_obj()``. Saving the **Structure** will use the ``.path`` and ``.name`` attribute strings for creating the file name, i.e. **/path/name.obj**. The file name string ``filename`` must be given for loading an existing **.obj**. These operations will save or load data as a pickled object using the Python ``Pickle`` module, containing all of the populated dictionaries, objects and analysis results (if any). A confirmation message will be displayed in the Python terminal upon each save and load call if the argument ``output`` is ``True``, if ``False`` then it is suppressed.

.. code-block:: bash

    >>> mdl.save_to_obj(output=True)
    ***** Structure saved to: /home/al/Temp/simple-truss.obj *****

    >>> mdl = Structure.load_from_obj(filename='/home/al/Temp/simple-truss.obj', output=True)
    ***** Structure loaded from: /home/al/Temp/simple-truss.obj *****
