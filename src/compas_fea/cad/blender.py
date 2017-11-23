"""
compas_fea.cad.blender : Blender specific functions.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas_blender.geometry import BlenderMesh
from compas_blender.helpers import mesh_from_bmesh
from compas_blender.utilities import clear_layer
from compas_blender.utilities import draw_cuboid
from compas_blender.utilities import draw_pipes
from compas_blender.utilities import draw_plane
from compas_blender.utilities import get_objects
from compas_blender.utilities import get_object_location
from compas_blender.utilities import set_object_location
from compas_blender.utilities import xdraw_mesh
from compas_blender.utilities import xdraw_texts

from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors

from compas_fea.utilities import colorbar
from compas_fea.utilities import extrude_mesh
from compas_fea.utilities import network_order
from compas_fea.utilities import postprocess
from compas_fea.utilities import voxels

from numpy import array
from numpy import min
from numpy import max
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
    'ordered_network',
    'plot_voxels',
    'mesh_extrude'
]


def add_nodes_elements_from_bmesh(structure, bmesh, line_type=None, mesh_type=None, acoustic=False, thermal=False):
    """ Adds the Blender mesh's nodes, edges and faces to the Structure object.

    Parameters:
        structure (obj): Structure object to update.
        bmesh (obj): Blender mesh object.
        line_type (str): Element type for lines (bmesh edges).
        mesh_type (str): Element type for meshes.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    solids = ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']

    blendermesh = BlenderMesh(bmesh)
    vertices = blendermesh.get_vertex_coordinates()
    edges = blendermesh.get_edge_vertex_indices()
    faces = blendermesh.get_face_vertex_indices()

    try:
        name = blendermesh.guid
        if name[-5:-3] == '}.':
            name = name[:-4]
    except:
        pass

    for vertex in vertices:
        structure.add_node(vertex)

    if line_type and edges:

        try:
            dic_ = json.loads(name.replace("'", '"'))
            ex = dic_.get('ex', None)
            ey = dic_.get('ey', None)
        except:
            ex = None
            ey = None
        axes = {'ex': ex, 'ey': ey}

        for u, v in edges:
            sp = structure.check_node_exists(vertices[u])
            ep = structure.check_node_exists(vertices[v])
            ez = subtract_vectors(structure.node_xyz(ep), structure.node_xyz(sp))
            axes['ez'] = ez
            structure.add_element(nodes=[sp, ep], type=line_type, acoustic=acoustic, thermal=thermal, axes=axes)

    if mesh_type:

        if mesh_type in solids:
            nodes = [structure.check_node_exists(i) for i in vertices]
            structure.add_element(nodes=nodes, type=mesh_type, acoustic=acoustic, thermal=thermal)
        else:
            for face in faces:
                nodes = [structure.check_node_exists(vertices[i]) for i in face]
                structure.add_element(nodes=nodes, type=mesh_type, acoustic=acoustic, thermal=thermal)


def add_nodes_elements_from_layers(structure, layers, line_type=None, mesh_type=None, acoustic=False, thermal=False):
    """ Adds node and element data from Blender layers to Structure object.

    Parameters:
        structure (obj): Structure object to update.
        layers (list): Layers to extract nodes and elements.
        line_type (str): Element type for lines (bmesh edges).
        mesh_type (str): Element type for meshes.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    if isinstance(layers, int):
        layers = [layers]

    for layer in layers:
        bmeshes = get_objects(layer=layer)
        for bmesh in bmeshes:
            add_nodes_elements_from_bmesh(structure=structure, bmesh=bmesh, line_type=line_type, mesh_type=mesh_type, acoustic=acoustic, thermal=thermal)


def add_tets_from_bmesh(structure, name, bmesh, draw_tets=False, volume=None, layer=19, acoustic=False, thermal=False):
    """ Adds tetrahedron elements from a Blender mesh to the Structure object.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name for the element set of tetrahedrons.
        bmesh (ob): The Blender mesh representing the outer surface.
        draw_tets (bool): Draw the generated tetrahedrons.
        volume (float): Maximum volume for tets.
        layer (int): Layer to draw tetrahedrons if draw_tets=True.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    blendermesh = BlenderMesh(bmesh)
    vertices = blendermesh.get_vertex_coordinates()
    faces = blendermesh.get_face_vertex_indices()

    info = MeshInfo()
    info.set_points(vertices)
    info.set_facets(faces)
    tets = build(info, max_volume=volume)

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
            xdraw_mesh(name=str(i), vertices=xyz, faces=tet_faces, layer=layer)


def add_elset_from_bmeshes(structure, name, bmeshes=None, layer=None, explode=False):
    """ Adds the Blender meshes' edges and faces as an element set.

    Note:
        - Either bmeshes or layer should be given, not both.

    Parameters:
        structure (obj): Structure object to update.
        name (str): Name of the new element set.
        bmeshes (list): Blender mesh objects to extract edges and faces.
        layer (int): Layer to get bmeshes from if bmeshes are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        bmeshes = [object for object in get_objects(layer=layer) if object.type == 'MESH']

    elements = []
    for bmesh in bmeshes:

        blendermesh = BlenderMesh(bmesh)
        vertices = blendermesh.get_vertex_coordinates()
        edges = blendermesh.get_edge_vertex_indices()
        faces = blendermesh.get_face_vertex_indices()

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
        name (str): Name of the new node set.
        bmeshes (list): Blender mesh objects to extract vertices.
        layer (int): Layer to get bmeshes from if bmeshes are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        bmeshes = [object for object in get_objects(layer=layer) if object.type == 'MESH']

    nodes = []
    for bmesh in bmeshes:

        blendermesh = BlenderMesh(bmesh)
        vertices = blendermesh.get_vertex_coordinates()

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
        name (str): Name of the new node set.
        objects (list): Objects to use location values.
        layer (int): Layer to get objects from if objects are not given.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if layer is not None:
        objects = get_objects(layer=layer)
    nodes = [structure.check_node_exists(object.location) for object in objects]
    structure.add_set(name=name, type='node', selection=nodes, explode=explode)


def mesh_extrude(structure, bmesh, nz, dz, setname):
    """ Extrudes a Blender mesh into cells of many layers and adds to Structure.

    Note:
        - Extrusion is along the vertex normals.
        - Elements are added automatically to the Structure object.

    Parameters:
        structure (obj): Structure object to update.
        bmesh (obj): Blender mesh object.
        nz (int): Number of layers.
        dz (float): Layer thickness.
        setname (str): Name of set for added elements.

    Returns:
        None
    """
    mesh = mesh_from_bmesh(bmesh)
    extrude_mesh(structure=structure, mesh=mesh, nz=nz, dz=dz, setname=setname)


def ordered_network(structure, network, layer):
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
    sp_xyz = get_object_location(object=get_objects(layer=layer)[0])
    return network_order(sp_xyz=sp_xyz, structure=structure, network=network)


def plot_axes():
    raise NotImplementedError


def plot_data(structure, step, field='um', layer=0, scale=1.0, radius=0.05, cbar=[None, None], iptype='mean',
              nodal='mean', mode='', colorbar_size=1):
    """ Plots analysis results on the deformed shape of the Structure.

    Note:
        - Pipe visualisation of line elements is not based on the element section.

    Parameters:
        structure (obj): Structure object.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'um', 'sxx', 'sm1'.
        layer (int): Layer number for plotting.
        scale (float): Scale displacements for the deformed plot.
        radius (float): Radius of the pipe visualisation meshes.
        cbar (list): Minimum and maximum limits on the colorbar.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        mode (int): mode or frequency number to plot, in case of modal, harmonic or buckling analysis.
        colorbar_size (float): Scale on the size of the colorbar.

    Returns:
        None
    """
    clear_layer(layer=layer)

    # Node and element data

    nkeys = sorted(structure.nodes, key=int)
    nodes = [structure.node_xyz(nkey) for nkey in nkeys]

    ekeys = sorted(structure.elements, key=int)
    elements = [structure.elements[ekey].nodes for ekey in ekeys]

    nodal_data = structure.results[step]['nodal']
    ux = [nodal_data['ux{0}'.format(str(mode))][key] for key in nkeys]
    uy = [nodal_data['uy{0}'.format(str(mode))][key] for key in nkeys]
    uz = [nodal_data['uz{0}'.format(str(mode))][key] for key in nkeys]

    # Process data

    try:
        data = [nodal_data[field + str(mode)][key] for key in nkeys]
        dtype = 'nodal'
    except(Exception):
        elemental_data = structure.results[step]['element']
        data = elemental_data[field]
        dtype = 'element'

    toc, U, cnodes, fabs = postprocess(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, 1, iptype, nodal)
    U = array(U)

    print('\n***** Data processed : {0} s *****'.format(toc))

    # Plot meshes

    npts = 8
    mesh_faces = []

    for nodes in elements:
        n = len(nodes)

        if n == 2:
            u, v = nodes
            pipe = draw_pipes(start=[U[u]], end=[U[v]], radius=radius, layer=layer)[0]
            col1 = [cnodes[u]] * npts
            col2 = [cnodes[v]] * npts
            blendermesh = BlenderMesh(pipe)
            blendermesh.set_vertex_colors(vertices=range(0, 2 * npts, 2), colors=col1)
            blendermesh.set_vertex_colors(vertices=range(1, 2 * npts, 2), colors=col2)

        elif n in [3, 4]:
            mesh_faces.append(nodes)

    if mesh_faces:
        bmesh = xdraw_mesh(name='bmesh', vertices=U, faces=mesh_faces, layer=layer)
        blendermesh = BlenderMesh(bmesh)
        blendermesh.set_vertex_colors(vertices=range(U.shape[0]), colors=cnodes)

    # Plot colourbar

    xr, yr, _ = structure.node_bounds()
    yran = yr[1] - yr[0]
    if not yran:
        yran = 1
    s = yran * 0.1 * colorbar_size
    xmin = xr[1] + 3 * s
    ymin = yr[0]

    cmesh = draw_plane(name='colorbar', Lx=s, dx=s, Ly=10*s, dy=s, layer=layer)
    set_object_location(object=cmesh, location=[xmin, ymin, 0])
    blendermesh = BlenderMesh(cmesh)
    vertices = blendermesh.get_vertex_coordinates()
    y = array(vertices)[:, 1]

    yn = yran * colorbar_size
    colors = colorbar(((y - ymin - 0.5 * yn) * 2 / yn)[:, newaxis], input='array', type=1)
    blendermesh.set_vertex_colors(vertices=range(len(vertices)), colors=colors)

    h = 0.6 * s
    texts = []
    for i in range(5):
        x0 = xmin + 1.2 * s
        yu = ymin + (5.8 + i) * s
        yl = ymin + (3.8 - i) * s
        valu = float(+fabs * (i + 1) / 5.)
        vall = float(-fabs * (i + 1) / 5.)
        texts.extend([
            {'radius': h, 'pos': [x0, yu, 0], 'text': '{0:.5g}'.format(valu), 'layer': layer},
            {'radius': h, 'pos': [x0, yl, 0], 'text': '{0:.5g}'.format(vall), 'layer': layer}])
    texts.extend([
        {'radius': h, 'pos': [x0, ymin + 4.8 * s, 0], 'text': '0', 'layer': layer},
        {'radius': h, 'pos': [xmin, ymin + 12 * s, 0], 'text': 'Step:{0}   Field:{1}'.format(step, field), 'layer': layer}])

    xdraw_texts(texts)


def plot_voxels(structure, step, field='smises', layer=0, scale=1.0, cbar=[None, None], iptype='mean', nodal='mean',
                vdx=None, cube_size=[10, 10, 10]):
    """ Applies a base voxel material and texture to a cube for 4D visualisation.

    Note:
        - Texture ramping should be done manually afterwards.
        - Voxel display works best with cube dimensions >= 10.
        - The absolute value is plotted, ranged between [0, 1].

     Parameters:
        structure (obj): Structure object.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'smises'.
        layer (int): Layer to plot voxel cuboid on.
        scale (float): Scale displacements for the deformed plot.
        cbar (list): Minimum and maximum limits on the colorbar.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        vdx (float): Voxel spacing.
        cube_size (list): x, y, and z lengths of the cube.

    Returns:
        None
    """
    pass

#     # Load data

#     temp = '{0}{1}/'.format(path, name)
#     cmin, cmax = cbar
#     toc, cnodes, celements, cnodal, fabs, nabs, U, fscaled, nscaled = postprocess(
#         temp, name, step, field, component, 1, iptype, nodal, cmin, cmax, type=1)

#     # Process data

#     if field in node_fields:
#         data = fscaled
#     elif field in element_fields:
#         data = nscaled
#     Am = voxels(values=data, vmin=None, U=U, vdx=vdx, plot=None, indexing='ij')
#     sx, sy, sz = Am.shape

#     # Save bvox data

#     header = array([sx, sy, sz, 1])
#     data = Am.flatten()
#     fnm_bvox = '{0}{1}-voxels.bvox'.format(temp, name)
#     with open(fnm_bvox, 'wb') as fnm:
#         header.astype('<i4').tofile(fnm)
#         data.astype('<f4').tofile(fnm)

#     # Create cube with volumetric material

#     clear_layers([layer])
#     delete_all_materials()
#     material = bpy.data.materials.new('material')
#     material.type = 'VOLUME'
#     material.volume.density = 0
#     material.volume.density_scale = 5
#     material.volume.scattering = 0.5
#     cx, cy, cz = cube_size
#     cube = draw_cuboid(cx, cy, cz, location=[0, 0, 0], layer=layer)
#     cube.data.materials.append(material)

#     # Create base voxel texture

#     texture = bpy.data.textures.new('texture', type='VOXEL_DATA')
#     texture.voxel_data.file_format = 'BLENDER_VOXEL'
#     texture.voxel_data.filepath = fnm_bvox
#     texture.voxel_data.extension = 'EXTEND'
#     texture.voxel_data.interpolation = 'TRILINEAR'
#     slot = cube.data.materials['material'].texture_slots.add()
#     slot.texture = texture
#     slot.texture_coords = 'ORCO'
#     slot.mapping = 'FLAT'
#     slot.use_map_density = True
#     slot.use_map_emission = True
#     slot.use_map_color_emission = True
