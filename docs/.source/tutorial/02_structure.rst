********************************************************************************
Structure
********************************************************************************


The following shows some of the basics of importing compas_fea Classes and the main **Structure** object, as well as some of the **Structure** object's most useful methods.

.. .. contents::


=============================
Importing modules and classes
=============================

A **.py** file is generally created for every compas_fea model and analysis, which is where an empty **Structure** object is first instantiated and then populated with the components needed for the model. To import these components and use other helper functions from the core compas or compas_fea package, ``import`` statements are needed in the first few lines of the file.

For example, if the user wishes to use a CAD environment for extracting geometry or visualising analysis results, either of the following below could be written to use Rhinoceros or Blender. These imports will make a variety of functions available from the **compas_fea.cad.blender** and **compas_fea.cad.rhino** modules.

.. code-block:: python

   from compas_fea.cad import rhino

.. code-block:: python

   from compas_fea.cad import blender

It is also useful to use modules and functions from the core compas library, especially geometry and datastructure imports to help build the **Structure** object:

.. code-block:: python

   from compas_rhino.helpers import mesh_from_guid

   from compas.datastructures import Mesh

   from compas.geometry import distance_point_point

and various functions from the core compas CAD packages, for creating, editing or deleting objects and layers:

.. code-block:: python

   from compas_blender.utilities import clear_layers
   from compas_blender.utilities import delete_objects

The most important imports will be for retrieving classes from **compas_fea.structure**, including the main **Structure** class itself:

.. code-block:: python

   from compas_fea.structure import GeneralStep
   from compas_fea.structure import PointLoad
   from compas_fea.structure import Structure

These special classes make important objects for the model and will be described in more detail throughout the various topics.


================
Structure object
================

The container for all data is the **Structure** object, created from the **Structure** class. All of the attributes and methods of this class can be found at **compas_fea.structure.structure**, with the most important methods demonstrated here-in. The following code creates an empty **Structure** object named ``mdl`` (used in examples as a shortcut for model). See the various topics on the left-hand-side to understand how to add all the various data and objects to the **Structure** object.

.. code-block:: python

   from compas_fea.structure import Structure

   mdl = Structure(name='simple-truss', path='/home/al/Temp/')

The most important files that are generated when using the compas_fea package, will be saved to folder ``path`` and with the prefix ``name``. These can be passed when instantiating the **Structure** object, or by changing the attributes directly.

.. code-block:: python

    mdl.name = 'new-truss'
    mdl.path = '/home/al/Folder/'

The above pairing will produce files such as **/home/al/Folder/new-truss.inp** (Abaqus input file) and **/home/al/Folder/new-truss.obj**. Additional temporary files, including output **.json** data and analysis output databases such as an Abaqus **.odb** file will be stored in a separate folder within ``path`` with folder name ``name``, this is to keep things organised as an analysis will often generate hundreds of output files. These output files are explained in more detail in the Analysis topic.


=======
Summary
=======

Once constructed, a top-down summary of the **Structure** object can be printed with method ``.summary()`` or by printing the object e.g. ``print(mdl)``. This will print information such as the number of nodes and elements, the name of sets and how many items in their selection, and the name and type of added objects such as **Materials**, **Sections**, **Loads**, **Displacements** and **Steps**. This summary is useful for checking that nodes, elements and objects have been added correctly before any analysis is performed.

.. code-block:: python

  >>> mdl.summary()
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  compas_fea structure: simple-truss
  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

  - Number of nodes: 5

  - Number of elements: 5

  - Sets:
      nset_base : 4 node(s)
      nset_top : 1 node(s)
      elset_beams : 4 element(s)
      elset_shell : 1 element(s)

  - Materials:
      mat_elastic : ElasticIsotropic

  - Sections:
      sec_circ : CircularSection
      sec_shell : ShellSection

  - Loads:
      load_point : PointLoad
      load_gravity : GravityLoad

  - Displacements:
      disp_pinned : PinnedDisplacement

  - Constraints:
      n/a

  - Interactions:
      n/a

  - Misc:
      n/a

  - Steps:
      step_bc : GeneralStep
      step_loads : GeneralStep


==================
Loading and saving
==================

The methods to save and load a **Structure** object are ``.save_to_obj()`` and ``.load_from_obj()``. Saving the **Structure** will use the ``.path`` and ``.name`` strings for creating the file name, whilst the file name string ``fnm`` must be given for loading an existing **.obj**. These operations will save or load data as a pickled object containing all populated dictionaries and objects. A confirmation message will be displayed upon save and load.

.. code-block:: python

   >>> mdl.save_to_obj()
   ***** Structure saved to: /home/al/Temp/simple-truss.obj *****

   >>> mdl = Structure.load_from_obj(fnm='/home/al/Temp/simple-truss.obj')
   ***** Structure loaded from: /home/al/Temp/simple-truss.obj *****
