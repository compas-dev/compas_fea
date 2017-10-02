"""
compas_fea.cad.blender : Blender specific functions.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas_blender.geometry import bmesh_data
from compas_blender.geometry.mesh import colour_bmesh_vertices

from compas_blender.helpers import mesh_from_bmesh

from compas_blender.utilities import clear_layers
from compas_blender.utilities import delete_all_materials
from compas_blender.utilities import draw_bmesh
from compas_blender.utilities import draw_cuboid
from compas_blender.utilities import draw_pipes
from compas_blender.utilities import get_objects
from compas_blender.utilities import get_objects_locations
from compas_blender.utilities import xdraw_texts

from compas_fea.utilities.functions import colorbar
from compas_fea.utilities.functions import extrude_mesh
from compas_fea.utilities.functions import network_order
from compas_fea.utilities.functions import postprocess
from compas_fea.utilities.functions import voxels

from numpy import array
from numpy import newaxis

try:
    from meshpy.tet import build
    from meshpy.tet import MeshInfo
except ImportError:
    print('***** MeshPy not imported *****')

import json

try:
    import bpy
except ImportError:
    pass


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'add_nodes_elements_from_bmesh',
    'add_nodes_elements_from_layers',
    'add_tets_from_bmesh',
    'add_nset_from_bmeshes',
    'add_elset_from_bmeshes',
    'add_nset_from_objects',
    'plot_data',
    'ordered_lines',
    'plot_voxels',
    'mesh_extrude'
]


node_fields = ['RF', 'RM', 'U', 'UR', 'CF', 'CM']
element_fields = ['SF', 'SM', 'SK', 'SE', 'S', 'E', 'PE', 'RBFOR']


def add_nodes_elements_from_bmesh(structure, bmesh, edge_type=None, face_type=None, block_type=None, acoustic=False,
                                  thermal=False):
    """ Adds the Blender mesh's nodes, edges and faces to the Structure object.

    Parameters:
        structure (obj): Structure object to update.
        bmesh (obj): Blender mesh object.
        edge_type (str): Element type for bmesh edges.
        face_type (str): Element type for bmesh faces.
        block_type (str): Element type for bmesh blocks.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """

    try:
        name = bmesh.name
        if name[-5:-3] == '}.':
            dic = name[:-4]
        else:
            dic = name
    except:
        pass

    vertices, edges, faces = bmesh_data(bmesh)

    for vertex in vertices:
        structure.add_node(vertex)

    if edge_type:
        try:
            dic_ = json.loads(dic.replace("'", '"'))
            ex = dic_.get('ex', None)
            ey = dic_.get('ey', None)
            axes = {'ex': ex, 'ey': ey}
        except:
            axes = {}
        for u, v in edges:
            sp = structure.check_node_exists(vertices[u])
            ep = structure.check_node_exists(vertices[v])
            structure.add_element(nodes=[sp, ep], type=edge_type, acoustic=acoustic, thermal=thermal, axes=axes)

    if face_type:
        for face in faces:
            nodes = [structure.check_node_exists(vertices[i]) for i in face]
            structure.add_element(nodes=nodes, type=face_type, acoustic=acoustic, thermal=thermal)

    if block_type in ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']:
            nodes = [structure.check_node_exists(i) for i in vertices]
            structure.add_element(nodes=nodes, type=block_type, acoustic=acoustic, thermal=thermal)


def add_nodes_elements_from_layers(structure, layers, edge_type=None, face_type=None, block_type=None, acoustic=False,
                                   thermal=False):
    """ Adds node and element data from Blender layers to Structure object.

    Note:
        - Layer is to contain only Blender mesh objects.

    Parameters:
        structure (obj): Structure object to update.
        layers (list): Layer numbers to extract nodes and elements from bmeshes.
        edge_type (str): Element type for bmesh edges.
        face_type (str): Element type for bmesh faces.
        block_type (str): Element type for bmesh blocks.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    if isinstance(layers, int):
        layers = [layers]
    for layer in layers:
        bmeshes = get_objects(layer)
        for bmesh in bmeshes:
            add_nodes_elements_from_bmesh(structure=structure, bmesh=bmesh, edge_type=edge_type, face_type=face_type,
                                          block_type=block_type, acoustic=acoustic, thermal=thermal)


def add_tets_from_bmesh(structure, name, bmesh, draw_tets=False, volume=None, layer=19, acoustic=False, thermal=False):
    """ Adds tetrahedron elements from a Blender mesh to Structure object.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name for the ELSET of tetrahedrons.
        bmesh (ob): The Blender mesh representing the outer surface.
        draw_tets (bool): Draw the generated tetrahedrons.
        volume (float): Maximum volume for tets.
        layer (int): Layer to draw tetrahedrons if draw_tets=True.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    vertices, edges, faces = bmesh_data(bmesh)
    tets_info = MeshInfo()
    tets_info.set_points(vertices)
    tets_info.set_facets(faces)
    tets = build(tets_info, max_volume=volume)

    for point in tets.points:
        structure.add_node(point)
    ekeys = []
    for element in tets.elements:
        nodes = [structure.check_node_exists(tets.points[i]) for i in element]
        ekey = structure.add_element(nodes=nodes, type='TetrahedronElement', acoustic=acoustic, thermal=thermal)
        ekeys.append(ekey)
    structure.add_set(name=name, type='element', selection=ekeys, explode=False)

    if draw_tets:
        tet_faces = [[0, 1, 2], [1, 3, 2], [1, 3, 0], [0, 2, 3]]
        for i, points in enumerate(tets.elements):
            xyz = [tets.points[j] for j in points]
            draw_bmesh(name=str(i), vertices=xyz, faces=tet_faces, layer=layer)


def add_elset_from_bmeshes(structure, name, bmeshes=None, layer=None, explode=False):
    """ Adds the Blender meshes' edges and faces as an element set.

    Note:
        - Either bmeshes or layer should be given, not both.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name of the new ELSET.
        bmeshes (list): Blender mesh objects to extract edges and faces.
        layer (int): Layer to get bmeshes from if bmeshes are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        bmeshes = get_objects(layer)
    elements = []
    for bmesh in bmeshes:
        vertices, edges, faces = bmesh_data(bmesh)

        for u, v in edges:
            sp = structure.check_node_exists(vertices[u])
            ep = structure.check_node_exists(vertices[v])
            element = structure.check_element_exists([sp, ep])
            if element is not None:
                elements.append(element)

        for face in faces:
            nodes = [structure.check_node_exists(vertices[i]) for i in face]
            element = structure.check_element_exists(nodes)
            if element is not None:
                elements.append(element)

    structure.add_set(name=name, type='element', selection=elements, explode=explode)


def add_nset_from_bmeshes(structure, name, bmeshes=None, layer=None, explode=False):
    """ Adds the Blender meshes' vertices as a node set.

    Note:
        - Either bmeshes or layer should be given, not both.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name of the new NSET.
        bmeshes (list): Blender mesh objects to extract vertices.
        layer (int): Layer to get bmeshes from if bmeshes are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        bmeshes = get_objects(layer)
    nodes = []
    for bmesh in bmeshes:
        vertices, edges, faces = bmesh_data(bmesh)

        for vertex in vertices:
            node = structure.check_node_exists(vertex)
            if node is not None:
                nodes.append(node)

    structure.add_set(name=name, type='node', selection=nodes, explode=explode)


def add_nset_from_objects(structure, name, objects=None, layer=None, explode=False):
    """ Adds the objects' locations as a node set.

    Note:
        - Either objects or layer should be given, not both.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name of the new NSET.
        objects (list): Objects to use location values.
        layer (int): Layer to get objects from if objects are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        objects = get_objects(layer)
    nodes = [structure.check_node_exists(object.location) for object in objects]
    structure.add_set(name=name, type='node', selection=nodes, explode=explode)


def add_elset_from_objects():
    raise NotImplementedError


def mesh_extrude(structure, bmesh, nz, dz):
    """ Extrudes a Blender mesh into cells of many layers.

    Note:
        - Extrusion is along the vertex normals.
        - Elements are added automatically to Structure object.

    Parameters:
        structure (obj): Structure object to update.
        bmesh (obj): Blender mesh object.
        nz (int): Number of layers.
        dz (float): Layer thickness.

    Returns:
        None
    """
    mesh = mesh_from_bmesh(bmesh)
    extrude_mesh(structure, mesh, nz, dz)


def ordered_lines(structure, network, layer):
    """ Extract node and element orders from a Network for a given start-point.

    Note:
        - Function is for a Network representing a single structural element.

    Parameters:
        structure (obj): Structure object.
        network (obj): Network object.
        layer (str): Layer to extract start-point (Blender object).

    Returns:
        list: Ordered nodes.
        list: Ordered elements.
        list: Cumulative lengths at element mid-points.
        float: Total length.
    """
    sp_xyz = get_objects_locations(get_objects(layer))[0]
    return network_order(sp_xyz, structure, network)


def plot_axes():
    raise NotImplementedError


def plot_data(structure, path, name, step, field='U', component='magnitude', scale=1.0, radius=0.05,
              iptype='mean', nodal='mean', cbar=[None, None], layer=0):
    """ Plots analysis results on the deformed shape of the Structure.

    Note:
        - Pipe visualisation of line elements is not based on the element section.

    Parameters:
        structure (obj): Structure object.
        path (str): Folder to saved data.
        name (str): Structure name.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'U', 'S', 'SM'.
        component (str): Component to plot, e.g. 'U1', 'RF2'.
        scale (float): Scale displacements for the deformed plot.
        radius (float): Radius of the pipe visualisation meshes.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        cbar (list): Minimum and maximum limits on the colourbar.
        layer (int): Layer number for plotting.

    Returns:
        None
    """
    clear_layers([layer])

    # Process data

    temp = '{0}{1}/'.format(path, name)
    cmin, cmax = cbar
    toc, cnodes, celements, cnodal, fabs, nabs, U, fscaled, nscaled = postprocess(
        temp, name, step, field, component, scale, iptype, nodal, cmin, cmax, type=1)
    with open('{0}{1}-elements.json'.format(temp, name), 'r') as f:
        elements = json.load(f)

    # Print info

    with open('{0}{1}-{2}-info.json'.format(temp, name, step), 'r') as f:
        info = json.load(f)
    print('\n')
    print('Step summary: {0}'.format(step))
    print('--------------' + '-' * len(step))
    print('Frame description: {0}'.format(info['description']))
    print('Analysis time: {0:.3f}'.format(info['toc_analysis']))
    print('Extraction time: {0:.3f}'.format(info['toc_extraction']))
    print('Processing time: {0:.3f}'.format(toc))

    # Plot meshes

    mesh_faces = []
    npts = 8
    for ekey, nodes in elements.items():
        n = len(nodes)

        if n == 2:
            u, v = nodes
            pipe = draw_pipes(start=[U[u]], end=[U[v]], radius=radius, layer=layer)[0]
            if field in node_fields:
                col1 = [list(cnodes[u])] * npts
                col2 = [list(cnodes[v])] * npts
            elif field in element_fields:
                col1 = [list(celements[int(ekey)])] * npts
                col2 = [list(celements[int(ekey)])] * npts
            colour_bmesh_vertices(bmesh=pipe, vertices=range(0, 2 * npts, 2), colours=col1)
            colour_bmesh_vertices(bmesh=pipe, vertices=range(1, 2 * npts, 2), colours=col2)

        elif n in [3, 4]:
            mesh_faces.append(nodes)

    if mesh_faces:
        bmesh = draw_bmesh(name='bmesh', vertices=U, faces=mesh_faces, layer=layer)
        nv = U.shape[0]
        if field in node_fields:
            colour_bmesh_vertices(bmesh=bmesh, vertices=range(nv), colours=list(cnodes))
        elif field in element_fields:
            colour_bmesh_vertices(bmesh=bmesh, vertices=range(nv), colours=list(cnodal))

    if field in element_fields:
        fabs = max([fabs, nabs])

    # Plot colourbar

    try:
        cmesh = get_objects(19)[0]
    except:
        x = [i * 0.1 for i in range(11)]
        y = [i * 0.1 - 1 for i in range(2)]
        vertices = [[xi, yi, 0] for yi in y for xi in x]
        faces = [[j * 11 + i, j * 11 + i + 1, (j + 1) * 11 + i + 1, (j + 1) * 11 + i + 0]
                 for i in range(10) for j in range(1)]
        cmesh = draw_bmesh(name='colorbar', vertices=vertices, faces=faces, layer=19)

    vertices, edges, faces = bmesh_data(cmesh)
    n = len(vertices)
    x = array(vertices)[:, 0]
    y = array(vertices)[:, 1]
    xmin = min(x)
    xmax = max(x)
    xran = xmax - xmin
    ymin = min(y)
    colors = colorbar(((x - xmin - xran / 2) / (xran / 2))[:, newaxis], input='array', type=1)
    bmesh = draw_bmesh(name='colorbar', vertices=vertices, faces=faces, layer=layer)
    colour_bmesh_vertices(bmesh=bmesh, vertices=range(n), colours=colors)
    h = xran / 20.
    pos1 = [xmax, ymin - 2 * h, 0]
    pos2 = [xmin, ymin - 2 * h, 0]
    pos3 = [xmin + xran / 2., ymin - 2 * h, 0]
    text1 = '{0:.4g}'.format(+fabs)
    text2 = '{0:.4g}'.format(-fabs)
    text3 = '0'
    texts = [
        {'radius': 2 * h, 'pos': pos1, 'color': 'white', 'name': 'max', 'text': text1, 'layer': layer},
        {'radius': 2 * h, 'pos': pos2, 'color': 'white', 'name': 'min', 'text': text2, 'layer': layer},
        {'radius': 2 * h, 'pos': pos3, 'color': 'white', 'name': 'mid', 'text': text3, 'layer': layer}]
    xdraw_texts(texts)


def plot_voxels(structure, path, name, step, field='S', component='mises', iptype='max', nodal='max', vdx=1,
                cbar=[0, 1], cube_size=[10, 10, 10], layer=0):
    """ Applies a base voxel material and texture to a cube for 4D visualisation.

    Note:
        - Texture ramping should be done manually afterwards.
        - Voxel display works best with cube dimensions >= 10.
        - The absolute value is plotted, ranged between [0, 1].

     Parameters:
        structure (obj): Structure object.
        path (str): Folder where results files are stored.
        name (str): Structure name.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'U', 'S'.
        component (str): Component to plot, e.g. 'U1', 'mises'.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        vdx (float): Voxel data spacing.
        cbar (list): Minimum and maximum limits on the colorbar.
        cube_size (list): x, y, and z lengths of the cube.
        layer (int): Layer to plot voxel cuboid on.

    Returns:
        None
    """

    # Load data

    temp = '{0}{1}/'.format(path, name)
    cmin, cmax = cbar
    toc, cnodes, celements, cnodal, fabs, nabs, U, fscaled, nscaled = postprocess(
        temp, name, step, field, component, 1, iptype, nodal, cmin, cmax, type=1)

    # Process data

    if field in node_fields:
        data = fscaled
    elif field in element_fields:
        data = nscaled
    Am = voxels(values=data, vmin=None, U=U, vdx=vdx, plot=None, indexing='ij')
    sx, sy, sz = Am.shape

    # Save bvox data

    header = array([sx, sy, sz, 1])
    data = Am.flatten()
    fnm_bvox = '{0}{1}-voxels.bvox'.format(temp, name)
    with open(fnm_bvox, 'wb') as fnm:
        header.astype('<i4').tofile(fnm)
        data.astype('<f4').tofile(fnm)

    # Create cube with volumetric material

    clear_layers([layer])
    delete_all_materials()
    material = bpy.data.materials.new('material')
    material.type = 'VOLUME'
    material.volume.density = 0
    material.volume.density_scale = 5
    material.volume.scattering = 0.5
    cx, cy, cz = cube_size
    cube = draw_cuboid(cx, cy, cz, location=[0, 0, 0], layer=layer)
    cube.data.materials.append(material)

    # Create base voxel texture

    texture = bpy.data.textures.new('texture', type='VOXEL_DATA')
    texture.voxel_data.file_format = 'BLENDER_VOXEL'
    texture.voxel_data.filepath = fnm_bvox
    texture.voxel_data.extension = 'EXTEND'
    texture.voxel_data.interpolation = 'TRILINEAR'
    slot = cube.data.materials['material'].texture_slots.add()
    slot.texture = texture
    slot.texture_coords = 'ORCO'
    slot.mapping = 'FLAT'
    slot.use_map_density = True
    slot.use_map_emission = True
    slot.use_map_color_emission = True
