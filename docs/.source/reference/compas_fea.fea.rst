
.. _compas_fea.fea:

********************************************************************************
fea
********************************************************************************

.. module:: compas_fea.fea

The compas_fea package supports ABAQUS, ANSYS and OpenSEES as analysis backends.


abaq
====

.. currentmodule:: compas_fea.fea.abaq

:mod:`compas_fea.fea.abaq`

.. autosummary::
    :toctree: generated/

    abaqus_launch_process
    extract_odb_data
    input_write_constraints
    input_write_elements
    input_generate
    input_write_heading
    input_write_materials
    input_write_misc
    input_write_nodes
    input_write_properties
    input_write_sets
    input_write_steps


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
    delete_result_files
    write_total_results


opensees
========

.. currentmodule:: compas_fea.fea.opensees

:mod:`compas_fea.fea.opensees`

.. autosummary::
    :toctree: generated/

    input_generate
    input_write_heading
    input_write_nodes
    input_write_bcs
    input_write_elements
    input_write_recorders
    input_write_patterns
    opensees_launch_process

