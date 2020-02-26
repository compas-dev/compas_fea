"""
********************************************************************************
utilities
********************************************************************************

.. currentmodule:: compas_fea.utilities

The compas_fea package's supporting utilities and functions.


functions
=========

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

.. autosummary::
    :toctree: generated/

    discretise_faces
    extrude_mesh
    tets_from_vertices_faces

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .functions import *
from .meshing import *

__all__ = [name for name in dir() if not name.startswith('_')]
