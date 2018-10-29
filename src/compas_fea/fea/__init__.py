"""
.. _compas_fea.fea:

********************************************************************************
fea
********************************************************************************

.. module:: compas_fea.fea

The compas_fea package supports Abaqus, Ansys, Sofistik and OpenSees as analysis backends.


writer
======

.. currentmodule:: compas_fea.fea.writer

:mod:`compas_fea.fea.writer`

.. autosummary::
    :toctree: generated/

    Writer


abaq
====

.. currentmodule:: compas_fea.fea.abaq

:mod:`compas_fea.fea.abaq`

.. autosummary::
    :toctree: generated/

    input_generate
    extract_data
    launch_process


ansys
=====

.. currentmodule:: compas_fea.fea.ansys

:mod:`compas_fea.fea.ansys`

.. autosummary::
    :toctree: generated/

    input_generate
    make_command_file_static
    make_command_file_modal
    make_command_file_harmonic
    ansys_launch_process
    ansys_launch_process_extract
    delete_result_files
    extract_rst_data
    write_results_from_rst
    load_to_results


opensees
========

.. currentmodule:: compas_fea.fea.opensees

:mod:`compas_fea.fea.opensees`

.. autosummary::
    :toctree: generated/

    input_generate
    extract_data
    launch_process


sofistik
========

.. currentmodule:: compas_fea.fea.sofistik

:mod:`compas_fea.fea.sofistik`

.. autosummary::
    :toctree: generated/

    input_generate

"""

from .writer import *
