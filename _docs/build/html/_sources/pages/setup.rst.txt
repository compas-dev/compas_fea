********************************************************************************
Setup
********************************************************************************

The following instructions describe the prerequisites for using the compas_fea package.

.. contents::


=====================
FE software
=====================

Abaqus
******

Most support with the compas_fea package is for the finite element software Abaqus by Simulia. Development has been for version 6.14 and has not been verified to work for the newer 201x releases. As this software is generally used by academia, licensing is usually through a university network academic license, or a lighter student license. be aware that a student license may contain a restriction on the number of nodes that the model may contain, and so heavy models with many shell or solid elements may surpass this limit and not execute. Licenses that require the computer to be connected to the same network as the license server, will require the host to be connected through a Virtual Private Network (VPN) through a client such as `Cisco AnyConnect <https://www.cisco.com/c/en/us/products/security/anyconnect-secure-mobility-client/index.html>`_.

Abaqus should be installed as per the installation instructions for your version. The Abaqus documentation is not needed for the compas_fea package to run, but is a useful reference. On installation, Abaqus requires a temporary directory to be nominated for saving many different files during analysis, including the most important **.odb** file and various useful log files. Generally this folder will be **C:/Temp/** on Windows or **~/Temp** on Linux, but a different folder location may be defined at the start of any compas_fea script. Abaqus will also register its core executables to the **PATH** for Windows systems, which can be confirmed by opening the program by typing ``abaqus cae`` in a ``cmd`` terminal. Linux users may wish to define similar aliases manually with the following in their **.bashrc** or **.profile** file.

.. code-block:: bash

    alias abaqus_cae="XLIB_SKIP_ARGB_VISUALS=1 /path/to/abaqus/Commands/abaqus cae -mesa"
    alias abaqus="/path/to/abaqus/Commands/abaqus"

Having these aliases set will make the use of the package easier, although the Abaqus executable can be manually given at analysis. When called for an analysis, the Abaqus executable is run in the background as a subprocess to analyse a model. There is no official support for Abaqus with Mac OS, Mac users will need to use a Virtual Machine such as `Parallels <http://www.parallels.com/>`_, `VirtualBox <https://www.virtualbox.org/>`_ or `VMWare Workstation <https://www.vmware.com/products/workstation.html>`_, and use a Windows or Linux Abaqus operating system installation (see also the Opensource section below).

ANSYS
*****

Support for ANSYS finite element software is in development.

Opensource
**********

Support for opensource finite element libraries is currently in development and will be an important part of the compas_fea package. The first opensource finite element library support will be for `OpenSees <http://opensees.berkeley.edu/OpenSees/manuals/usermanual/index.html>`_ by the Pacific Earthquake Engineering (PEER) Center, due to, amongst other things, its cross-platform support.


======
Python
======

As the compas_fea package uses the core compas framework for a variety of datastructure, visualisation and geometric tasks, the core compas library must be on the **PYTHONPATH**. This can be set in Windows under Environment Variables in Advanced System Settings, and on Linux with the following additions to the **.bashrc** or **.profile** files:

.. code-block:: bash

    export PYTHONPATH=${PYTHONPATH}:/path/to/compas_framework/src/

The compas_fea package is compatible with Python versions 2.x and 3.x, and although the target finite element software may utilise one version or the other for their API, the input files that are needed to run the model through this software are generated independently.

A number of Python dependencies exists in order to use the compas_fea package, either as an optional or a required module or package, these are listed below. A Python distribution such as `Anaconda <http://www.anaconda.com/download/>`_ 2 or 3, will generally cover all of the required module and packages and most optional ones. For a standalone `CPython <https://www.python.org/downloads/>`_ installation, additional modules and packages are recommended to be installed via ``pip``.

Required modules
****************

- **NumPy**: needed for efficient post-processing of output data.
- **SciPy**: used for various 4D (voxel) visualisation functions and post-processing sparse arrays.

Optional modules
****************

- **mayavi**: utilised for standalone voxel plotting of solid elements.
- **MeshPy**: for the meshing of triangular shells (Triangle) and tetrahedron solids (TetGen).
- **PyOpenGL**: a Python OpenGL requirement for the core compas Viewer.
- **PySide**: for the base visualisation App.


============
CAD software
============

The compas_fea package does not need CAD software to be installed to function, but it is very useful for generating and inserting geometry into the **Structure** object and for efficiently visualising results, either for a single analysis of a structural model, or as part of a parametric analysis with many cycles or analyses. In general, the only difference in using a specific type of CAD software, is the manner in which geometric information is taken from the CAD environment (e.g. through layers or objects) and the way that output data is then re-plotted on this geometry. There is no difference in how objects such as loads, materials and boundary conditions are applied, as this is based on adding objects through scripting.

Rhinoceros
**********

Support for `Rhinoceros <http://www.rhino3d.com>`_ from Robert McNeel & Associates is based on version 5.0, for which `IronPython <http://www.ironpython.net/>`_ is standard. Please see the installation and set-up instructions for using Rhinoceros with the core compas library, as the only addition for compas_fea compatibility is to include the compas_fea package in the **PYTHONPATH**.

Blender
*******

Support for the opensource graphics software `Blender <https://www.blender.org/>`_ by the Blender Foundation is based on version 2.78, for which Python 3.6 (CPython) is standard. The compas_fea package must again be on the **PYTHONPATH** to work.
