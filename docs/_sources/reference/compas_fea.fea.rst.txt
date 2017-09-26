
.. _compas_fea.fea:

********************************************************************************
compas_fea.fea
********************************************************************************

.. module:: compas_fea.fea

The compas_fea package supports ABAQUS, ANSYS and OpenSEES as analysis backends.


abaq
====

.. currentmodule:: compas_fea.fea.abaq

:mod:`compas_fea.fea.abaq`

.. autosummary::
    :toctree: generated/

    inp_write_constraints
    inp_write_elements
    inp_generate
    inp_write_heading
    inp_write_materials
    inp_write_misc
    inp_write_nodes
    inp_write_properties
    inp_write_sets
    inp_write_steps


ansys
=====

.. currentmodule:: compas_fea.fea.ansys

:mod:`compas_fea.fea.ansys`

.. autosummary::
    :toctree: generated/

    inp_generate
    make_command_file_static
    make_command_file_static_combined
    make_command_file_modal
    make_command_file_harmonic
    ansys_launch_process
    delete_result_files
    write_total_results


