********************************************************************************
Installation
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _EPD: https://www.enthought.com/products/epd/

.. highlight:: bash

.. note::
    Since version ``0.1.1``, adding the *compas_fea* package *src* folder to the *PYTHONPATH* is **no longer necessary**. For previous users, it is **strongly suggested** to remove the package from the *PYTHONPATH* and proceed with a clean installation following the instructions below.

compas_fea package
==================

You can choose either of the following two installations:

Installation from source
************************

Choose a location where you want to clone the repository, open a terminal and do:

::

    $ cd <path-to-folder>/
    $ git clone https://github.com/compas-dev/compas_fea.git


Now you have the source code on your machine. To keep it up-to-date regularly pull the lastest changes by doing:

::

    $ cd <path-to-folder>/compas_fea/
    $ git pull


Released versions of ``compas_fea`` can be installed with *pip*.
With the desired virtual (conda) environment activated, do

::

    $ cd <path-to-folder>/compas_fea/
    $ pip install -e .


Installation from GitHub
************************

You can also install directly from the GitHub repo. Use this method if you don't plan to contribute to the package.

::

    $ pip install git+https://github.com/compas-dev/compas_fea.git


If you want to upgrade it to the latest version, do

::

    $ pip install compas-fea --upgrade


CAD software
============

``compas_fea`` does not need Computer Aided Design (CAD) software to be installed and used effectively, but it is very valuable for generating and inserting geometry into the **Structure** object and for efficiently visualising results in 3D. This is useful either for a single analysis of a structural model with geometry extracted from the CAD workspace, or as part of a parametric study with many models and analyses through scripted geometry. In general, the only difference in using a specific type of CAD software, is the manner in which geometric information is taken from the CAD environment (e.g. through layers or objects) and the way that output data is then re-plotted on native geometry types. There is no difference in how objects such as loads, materials and boundary conditions are applied, as this is based on adding objects to the **Structure** through core Python scripting, making it CAD independent.

Rhinoceros
**********

Support for `Rhinoceros <http://www.rhino3d.com>`_ from Robert McNeel & Associates is based on version 6.0, for which the `IronPython <http://www.ironpython.net/>`_ distribution is standard. Please see the installation and set-up instructions for using Rhinoceros with the core `compas library <https://compas-dev.github.io/main/gettingstarted/cad/rhino.html>`_.

In order to install ``compas_fea`` for Rhino, with the desired virtual (conda) environment activated, do

::

    $ python -m compas_rhino.uninstall
    $ python -m compas_rhino.install
    $ python -m compas_rhino.install -p compas_fea

Every time a new file is opened in Rhino, be sure to reset the Python Scritp Engine before running scripts.

.. note::
    if you have a new installation of Rhino and you never used the Python editor included in Rhino, you have to open the editor at least once before running these coomands.


Blender
*******

For using ``compas_fea`` with Blender you just need to link the environment where ``compas_fea`` is installed to Blender as explained `here <https://compas-dev.github.io/main/gettingstarted/cad/blender.html>`_.


