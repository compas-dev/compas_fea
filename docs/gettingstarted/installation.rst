********************************************************************************
Installation
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _EPD: https://www.enthought.com/products/epd/


To use ``compas_fea`` you need to install COMPAS,
and have at least on of the supported analysis backends available on your system.
Currently, ``compas_fea`` supports Abaqus, ANSYS, and OpenSEES to various degrees.
See :ref:`fea` for more detailed information.
For instructions about using ``compas_fea`` in CAD software, see :ref:`cad`.

By installing COMPAS all required Python packages for ``compas_fea`` will be installed as well.
To install COMPAS, see the `Getting Started <https://compas-dev.github.io/main/gettingstarted.html>`_ instructions in the COMPAS docs.

``compas_fea`` itself can be installed using ``pip`` from a local source repo, or directly from GitHub.


.. note::

    Make sure to install ``compas_fea`` in the same environment as COMPAS!


From Local Source
=================

To install from a local source repo, clone the repo onto your computer using your Favourite Git client,
or using the command line.

Then navigate to the root of the ``compas_fea`` repo and install using pip:

.. code-block:: bash

    cd compas_fea
    pip install -e .


From GitHub
===========

To install directly from the GitHub repo, just do

.. code-block:: bash

    $ pip install git+https://github.com/compas-dev/compas_fea.git#egg=compas_fea


Verify
======

To check the installation, open an interactive Python prompt and import the package.

.. code-block:: Python

    >>> import compas
    >>> import compas_fea
