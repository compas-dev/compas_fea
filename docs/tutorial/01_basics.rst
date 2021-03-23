********************************************************************************
Basics
********************************************************************************

The following page shows some of the fundamentals of importing **compas_fea** classes and how to use the main **Structure** object, including some of the **Structure** object's most important high level methods and attributes.

=============================
Importing modules and classes
=============================

A Python **.py** file is created for every **compas_fea** model and analysis, which is where an empty **Structure** object is first instantiated and then populated with the components needed for the model. To import these components and to also use other helper functions from the core **compas** or **compas_fea** packages, ``import`` statements are needed in the first few lines of the Python file. For example, if the user wishes to use a CAD environment for extracting geometry or visualising analysis results, either of the following lines below could be written to use Rhinoceros or Blender.
These imports will make a variety of functions available from the **compas_fea.cad.blender** and **compas_fea.cad.rhino** modules.

.. code-block:: python

    from compas_fea.cad import rhino  # import Rhinoceros support


.. code-block:: python

    from compas_fea.cad import blender  # import Blender support


It is useful to use packages, modules and functions from the core **compas** library, especially **compas.geometry** and **compas.datastructure** imports to help build the **Structure** object.
Such imports will be seen in a variety of the example models to construct the **Structure**.

.. code-block:: python

    from compas.datastructures import Mesh  # make the compas Mesh datastructure available
    from compas.geometry import distance_point_point  # function to measure distances between two points


There are also many functions from the core **compas** CAD packages that can be helpful for creating, editing or deleting objects and layers in the CAD workspace:

.. code-block:: python

    from compas_blender.utilities import clear_layers  # clear all objects from a given layer
    from compas_blender.utilities import delete_objects  # delete specific objects from the scene


The most important imports will be for retrieving classes from **compas_fea.structure**, including the main **Structure** class itself. Imports, like with the main **compas** library, are always available from the second level, with embedded modules on the third level onwards, pulled up to the second level to enable this. This is particularly useful for all of the classes found in **compas_fea.structure**, as you do not need to know the package structure beyond this level. The special classes in **compas_fea.structure** are used to make important objects for the model and will be described in more detail throughout the various tutorial topics.
Below are three imports that bring in the **GeneralStep**, **PointLoad** and **Structure** classes.

.. code-block:: python

    from compas_fea.structure import GeneralStep
    from compas_fea.structure import PointLoad
    from compas_fea.structure import Structure


Bringing all of the import considerations together, the top of the **.py** file might look something like:

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
