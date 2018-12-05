"""
.. _compas_fea.utilities:

********************************************************************************
utilities
********************************************************************************

.. module:: compas_fea.utilities

The compas_fea package's supporting utilities and functions.


functions
=========

.. currentmodule:: compas_fea.utilities.functions

:mod:`compas_fea.utilities.functions`

.. autosummary::
    :toctree: generated/

    colorbar
    combine_all_sets
    group_keys_by_attribute
    group_keys_by_attributes
    identify_ranges
    mesh_from_shell_elements
    network_order
    normalise_data
    principal_stresses
    process_data
    postprocess
    plotvoxels


meshing
=======

.. currentmodule:: compas_fea.utilities.meshing

:mod:`compas_fea.utilities.meshing`

.. autosummary::
    :toctree: generated/

    discretise_faces
    extrude_mesh
    tets_from_vertices_faces

"""

from .functions import *
from .meshing import *
