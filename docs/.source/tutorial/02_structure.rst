********************************************************************************
Structure
********************************************************************************

The following page shows some of the fundamentals of importing **compas_fea** classes and usage of the main **Structure** object, including some of the **Structure** object's most useful methods and important attributes.

=============================
Importing modules and classes
=============================

A Python **.py** file is generally created for every **compas_fea** model and analysis, which is where an empty **Structure** object is first instantiated and then populated with the components needed for the model. To import these components and use other helper functions from the core **compas** or **compas_fea** package, ``import`` statements are needed in the first few lines of the file. For example, if the user wishes to use a CAD environment for extracting geometry or visualising analysis results, either of the following lines below could be written to use Rhinoceros or Blender. These imports will make a variety of functions available from the **compas_fea.cad.blender** and **compas_fea.cad.rhino** modules.

.. code-block:: python

    from compas_fea.cad import rhino

.. code-block:: python

    from compas_fea.cad import blender

It is useful to use packages, modules and functions from the core **compas** library, especially **compas.geometry** and **compas.datastructure** imports to help build the **Structure** object:

.. code-block:: python

    from compas_rhino.helpers import mesh_from_guid

    from compas.datastructures import Mesh

    from compas.geometry import distance_point_point

There are also many functions from the core **compas** CAD packages that can be helpful for creating, editing or deleting objects and layers:

.. code-block:: python

    from compas_blender.utilities import clear_layers
    from compas_blender.utilities import delete_objects

The most important imports will be for retrieving classes from **compas_fea.structure**, including the main **Structure** class itself. Imports, like with the main **compas** library, are from the second level, with embedded modules pulled up to this level. This is particularly useful for all of the classes found in **compas_fea.structure**. These special classes make important objects for the model and will be described in more detail throughout the various tutorial topics.

.. code-block:: python

    from compas_fea.structure import GeneralStep
    from compas_fea.structure import PointLoad
    from compas_fea.structure import Structure

The top of the **.py** file might look something like:

.. code-block:: python

    from compas.datastructures import Mesh

    from compas.geometry import distance_point_point

    from compas_rhino.helpers import mesh_from_guid

    from compas_fea.cad import rhino

    from compas_fea.structure import BucklingStep
    from compas_fea.structure import Concrete
    from compas_fea.structure import ElementProperties as Properties
    from compas_fea.structure import GeneralStep
    from compas_fea.structure import GravityLoad
    from compas_fea.structure import PointLoad
    from compas_fea.structure import RectangularSection
    from compas_fea.structure import RollerDisplacementY
    from compas_fea.structure import ShellSection
    from compas_fea.structure import Steel
    from compas_fea.structure import Structure
    from compas_fea.structure import TrussSection


================
Structure object
================

The container for all model and analysis data is the **Structure** object, created from the **Structure** class. All of the attributes and methods of this class can be found at **compas_fea.structure.structure**, with the most important methods demonstrated here and through the other topics of the tutorial. See the various topics on the left-hand-side to understand how to add all the various data and objects to the **Structure** object. The following code creates an empty **Structure** object named ``mdl`` (used in the tutorial and examples as a short-cut).

.. code-block:: python

    from compas_fea.structure import Structure

    mdl = Structure(name='simple-truss', path='/home/al/Temp/')

The files that are generated when using the **compas_fea** package, will all be saved in a folder named ``path``, with many temporary files stored within this location under another folder called ``path/name``. These can be passed when instantiating the **Structure** object like above, or by changing the attributes directly at a later time.

.. code-block:: python

    mdl.name = 'new-truss'
    mdl.path = '/home/al/Folder/'

The above pairing will produce files such as **/home/al/Folder/new-truss.inp** (an Abaqus input file) and **/home/al/Folder/new-truss.obj**. Additional temporary files, including output **.json** data and analysis output databases such as an Abaqus **.odb** file will be stored in **/home/al/Folder/new-truss/**, this is to keep things organised as an analysis will often generate hundreds of output files.


=======
Summary
=======

Once constructed, a top-down summary of the **Structure** object can be printed with method ``.summary()`` or by printing the object ``print(mdl)``. This will print information to the terminal such as the number of nodes and elements, the name of sets and how many items in their selection, and the name and type of added objects such as **Materials**, **Sections**, **Loads**, **Displacements** and **Steps**. This summary is useful for checking that nodes, elements and objects have been added correctly before any analysis is performed. If no objects of a particular type are present in that attribute of the **Structure**, then **n/a** is printed.

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
      elset_diag : 105 element(s)
      elset_main : 51 element(s)
      nset_load_v : 6 node(s)
      elset_stays : 2 element(s)
      nset_load_h : 2 node(s)
      nset_pins : 8 node(s)

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
      load_pl_h : PointLoad
      load_pl_v : PointLoad
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

The methods to save and load a **Structure** object are ``.save_to_obj()`` and ``.load_from_obj()``. Saving the **Structure** will use the ``.path`` and ``.name`` attribute strings for creating the file name, whilst the file name string ``filename`` must be given for loading an existing **.obj**. These operations will save or load data as a pickled object using Pickle, containing all populated dictionaries and objects. A confirmation message will be displayed upon each save and load call.

.. code-block:: python

    >>> mdl.save_to_obj()
    ***** Structure saved to: /home/al/Temp/simple-truss.obj *****

    >>> mdl = Structure.load_from_obj(filename='/home/al/Temp/simple-truss.obj')
    ***** Structure loaded from: /home/al/Temp/simple-truss.obj *****
