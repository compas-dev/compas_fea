********************************************************************************
Installation
********************************************************************************

.. note::

    Old versions of :mod:`compas_fea` were installed by adding the location of a
    local source folder directly to the ``PYTHONPATH``.
    If you still have such a legacy install on your system, we highly recommend
    that you remove all traces of it, which means to remove :mod:`compas`,
    :mod:`compas_fea`, or any other COMPAS packages from your ``PYTHONPATH``,
    because it will interfere with the proper functioning of more modern, flexible
    and robust installation procedures adopted by the COMPAS ecosystem.

    This also applies to old procedures for installing COMPAS packages for Rhino.
    If you still have COMPAS packages registered directly in the ``Modules Search Path`` in Rhino,
    please remove them.


Requirements
============

To use :mod:`compas_fea` you need to install COMPAS,
and have at least on of the supported analysis backends available on your system.
Currently, :mod:`compas_fea` supports Abaqus, ANSYS, and OpenSEES to various degrees.
See :ref:`fea` for more detailed information.

To install COMPAS, see the `Getting Started <https://compas-dev.github.io/main/gettingstarted.html>`_
instructions in the COMPAS docs.


Install :mod:`compas_fea`
=========================

As with all other COMPAS packages, we recommend to install :mod:`compas_fea` in a ``conda`` environment.

.. code-block:: bash

    conda create -n fea -c conda-forge python=3.9 compas --yes
    conda activate fea
    pip install compas_fea


Working in Rhino
================

If you wish to use :mod:`compas_fea` in Rhino, you have to add it to the installed Rhino COMPAS packages.

.. code-block:: bash

    conda activate fea
    python -m compas_rhino.install -v 7.0
    python -m compas_rhino.install -v 7.0 -p compas_fea

For more information about using COMPAS in Rhino, see the COMPAS docs:
https://compas.dev/compas/dev/gettingstarted/rhino.html


Working in Blender
==================

To use :mod:`compas_fea` in Blender, you simply have to register the environment with Blender.

.. code-block:: bash

    conda activate fea
    python -m compas_blender.install -v 2.93

For more information about using COMPAS in Blender, see the COMPAS docs:
https://compas.dev/compas/dev/gettingstarted/blender.html
