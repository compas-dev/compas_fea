********************************************************************************
Setup
********************************************************************************

The following instructions describe the setup prerequisites for using the **compas_fea** package. Information is provided for setting-up the supported finite element software/libraries, settings required for Python, and the use of supported CAD software.

.. contents::


=====================
FE software
=====================

Abaqus
******

Most support with the **compas_fea** package is for the finite element software `Abaqus <https://www.3ds.com/products-services/simulia/products/abaqus/>`_ by `SIMULIA <https://www.3ds.com/products-services/simulia/>`_ of `Dassault Systemes <https://www.3ds.com/en-uk/>`_. Development of the **compas_fea** package has been for version 6.14 (2014) and has not been verified to work for the newer 201x releases. As this software is generally used by academia, licensing is usually through a university network academic license. Licenses that require the computer to be connected to the same network as the license server, will require the host to be connected through a Virtual Private Network (VPN) if they are off-site, through a client such as `Cisco AnyConnect <https://www.cisco.com/c/en/us/products/security/anyconnect-secure-mobility-client/index.html>`_. Abaqus should be installed as per the installation instructions for your version and licensing scheme. The Abaqus documentation does not need to be installed for the **compas_fea** package to run, but is a useful reference. On installation, Abaqus requires a temporary directory to be nominated for saving many different files during analysis, including the most important **.odb** file and various useful log files. Generally this folder will be **C:/Temp/** on Windows or **~/Temp** on Linux, but a different folder location may be defined at the start of any **compas_fea** script or through the **structure.path** attribute of the **Structure** object.

During installation, Abaqus will register its core executables to the **PATH** for Windows systems, which can be confirmed by opening the program with graphical interface by typing ``abaqus cae`` in a ``cmd`` terminal. Linux users may wish to define similar aliases manually with the following in their home **.bashrc** or **.profile** file.

.. code-block:: bash

    alias abaqus_cae="XLIB_SKIP_ARGB_VISUALS=1 /path/to/abaqus/Commands/abaqus cae -mesa"
    alias abaqus="/path/to/abaqus/Commands/abaqus"

Having these aliases set will make the use of the package easier as the Abaqus executable can be loaded conveniently, although the Abaqus executable path can also be manually given at analysis. When called for an analysis, Abaqus is run in the background as a subprocess to analyse a model.

There is no official support for Abaqus with Mac OS, and so Mac users will need to use a Virtual Machine such as `Parallels <http://www.parallels.com/>`_, `VirtualBox <https://www.virtualbox.org/>`_ or `VMWare Workstation <https://www.vmware.com/products/workstation.html>`_, and use a Windows or Linux Abaqus operating system installation (see also the Opensource section below).

ANSYS
*****

Support for ANSYS finite element software is in development.


OpenSees
**********

The Opensource finite element library `OpenSees <http://opensees.berkeley.edu/wiki/index.php/OpenSees_User>`_ by the Pacific Earthquake Engineering (PEER) Center, has cross-platform support and is in active development. The functionality and **compas_fea** implementation is current behind that of Abaqus. OpenSees is much leaner than Abaqus in terms of its file size and resources usage, which leads to a much faster analysis and results extraction.

For Windows, the needed executable files can be found on the `Download <http://opensees.berkeley.edu/OpenSees/user/download.php>`_ page for registered users (registration is free), for which the current tested version is 2.5.0. Once **Tcl** has been installed, the ``OpenSees.exe`` should ideally be saved to ``C:/OpenSees.exe`` for the **compas_fea** package to pick-up its location easily. It can be stored in a different location if preferred, but this location will need to be given as a string for each analysis.

For Linux, make sure the **Tcl** scripting language is installed on the system. The OpenSees source code may be downloaded via `SVN <http://opensees.berkeley.edu/OpenSees/developer/svn.php>`_ with build instruction at the `builds <http://opensees.berkeley.edu/OpenSees/developer/builds.php>`_ page. The download includes a variety of template ``Makefile.def`` files, which should be read carefully to set-up OpenSees for your specific system. Alternatively, OpenSees packages may already be available for your Linux distribution, such as with `archlinux <https://aur.archlinux.org/packages/opensees/>`_. The location of where the OpenSees program has been built to, will need to be given as a string for each analysis.

An OpenSees executable for Apple Machines with Intel processors running OS 10.4 or above is also available.


======
Python
======

As the **compas_fea** package uses the core **compas** framework for a variety of datastructure, visualisation and geometric tasks, the core **compas** library (``src`` folder) in addition to the **compas_fea** package (``src`` folder) must be on the **PYTHONPATH**. This can be set in Windows under **Environment Variables** in **Advanced System Settings**, and on Linux with the following addition to the **.bashrc** or **.profile** files:

.. code-block:: bash

    export PYTHONPATH='${PYTHONPATH}:/path/to/compas_framework/src/:/path/to/compas_fea/src/'

The **compas_fea** package is compatible with Python versions 2.7 and 3.5 onwards. Although any utilised finite element software may choose one version over the other for their API, the input files that are needed to run the model through this software are generated independently with the user's own independent Python version of choice.

A number of Python dependencies exists in order to use the **compas_fea** package, either as an optional or a required module or package, these are listed below. A Python distribution such as `Anaconda <http://www.anaconda.com/download/>`_ 2 or 3 for Python 2.7 and 3.x respectively, will cover all of the required module and packages and most of the optional ones. For a standalone `CPython <https://www.python.org/downloads/>`_ installation, additional modules and packages are recommended to be installed individually via ``pip install``.

Required
********

- **NumPy**: needed for efficient post-processing of output data in array format.
- **SciPy**: used for various spatial and visualisation functions and post-processing with sparse arrays.

Optional
********

- **mayavi**: utilised for standalone voxel plotting of solid elements.
- **MeshPy**: for the meshing of triangular shells (Triangle) and tetrahedron solids (TetGen).
- **PyOpenGL**: a Python OpenGL requirement for independent model viewing.
- **PySide2**: for the base visualisation application.


============
CAD software
============

The **compas_fea** package does not need CAD software to be installed to function, but it is very useful for generating and inserting geometry into the **Structure** object and for efficiently visualising results, either for a single analysis of a structural model, or as part of a parametric analysis with many models and analyses. In general, the only difference in using a specific type of CAD software, is the manner in which geometric information is taken from the CAD environment (e.g. through layers or objects) and the way that output data is then re-plotted on native geometry types. There is no difference in how objects such as loads, materials and boundary conditions are applied, as this is based on adding objects to the **Structure** through scripting, making it CAD independent.

Rhinoceros
**********

Support for `Rhinoceros <http://www.rhino3d.com>`_ from Robert McNeel & Associates is based on version 5.0, for which the `IronPython <http://www.ironpython.net/>`_ distribution is standard. Please see the installation and set-up instructions for using Rhinoceros with the core **compas** library, such as installing IronPython 2.7.5 and adding the ``Lib`` directory. The only addition for **compas_fea** compatibility is to include the **compas_fea** package ``src`` folder in the Rhinoceros equivalent **PYTHONPATH**. As for the required NumPy and SciPy packages, these will be called in subprocesses, and so the CPython distribution that has these packages, should be on the system's **PATH**.

Blender
*******

Support for the Opensource graphics software `Blender <https://www.blender.org/>`_ by the Blender Foundation is based on version 2.79, for which Python 3.6 (CPython) is standard. Blender uses its own Python paths as well as the global system or user Python paths, so the easiest step is to place the **compas_fea** package ``src`` folder on the **PYTHONPATH**, along with access to the NumPy and SciPy packages. As Blender uses CPython, subprocesses are not needed, which allows for a faster execution time for processes that would require the serialisation of large ``.json`` files, as is the case for data extraction after an analysis.
