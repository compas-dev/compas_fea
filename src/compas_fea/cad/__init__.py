"""
********************************************************************************
cad
********************************************************************************

.. currentmodule:: compas_fea.cad

The compas_fea package supports Rhino and Blender in the frontend.

Blender
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    add_nodes_elements_from_bmesh
    add_nodes_elements_from_layers
    add_nsets_from_layers
    add_nset_from_meshes
    add_tets_from_mesh
    discretise_mesh
    mesh_extrude
    plot_concentrated_forces
    plot_data
    plot_reaction_forces
    plot_voxels
    weld_meshes_from_layer


Rhino
=====

.. autosummary::
    :toctree: generated/
    :nosignatures:

    add_element_set
    add_node_set
    add_nodes_elements_from_layers
    add_sets_from_layers
    add_tets_from_mesh
    discretise_mesh
    mesh_extrude
    network_from_lines
    ordered_network
    plot_reaction_forces
    plot_concentrated_forces
    plot_mode_shapes
    plot_volmesh
    plot_axes
    plot_data
    plot_principal_stresses
    plot_voxels
    weld_meshes_from_layer

"""
from __future__ import absolute_import

import compas

if compas.BLENDER:
    from .blender import (  # noqa: F401
        add_nodes_elements_from_bmesh,
        add_nodes_elements_from_layers,
        add_nsets_from_layers,
        add_nset_from_meshes,
        add_tets_from_mesh,
        discretise_mesh,
        mesh_extrude,
        plot_concentrated_forces,
        plot_data,
        plot_reaction_forces,
        plot_voxels,
        weld_meshes_from_layer,
    )
    __all__ = [
        'add_nodes_elements_from_bmesh',
        'add_nodes_elements_from_layers',
        'add_nsets_from_layers',
        'add_nset_from_meshes',
        'add_tets_from_mesh',
        'discretise_mesh',
        'mesh_extrude',
        'plot_concentrated_forces',
        'plot_data',
        'plot_reaction_forces',
        'plot_voxels',
        'weld_meshes_from_layer',
    ]

elif compas.RHINO:
    from .rhino import (  # noqa: F401
        add_element_set,
        add_node_set,
        add_nodes_elements_from_layers,
        add_sets_from_layers,
        add_tets_from_mesh,
        discretise_mesh,
        mesh_extrude,
        network_from_lines,
        ordered_network,
        plot_reaction_forces,
        plot_concentrated_forces,
        plot_mode_shapes,
        plot_volmesh,
        plot_axes,
        plot_data,
        plot_principal_stresses,
        plot_voxels,
        weld_meshes_from_layer,
    )
    __all__ = [
        'add_element_set',
        'add_node_set',
        'add_nodes_elements_from_layers',
        'add_sets_from_layers',
        'add_tets_from_mesh',
        'discretise_mesh',
        'mesh_extrude',
        'network_from_lines',
        'ordered_network',
        'plot_reaction_forces',
        'plot_concentrated_forces',
        'plot_mode_shapes',
        'plot_volmesh',
        'plot_axes',
        'plot_data',
        'plot_principal_stresses',
        'plot_voxels',
        'weld_meshes_from_layer',
    ]

else:
    __all__ = []
