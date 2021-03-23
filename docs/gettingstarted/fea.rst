.. _fea:

***********
FE software
***********

``compas_fea`` use FEA Software in the background to run the analyses.
Currently the following backends are supported to various degrees:

* Abaqus: ...
* ANSYS: ...
* OpenSEES: ...

Abaqus
======

Most support with the **compas_fea** package is for the finite element software `Abaqus <https://www.3ds.com/products-services/simulia/products/abaqus/>`_ by `SIMULIA <https://www.3ds.com/products-services/simulia/>`_ of `Dassault Systemes <https://www.3ds.com/en-uk/>`_. Development of the **compas_fea** package has been for version 6.14 (2014) and has not yet been verified to work for the newer 201x releases. As this software is generally used by academia, licensing is usually through a university network academic license. Licenses that require the computer to be connected to the same network as the license server will require the host to be connected through a Virtual Private Network (VPN) if they are off-site, through a client such as `Cisco AnyConnect <https://www.cisco.com/c/en/us/products/security/anyconnect-secure-mobility-client/index.html>`_ or `OpenVPN <https://openvpn.net/get-open-vpn/>`_. The Abaqus documentation does not need to be installed for the **compas_fea** package to run, but is a useful reference. On installation, Abaqus requires a temporary directory to be nominated for saving many different files during analysis, including the most important output database **.odb** file and various useful log files. Generally this folder will be **C:/Temp/** on Windows or **~/Temp** on Linux, but a different folder location may be defined at the start of any **compas_fea** script or through the **structure.path** attribute of the **Structure** object (this is described later).

During installation, Abaqus will register its core executables to the **PATH** for Windows systems, which can be confirmed by opening the program with its graphical interface by typing ``abaqus cae`` in a ``cmd`` terminal. Linux users may wish to define similar aliases manually with the following in their home **.bashrc** or **.profile** files.

.. code-block:: bash

    alias abaqus_cae="XLIB_SKIP_ARGB_VISUALS=1 /path/to/abaqus/Commands/abaqus cae -mesa"
    alias abaqus="/path/to/abaqus/Commands/abaqus"

Having these aliases set will make the use of the **compas_fea** package easier as the Abaqus executable can be loaded conveniently, although the Abaqus executable path can also be manually given at the time of analysis. When called for an analysis, Abaqus is run in the background as a sub-process to analyse a model, with feedback presented to the user in the active terminal.

There is no official support for Abaqus with MacOS, and so Mac users will need to use a Virtual Machine such as `Parallels <http://www.parallels.com/>`_, `VirtualBox <https://www.virtualbox.org/>`_ or `VMWare Workstation <https://www.vmware.com/products/workstation.html>`_, and use a Windows or Linux operating system.


ANSYS
=====

Support for ANSYS finite element software is in development and is currently only available for Windows.
To be able to use ANSYS as a backend, make sure it is available on the ``PATH`` variable.

.. code-block:: bash

    "C:\Program Files\ANSYS Inc\v195\ansys\bin\winx64"


OpenSees
========

The open-source finite element library `OpenSees <http://opensees.berkeley.edu/wiki/index.php/OpenSees_User>`_ by the Pacific Earthquake Engineering (PEER) Centre, has cross-platform support and is in active development. The functionality is current behind that of Abaqus but growing (please contact us if you would like to contribute). OpenSees is much leaner than larger software such as Abaqus and Ansys in terms of its file size and resources usage, which leads to a much faster analysis and results extraction time, but has generally much less functionality.

For Windows, the necessary executable files for installation and running OpenSees can be found on the official `Download <http://opensees.berkeley.edu/OpenSees/user/download.php>`_ page for registered users (registration is free), for which the current tested version is 3.0.3. Once the required **Tcl** programming language has been installed, the ``OpenSees.exe`` should ideally be saved to ``C:/OpenSees.exe`` for the **compas_fea** package to pick-up its location easily. It can be stored in a different location if preferred, but this location will need to be given for each analysis so that **compas_fea** knows where to look.

For Linux variants, make sure the **Tcl** programming language is installed on the system, this is often the case by default. The OpenSees source code may be downloaded via `here <http://opensees.berkeley.edu/OpenSees/developer/svn.php>`_ with build instruction at the `builds <http://opensees.berkeley.edu/OpenSees/developer/builds.php>`_ page. The download includes a variety of template ``Makefile.def`` files, which should be read carefully to set-up OpenSees for your specific system. Alternatively, OpenSees packages may already be available for your Linux distribution through its default package manager, such as with `archlinux <https://aur.archlinux.org/packages/opensees/>`_. The location of where the OpenSees program has been built to, will need to be given for each analysis, a suggested location would be ``~/opensees/``.

An OpenSees executable for Apple Machines with Intel processors running OS 10.4 or above is also available, making OpenSees the only currently supported FE solver for Mac computers.

