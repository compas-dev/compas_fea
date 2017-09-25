********************************************************************************
Structure
********************************************************************************


The following shows some of the basics of importing and the main **Structure** object.

.. contents::


=============================
Importing modules and classes
=============================

A **.py** file is created for every compas_fea analysis, which is where a **Structure** object is first instantiated and then populated with the components needed for the particular project. To import these components and use other helper functions from the core compas or compas_fea package, ``import`` statements are needed in the first few lines of the file. For example, if the user wishes to use a CAD environment for extracting geometry or visualising analysis results, either of the following could be written to use Rhinoceros or Blender. These imports will make a variety of functions available from the **compas_fea.cad.blender** and **compas_fea.cad.rhino** modules.

.. code-block:: python

   from compas_fea.cad import rhino

.. code-block:: python

   from compas_fea.cad import blender

Similarly, depending on which finite element analysis software or library is being used, one of the following imports would be used:

.. code-block:: python

   from compas_fea.fea.abaq import abaq

.. code-block:: python

   from compas_fea.fea.ansys import ansys

.. code-block:: python

   from compas_fea.fea.opensees import opensees

It is also useful to pull modules from the core compas library, especially geometry and datastructure imports to help build the **Structure** object:

.. code-block:: python

   from compas_rhino.helpers.mesh import mesh_from_guid
   from compas.datastructures.mesh.mesh import Mesh
   from compas.geometry import distance_point_point

as well as various functions from the core compas CAD packages, for creating, editing or deleting objects and layers:

.. code-block:: python

   from compas_blender.utilities import clear_layers
   from compas_blender.helpers import network_from_bmesh

The most important imports will be for retrieving classes from the **compas_fea/structure/** folder, including the main **Structure** class itself:

.. code-block:: python

   from compas_fea.structure import GeneralStep
   from compas_fea.structure import PointLoad
   from compas_fea.structure import Structure

These special classes will be described in more detail throughout the various topics.


=====================
File and folder names
=====================

The most important files that are generated when using the compas_fea package, will be saved to folder ``path`` and with the prefix ``name``.

.. code-block:: python

   name = 'simple-truss'
   path = '/home/al/Temp/'

The above pairing will produce files such as **/home/al/Temp/simple-truss.inp** and **/home/al/Temp/simple-truss.obj**. Additional temporary files, including output **.json** data and analysis output databases such as an Abaqus **.odb** file will be stored in a separate folder within ``path`` with folder name ``name``, this is to keep things organised as an analysis will often generate hundreds of output files. These output files are explained in more detail in the Analysis topic.


================
Structure object
================

The container for all information is the **Structure** object, created from the **Structure** class. All of the attributes and methods of this class can be browsed in the source-code at **compas_fea/structure/structure.py**, with the most important methods demonstrated here-in. The following code creates an empty **Structure** object named **mdl** (used in examples as a shortcut for model). See the various topics on the left-hand-side to understand how to add all the various data and objects to the **Structure** object.

.. code-block:: python

   from compas_fea.structure import Structure

   mdl = Structure()


=======
Summary
=======

Once constructed, a top-down summary of the **Structure** object can be printed with method ``.summary()``. This will print information such as the number of nodes and elements, the name of sets and how many items in their selection, and the name and type of added objects such as **Materials**, **Sections**, **Loads**, **Displacements** and **Steps**. This summary is useful for checking that nodes, elements and objects have been added correctly before any analysis is performed.

.. code-block:: python

   >>> mdl.summary()
   --------------------------------------------------
   Structure summary
   --------------------------------------------------
   Nodes: 5
   Elements: 5
   Sets:
       nset_base : 4 node(s)
       nset_top : 1 node(s)
       elset_beams : 4 element(s)
       elset_shell : 1 element(s)
   Materials:
       mat_elastic : ElasticIsotropic
   Sections:
       sec_circ : CircularSection
       sec_shell : ShellSection
   Loads:
       load_point : PointLoad
       load_gravity : GravityLoad
   Displacements:
       disp_pinned : PinnedDisplacement
   Constraints:
   Interactions:
   Misc:
   Steps:
       step_bc : GeneralStep
       step_loads : GeneralStep
   --------------------------------------------------


==================
Loading and saving
==================

The method and function to save and load a created **Structure** object are ``.save_to_obj()`` and ``load_from_obj()`` respectively, where a filename string is given for the location of the file. This will save or load data as a pickled ``.obj`` containing all populated dictionaries and objects. A confirmation message will be displayed upon save and load.

.. code-block:: python

   >>> mdl.save_to_obj('/home/al/Temp/simple-truss.obj')
   ***** Structure saved as: /home/al/Temp/simple-truss.obj *****

   >>> from compas_fea.structure.structure import load_from_obj

   >>> mdl = load_from_obj('/home/al/Temp/simple-truss.obj')
   ***** Structure loaded from: /home/al/Temp/simple-truss.obj *****
