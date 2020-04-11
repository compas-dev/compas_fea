********************************************************************************
Installation
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _EPD: https://www.enthought.com/products/epd/

.. highlight:: bash

.. note::
Since of version ``0.1.1`` is no longer necessary to add the **compas_fea** package ``src`` folder to the **PYTHONPATH**. For previous users, it is strongly suggested to remove the package from  the **PYTHONPATH** and proceed with a clean installation following the instructions below.
:: 

Installation from source
========================

Choose a location where you want to clone the repository, open a terminal and do:

::

    $ cd <path-to-folder>/
    $ git clone https://github.com/compas-dev/compas_fea.git


Now you have the source code on your machine. To keep it up-to-date regularly pull the lastest changes by doing:

::

    $ cd <path-to-folder>/compas_fea/
    $ git pull


Released versions of :mod:`compas_fea` can be installed with *pip*.
With the desired virtual environment activated, do

::

    $ cd <path-to-folder>/compas_fea/
    $ pip install -e .


Installation from GitHub
========================

You can also install directly from the GitHub repo. Use this method if you don't plan to contribute to the package.

::

    $ pip install git+https://github.com/compas-dev/compas_fea.git


If you want to upgrade it to the latest version, do

::

    $ pip install compas-fea --upgrade


Rhino
=====

:mod:`compas_fea` is developed independent of the functionality of CAD software.
However, CAD software is still necessary in a computational design environment for visualising and interacting with datastructures, geometrical objects and visualise the results of the analysis.

In order to install :mod:`compas_3gs` for Rhino, with the desired virtual environment activated, do

::

    $ python -m compas_rhino.uninstall
    $ python -m compas_rhino.install
    $ python -m compas_rhino.install -p compas_fea

Every time a new file is opened in Rhino, be sure to reset the Python Scritp Engine before running scripts.
