.. _cad:

============
CAD software
============

The **compas_fea** package does not need Computer Aided Design (CAD) software to be installed and used effectively,
but it is very valuable for generating and inserting geometry into the **Structure** object and for efficiently visualising results in 3D.
This is useful either for a single analysis of a structural model with geometry extracted from the CAD workspace,
or as part of a parametric study with many models and analyses through scripted geometry.

In general, the only difference in using a specific type of CAD software, is the manner in which geometric information is taken from the CAD environment (e.g. through layers or objects) and the way that output data is then re-plotted on native geometry types.
There is no difference in how objects such as loads, materials and boundary conditions are applied,
as this is based on adding objects to the **Structure** through core Python scripting, making it CAD independent.


Rhinoceros
**********

Support for `Rhinoceros <http://www.rhino3d.com>`_ from Robert McNeel & Associates is based on version 6.0, for which the `IronPython <http://www.ironpython.net/>`_ distribution is standard.
Please see the installation and set-up instructions for using Rhinoceros with the core **compas** library.

The install **compas_fea** in Rhino, run the following commands in the Terminal (OSX) or Anaconda Prompt (Windows):

.. code-block:: bash

    conda activate name_of_your_environment
    python -m compas_rhino.install -p compas_fea


Blender
*******

Please see the installation and set-up instructions for using Blender with COMPAS.
