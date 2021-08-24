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
    # plotvoxels


meshing
=======

.. autosummary::
    :toctree: generated/

    discretise_faces
    extrude_mesh
    tets_from_vertices_faces

"""
from __future__ import absolute_import

from .functions import (
    colorbar,
    combine_all_sets,
    group_keys_by_attribute,
    group_keys_by_attributes,
    network_order,
    normalise_data,
    postprocess,
    process_data,
    principal_stresses,
    # plotvoxels,
    identify_ranges,
    mesh_from_shell_elements
)
from .meshing import (
    discretise_faces,
    extrude_mesh,
    tets_from_vertices_faces,
)

__all__ = [
    'colorbar',
    'combine_all_sets',
    'group_keys_by_attribute',
    'group_keys_by_attributes',
    'network_order',
    'normalise_data',
    'postprocess',
    'process_data',
    'principal_stresses',
    # 'plotvoxels',
    'identify_ranges',
    'mesh_from_shell_elements',

    'discretise_faces',
    'extrude_mesh',
    'tets_from_vertices_faces',
]
