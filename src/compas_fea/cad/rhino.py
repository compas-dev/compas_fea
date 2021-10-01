from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import compas
if compas.RHINO:
    from compas_rhino.geometry import RhinoMesh

from compas.datastructures.mesh import Mesh
from compas.datastructures import Network
from compas.geometry import Frame, Transformation, Vector
from compas.geometry import add_vectors
from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors
from compas_fea.structure import Structure


from compas_fea.utilities import colorbar
from compas_fea.utilities import extrude_mesh
from compas_fea.utilities import network_order

if not compas.IPY:
    from compas_fea.utilities import meshing
    from compas_fea.utilities import functions
else:
    from compas.rpc import Proxy
    functions = Proxy('compas_fea.utilities.functions')
    meshing = Proxy('compas_fea.utilities.meshing')

if compas.RHINO:
    import rhinoscriptsyntax as rs


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


def add_element_set(structure, guids, name):
    """
    Adds element set information from Rhino curve and mesh guids.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    guids : list
        Rhino curve and Rhino mesh guids.
    name : str
        Name of the new element set.

    Returns
    -------
    None

    Notes
    -----
    - Meshes representing solids must have 'solid' in their name.
    """

    elements = []

    for guid in guids:

        if rs.IsCurve(guid):

            sp = structure.check_node_exists(rs.CurveStartPoint(guid))
            ep = structure.check_node_exists(rs.CurveEndPoint(guid))
            element = structure.check_element_exists([sp, ep])
            if element is not None:
                elements.append(element)

        elif rs.IsMesh(guid):

            vertices = rs.MeshVertices(guid)
            faces = rs.MeshFaceVertices(guid)

            if rs.ObjectName(guid) and ('solid' in rs.ObjectName(guid)):
                nodes = [structure.check_node_exists(i) for i in vertices]
                element = structure.check_element_exists(nodes)
                if element is not None:
                    elements.append(element)
            else:
                for face in faces:
                    nodes = [structure.check_node_exists(vertices[i]) for i in face]
                    if nodes[2] == nodes[3]:
                        del nodes[-1]
                    element = structure.check_element_exists(nodes)
                    if element is not None:
                        elements.append(element)

    structure.add_set(name=name, type='element', selection=elements)


def add_node_set(structure, guids, name):
    """
    Adds node set information from Rhino point guids.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    guids : list
        Rhino point guids.
    name : str
        Name of the new node set.

    Returns
    -------
    None

    """

    nodes = []

    for guid in guids:

        if rs.IsPoint(guid):

            node = structure.check_node_exists(rs.PointCoordinates(guid))
            if node is not None:
                nodes.append(node)

    structure.add_set(name=name, type='node', selection=nodes)


def add_nodes_elements_from_layers(structure, layers, line_type=None, mesh_type=None, thermal=False, pA=None, pL=None):
    """
    Adds node and element data from Rhino layers to the Structure object.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    layers : list
        Layer string names to extract nodes and elements.
    line_type : str
        Element type for line objects.
    mesh_type : str
        Element type for mesh objects.
    thermal : bool
        Thermal properties on or off.
    pA : float
        Mass area density [kg/m2].
    pL : float
        Mass length density [kg/m].

    Returns
    -------
    list
        Node keys that were added to the Structure.
    list
        Element keys that were added to the Structure.

    """

    if isinstance(layers, str):
        layers = [layers]

    added_nodes = set()
    added_elements = set()

    for layer in layers:

        elset = set()

        for guid in rs.ObjectsByLayer(layer):

            if line_type and rs.IsCurve(guid):

                sp_xyz = rs.CurveStartPoint(guid)
                ep_xyz = rs.CurveEndPoint(guid)
                ez = subtract_vectors(ep_xyz, sp_xyz)
                L = length_vector(ez)
                m = 0.5 * L * pL if pL else None

                sp = structure.add_node(xyz=sp_xyz, mass=m)
                ep = structure.add_node(xyz=ep_xyz, mass=m)
                added_nodes.add(sp)
                added_nodes.add(ep)

                try:
                    name = rs.ObjectName(guid).replace("'", '"')

                    if name[0] in ['_', '^']:
                        name = name[1:]

                    dic = json.loads(name)
                    ex = dic.get('ex', None)
                    ey = dic.get('ey', None)

                    if ex and not ey:
                        ey = cross_vectors(ex, ez)

                except Exception:
                    ex = None
                    ey = None

                axes = {'ex': ex, 'ey': ey, 'ez': ez}

                ekey = structure.add_element(nodes=[sp, ep], type=line_type, thermal=thermal, axes=axes)

                if (line_type == 'BeamElement') and (ex is None):

                    if (ez[0] == 0) and (ez[1] == 0):

                        print('***** WARNING: vertical BeamElement with no ex axis, element {0} *****'.format(ekey))

                if ekey is not None:
                    added_elements.add(ekey)
                    elset.add(ekey)

            elif mesh_type and rs.IsMesh(guid):

                mesh = RhinoMesh.from_guid(guid).to_compas()

                vertices = rs.MeshVertices(guid)
                nodes = []
                masses = []

                for c, vertex in enumerate(vertices):
                    m = mesh.vertex_area(c) * pA if pA else None
                    masses.append(m)
                    nodes.append(structure.add_node(xyz=vertex, mass=m))

                added_nodes.update(nodes)

                if mesh_type in ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']:
                    ekey = structure.add_element(nodes=nodes, type=mesh_type, thermal=thermal)

                    if ekey is not None:
                        added_elements.add(ekey)
                        elset.add(ekey)

                elif mesh_type == 'MassElement':
                    node_iterator = 0
                    for node in nodes:
                        # structure.nodes[node].mass
                        ekey = structure.add_element(nodes=[node], type=mesh_type,
                                                     thermal=thermal, mass=masses[node_iterator])
                        node_iterator += 1
                        if ekey is not None:
                            added_elements.add(ekey)
                            elset.add(ekey)

                else:

                    try:
                        name = rs.ObjectName(guid).replace("'", '"')

                        if name[0] in ['_', '^']:
                            name = name[1:]

                        dic = json.loads(name)
                        ex = dic.get('ex', None)
                        ey = dic.get('ey', None)
                        ez = dic.get('ez', None)

                        if (ex and ey) and (not ez):
                            ez = cross_vectors(ex, ey)

                    except Exception:
                        ex = None
                        ey = None
                        ez = None

                    axes = {'ex': ex, 'ey': ey, 'ez': ez}

                    for face in rs.MeshFaceVertices(guid):

                        nodes = [structure.check_node_exists(vertices[i]) for i in face]
                        if nodes[-1] == nodes[-2]:
                            del nodes[-1]

                        ekey = structure.add_element(nodes=nodes, type=mesh_type, thermal=thermal, axes=axes)
                        if ekey is not None:
                            added_elements.add(ekey)
                            elset.add(ekey)

        structure.add_set(name=layer, type='element', selection=list(elset))

    return list(added_nodes), list(added_elements)


def add_sets_from_layers(structure, layers):
    """
    Add node and element sets to the Structure object from Rhino layers.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    layers : list
        List of layer string names to take objects from.

    Returns
    -------
    None

    Notes
    -----
    - Layers should exclusively contain nodes or elements.
    - Mixed elements, e.g. lines and meshes, are allowed on a layer.
    - Sets will inherit the layer names as their set name.

    """

    if isinstance(layers, str):
        layers = [layers]

    for layer in layers:
        guids = rs.ObjectsByLayer(layer)

        if guids:
            name = layer.split('::')[-1] if '::' in layer else layer
            check_points = [rs.IsPoint(guid) for guid in guids]

            if all(check_points):
                add_node_set(structure=structure, guids=guids, name=name)
            elif not any(check_points):
                add_element_set(structure=structure, guids=guids, name=name)
            else:
                print('***** Layer {0} contained a mixture of points and elements, set not created *****'.format(name))


def add_tets_from_mesh(structure, name, mesh, draw_tets=False, volume=None, thermal=False):
    """
    Adds tetrahedron elements from a mesh in Rhino to the Structure object.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    name : str
        Name for the element set of tetrahedrons.
    mesh : guid
        The mesh in Rhino representing the outer surface.
    draw_tets : str
        Layer to draw tetrahedrons on.
    volume : float
        Maximum volume for each tet.
    thermal : bool
        Thermal properties on or off.

    Returns
    -------
    None

    """

    rhinomesh = RhinoMesh.from_guid(mesh)
    vertices = rhinomesh.vertices
    faces = [face[:3] for face in rhinomesh.faces]

    try:
        tets_points, tets_elements = meshing.tets_from_vertices_faces(vertices=vertices, faces=faces, volume=volume)

        for point in tets_points:
            structure.add_node(point)

        ekeys = []

        for element in tets_elements:

            nodes = [structure.check_node_exists(tets_points[i]) for i in element]
            ekey = structure.add_element(nodes=nodes, type='TetrahedronElement', thermal=thermal)
            ekeys.append(ekey)

        structure.add_set(name=name, type='element', selection=ekeys)

        if draw_tets:

            rs.EnableRedraw(False)
            rs.DeleteObjects(rs.ObjectsByLayer(draw_tets))
            rs.CurrentLayer(draw_tets)

            tet_faces = [[0, 2, 1, 1], [1, 2, 3, 3], [1, 3, 0, 0], [0, 3, 2, 2]]

            for i, points in enumerate(tets_elements):

                xyz = [tets_points[j] for j in points]
                rs.AddMesh(vertices=xyz, face_vertices=tet_faces)

            rs.EnableRedraw(True)

        print('***** MeshPy (TetGen) successfull *****')

    except Exception:

        print('***** Error using MeshPy (TetGen) or drawing Tets *****')


def discretise_mesh(mesh, layer, target, min_angle=15, factor=1):
    """
    Discretise a mesh from an input triangulated coarse mesh into small denser meshes.

    Parameters
    ----------
    mesh : guid
        The guid of the Rhino input mesh.
    layer : str
        Layer name to draw results.
    target : float
        Target length of each triangle.
    min_angle : float
        Minimum internal angle of triangles.
    factor : float
        Factor on the maximum area of each triangle.

    Returns
    -------
    None

    """

    rhinomesh = RhinoMesh.from_guid(mesh)
    vertices = rhinomesh.vertices
    faces = [face[:3] for face in rhinomesh.faces]

    try:

        points, tris = meshing.discretise_faces(vertices=vertices, faces=faces,
                                                target=target, min_angle=min_angle, factor=factor)

        rs.CurrentLayer(rs.AddLayer(layer))
        rs.DeleteObjects(rs.ObjectsByLayer(layer))
        rs.EnableRedraw(False)

        for pts, tri in zip(points, tris):
            mesh_faces = []

            for i in tri:
                face_ = i + [i[-1]]
                mesh_faces.append(face_)
            rs.AddMesh(pts, mesh_faces)

        rs.EnableRedraw(True)

    except Exception:

        print('***** Error using MeshPy (Triangle) or drawing faces *****')


def mesh_extrude(structure, guid, layers, thickness, mesh_name='', links_name='', blocks_name='', points_name='',
                 plot_mesh=False, plot_links=False, plot_blocks=False, plot_points=False):
    """
    Extrudes a Rhino mesh and adds/creates elements.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    guid : guid
        Rhino mesh guid.
    layers : int
        Number of layers.
    thickness : float
        Layer thickness.
    mesh_name : str
        Name of set for mesh on final surface.
    links_name : str
        Name of set for adding links along extrusion.
    blocks_name : str
        Name of set for solid elements.
    points_name : str
        Name of aded points.
    plot_mesh : bool
        Plot outer mesh.
    plot_links : bool
        Plot links.
    plot_blocks : bool
        Plot blocks.
    plot_points : bool
        Plot end points.

    Returns
    -------
    None

    Notes
    -----
    - Extrusion is along the mesh vertex normals.

    """

    mesh = RhinoMesh.from_guid(guid).to_compas(cls=Mesh)
    extrude_mesh(structure=structure, mesh=mesh, layers=layers, thickness=thickness, mesh_name=mesh_name,
                 links_name=links_name, blocks_name=blocks_name)

    block_faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    xyz = structure.nodes_xyz()

    rs.EnableRedraw(False)

    if plot_blocks:

        rs.CurrentLayer(rs.AddLayer(blocks_name))
        rs.DeleteObjects(rs.ObjectsByLayer(blocks_name))

        for i in structure.sets[blocks_name]['selection']:
            nodes = structure.elements[i].nodes
            xyz = structure.nodes_xyz(nodes)
            rs.AddMesh(xyz, block_faces)

    if plot_mesh:

        rs.CurrentLayer(rs.AddLayer(mesh_name))
        rs.DeleteObjects(rs.ObjectsByLayer(mesh_name))

        faces = []
        for i in structure.sets[mesh_name]['selection']:
            enodes = structure.elements[i].nodes
            if len(enodes) == 3:
                enodes.append(enodes[-1])
            faces.append(enodes)
        rs.AddMesh(xyz, faces)

    if plot_links:

        rs.CurrentLayer(rs.AddLayer(links_name))
        rs.DeleteObjects(rs.ObjectsByLayer(links_name))

        if plot_points:
            rs.CurrentLayer(rs.AddLayer(points_name))
            rs.DeleteObjects(rs.ObjectsByLayer(points_name))

        for i in structure.sets[links_name]['selection']:

            nodes = structure.elements[i].nodes
            xyz = structure.nodes_xyz(nodes)
            rs.CurrentLayer(links_name)
            rs.AddLine(xyz[0], xyz[1])

            if plot_points:
                rs.CurrentLayer(points_name)
                rs.AddPoint(xyz[1])

    rs.EnableRedraw(True)
    rs.CurrentLayer(rs.AddLayer('Default'))


def network_from_lines(guids=[], layer=None):
    """
    Creates a Network datastructure object from a list of Rhino curve guids.

    Parameters
    ----------
    guids : list
        guids of the Rhino curves to be made into a Network.
    layer : str
        Layer to grab line guids from.

    Returns
    -------
    obj
        Network datastructure object.

    """

    if layer:
        guids = rs.ObjectsByLayer(layer)
    lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids if rs.IsCurve(guid)]

    return Network.from_lines(lines)


def ordered_network(structure, network, layer):
    """
    Extract vertex and edge orders from a Network for a given start-point.

    Parameters
    ----------
    structure : obj
        Structure object.
    network : obj
        Network Datastructure object.
    layer : str
        Layer to extract start-point (Rhino point).
    Returns
    -------
    list
        Ordered nodes for the Structure.
    list
        Ordered elements for the Structure.
    list
        Cumulative length at element mid-points.
    float
        Total length.
    Notes
    -----
    - This function is for a Network representing a single structural element, i.e. with two end-points (leaves).
    """

    start = rs.PointCoordinates(rs.ObjectsByLayer(layer)[0])

    return network_order(start=start, structure=structure, network=network)


def plot_reaction_forces(structure, step, layer=None, scale=1.0):
    """
    Plots reaction forces for the Structure analysis results.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    layer : str
        Layer name for plotting.
    scale : float
        Scale of the arrows.

    Returns
    -------
    None

    """

    if not layer:
        layer = '{0}-{1}'.format(step, 'reactions')

    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    rfx = structure.results[step]['nodal']['rfx']
    rfy = structure.results[step]['nodal']['rfy']
    rfz = structure.results[step]['nodal']['rfz']

    nkeys = rfx.keys()
    v = [scale_vector([rfx[i], rfy[i], rfz[i]], -scale * 0.001) for i in nkeys]
    rm = [length_vector(i) for i in v]
    rmax = max(rm)
    nodes = structure.nodes_xyz(nkeys)

    for i in nkeys:

        if rm[i] > 0.001:
            line = rs.AddLine(nodes[i], add_vectors(nodes[i], v[i]))
            rs.CurveArrows(line, 1)
            col = [int(j) for j in colorbar(rm[i] / rmax, input='float', type=255)]
            rs.ObjectColor(line, col)
            vector = [rfx[i], rfy[i], rfz[i]]
            name = json.dumps({'rfx': rfx[i], 'rfy': rfy[i], 'rfz': rfz[i], 'rfm': length_vector(vector)})
            rs.ObjectName(line, '_' + name)

    rs.CurrentLayer(rs.AddLayer('Default'))
    rs.LayerVisible(layer, False)
    rs.EnableRedraw(True)


def plot_concentrated_forces(structure, step, layer=None, scale=1.0):
    """
    Plots concentrated forces forces for the Structure analysis results.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    layer : str
        Layer name for plotting.
    scale : float
        Scale of the arrows.

    Returns
    -------
    None

    """

    if not layer:
        layer = '{0}-{1}'.format(step, 'forces')
    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    cfx = structure.results[step]['nodal']['cfx']
    cfy = structure.results[step]['nodal']['cfy']
    cfz = structure.results[step]['nodal']['cfz']

    nkeys = cfx.keys()
    v = [scale_vector([cfx[i], cfy[i], cfz[i]], -scale * 0.001) for i in nkeys]
    rm = [length_vector(i) for i in v]
    rmax = max(rm)
    nodes = structure.nodes_xyz(nkeys)

    for i in nkeys:

        if rm[i]:
            line = rs.AddLine(nodes[i], add_vectors(nodes[i], v[i]))
            rs.CurveArrows(line, 1)
            col = [int(j) for j in colorbar(rm[i] / rmax, input='float', type=255)]
            rs.ObjectColor(line, col)
            vector = [cfx[i], cfy[i], cfz[i]]
            name = json.dumps({'cfx': cfx[i], 'cfy': cfy[i], 'cfz': cfz[i], 'cfm': length_vector(vector)})
            rs.ObjectName(line, '_' + name)

    rs.CurrentLayer(rs.AddLayer('Default'))
    rs.LayerVisible(layer, False)
    rs.EnableRedraw(True)


def plot_mode_shapes(structure, step, layer=None, scale=1.0, radius=1):
    """
    Plots modal shapes from structure.results.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    layer : str
        Each mode will be placed in a layer with this string prefix.
    scale : float
        Scale displacements for the deformed plot.
    radius : float
        Radius of the pipe visualisation meshes.

    Returns
    -------
    None

    """

    if not layer:
        layer = step + '_mode_'

    try:
        it = structure.results[step]['frequencies']
    except Exception:
        it = structure.results[step]['info']['description']

    if isinstance(it, list):
        for c, fk in enumerate(it, 1):
            layerk = layer + str(c)
            plot_data(structure=structure, step=step, field='um', layer=layerk, scale=scale, mode=c, radius=radius)

    elif isinstance(it, dict):
        for mode, value in it.items():
            print(mode, value)
            layerk = layer + str(mode)
            plot_data(structure=structure, step=step, field='um', layer=layerk, scale=scale, mode=mode, radius=radius)


def plot_volmesh(volmesh, layer=None, draw_cells=True):
    """
    Plot a volmesh datastructure.

    Parameters
    ----------
    volmesh : obj
        volmesh datastructure object.
    layer : str
        Layer name to draw on.
    draw_cells : bool
        Draw cells.

    Returns
    -------
    None

    """

    if layer:
        rs.CurrentLayer(layer)

    vkeys = sorted(list(volmesh.vertices()), key=int)
    vertices = [volmesh.vertex_coordinates(vkey) for vkey in vkeys]

    if draw_cells:
        meshes = []
        for ckey in volmesh.cell:
            faces = [volmesh.halfface_vertices(fk, ordered=True) for fk in volmesh.cell_halffaces(ckey)]
            meshes.append(rs.AddMesh(vertices, faces))
        return meshes

    else:
        faces = []
        for fk in volmesh.halfface:
            face = volmesh.halfface_vertices(fk, ordered=True)
            faces.append(face)
        mesh = rs.AddMesh(vertices, faces)
        return mesh


def plot_axes(xyz, e11, e22, e33, layer, sc=1):
    """
    Plots a set of axes.

    Parameters
    ----------
    xyz : list
        Origin of the axes.
    e11 : list
        Normalised first axis component [x1, y1, z1].
    e22 : list
        Normalised second axis component [x2, y2, z2].
    e33 : list
        Normalised third axis component [x3, y3, z3].
    layer : str
        Layer to plot on.
    sc : float
         Size of the axis lines.

    Returns
    -------
    None

    """

    ex = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e11, sc)))
    ey = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e22, sc)))
    ez = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e33, sc)))

    rs.ObjectColor(ex, [255, 0, 0])
    rs.ObjectColor(ey, [0, 255, 0])
    rs.ObjectColor(ez, [0, 0, 255])
    rs.ObjectLayer(ex, layer)
    rs.ObjectLayer(ey, layer)
    rs.ObjectLayer(ez, layer)


def plot_data(structure, step, field='um', layer=None, scale=1.0, radius=0.05, cbar=[None, None], iptype='mean',
              nodal='mean', mode='', cbar_size=1):
    """
    Plots analysis results on the deformed shape of the Structure.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    field : str
        Field to plot, e.g. 'um', 'sxx', 'sm1'.
    layer : str
        Layer name for plotting.
    scale : float
        Scale on displacements for the deformed plot.
    radius : float
        Radius of the pipe visualisation meshes.
    cbar : list
        Minimum and maximum limits on the colorbar.
    iptype : str
        'mean', 'max' or 'min' of an element's integration point data.
    nodal : str
        'mean', 'max' or 'min' for nodal values.
    mode : int
        Mode or frequency number to plot, for modal, harmonic or buckling analysis.
    cbar_size : float
        Scale on the size of the colorbar.

    Returns
    -------
    None

    Notes
    -----
    - Pipe visualisation of line elements is not based on the element section.

    """

    if field in ['smaxp', 'smises']:
        nodal = 'max'
        iptype = 'max'

    elif field in ['sminp']:
        nodal = 'min'
        iptype = 'min'

    # Create and clear Rhino layer

    if not layer:
        layer = '{0}-{1}{2}'.format(step, field, mode)

    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    # Node and element data

    nodes = structure.nodes_xyz()
    elements = [structure.elements[i].nodes for i in sorted(structure.elements, key=int)]
    nodal_data = structure.results[step]['nodal']
    nkeys = sorted(structure.nodes, key=int)

    ux = [nodal_data['ux{0}'.format(mode)][i] for i in nkeys]
    uy = [nodal_data['uy{0}'.format(mode)][i] for i in nkeys]
    uz = [nodal_data['uz{0}'.format(mode)][i] for i in nkeys]

    try:
        data = [nodal_data['{0}{1}'.format(field, mode)][i] for i in nkeys]
        dtype = 'nodal'

    except(Exception):
        data = structure.results[step]['element'][field]
        dtype = 'element'

    # Postprocess

    result = functions.postprocess(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, 255, iptype, nodal)

    try:
        toc, U, cnodes, fabs, fscaled, celements, eabs = result
        print('\n***** Data processed : {0} s *****'.format(toc))

        # Plot meshes

        mesh_faces = []
        line_faces = [[0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
        block_faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        tet_faces = [[0, 2, 1, 1], [1, 2, 3, 3], [1, 3, 0, 0], [0, 3, 2, 2]]

        for element, nodes in enumerate(elements):

            n = len(nodes)

            if n == 2:

                u, v = nodes
                sp, ep = U[u], U[v]
                plane = rs.PlaneFromNormal(sp, subtract_vectors(ep, sp))
                xa = plane.XAxis
                ya = plane.YAxis
                r = radius
                xa_pr = scale_vector(xa, +r)
                xa_mr = scale_vector(xa, -r)
                ya_pr = scale_vector(ya, +r)
                ya_mr = scale_vector(ya, -r)
                pts = [add_vectors(sp, xa_pr), add_vectors(sp, ya_pr),
                       add_vectors(sp, xa_mr), add_vectors(sp, ya_mr),
                       add_vectors(ep, xa_pr), add_vectors(ep, ya_pr),
                       add_vectors(ep, xa_mr), add_vectors(ep, ya_mr)]
                guid = rs.AddMesh(pts, line_faces)

                if dtype == 'element':
                    col1 = col2 = celements[element]

                elif dtype == 'nodal':
                    col1 = cnodes[u]
                    col2 = cnodes[v]

                rs.MeshVertexColors(guid, [col1] * 4 + [col2] * 4)

            elif n == 3:

                mesh_faces.append(nodes + [nodes[-1]])

            elif n == 4:

                if structure.elements[element].__name__ in ['ShellElement', 'MembraneElement']:
                    mesh_faces.append(nodes)
                else:
                    for face in tet_faces:
                        mesh_faces.append([nodes[i] for i in face])

            elif n == 8:

                for block in block_faces:
                    mesh_faces.append([nodes[i] for i in block])

        if mesh_faces:
            guid = rs.AddMesh(U, mesh_faces)
            rs.MeshVertexColors(guid, cnodes)

        # Plot colorbar

        xr, yr, _ = structure.node_bounds()
        yran = yr[1] - yr[0] if yr[1] - yr[0] else 1
        s = yran * 0.1 * cbar_size
        xmin = xr[1] + 3 * s
        ymin = yr[0]

        xl = [xmin, xmin + s]
        yl = [ymin + i * s for i in range(11)]
        verts = [[xi, yi, 0] for xi in xl for yi in yl]
        faces = [[i, i + 1, i + 12, i + 11] for i in range(10)]
        id = rs.AddMesh(verts, faces)

        y = [i[1] for i in verts]
        yn = yran * cbar_size
        colors = [colorbar(2 * (yi - ymin - 0.5 * yn) / yn, input='float', type=255) for yi in y]
        rs.MeshVertexColors(id, colors)

        h = 0.4 * s

        for i in range(5):

            x0 = xmin + 1.2 * s
            yu = ymin + (5.8 + i) * s
            yl = ymin + (3.8 - i) * s
            vu = float(+max(eabs, fabs) * (i + 1) / 5.)
            vl = float(-max(eabs, fabs) * (i + 1) / 5.)
            rs.AddText('{0:.5g}'.format(vu), [x0, yu, 0], height=h)
            rs.AddText('{0:.5g}'.format(vl), [x0, yl, 0], height=h)

        rs.AddText('0', [x0, ymin + 4.8 * s, 0], height=h)
        rs.AddText('Step:{0}   Field:{1}'.format(step, field), [xmin, ymin + 12 * s, 0], height=h)

        if mode != '':
            try:
                freq = str(round(structure.results[step]['frequencies'][mode - 1], 3))
                rs.AddText('Mode:{0}   Freq:{1}Hz'.format(mode, freq), [xmin, ymin - 1.5 * s, 0], height=h)
            except Exception:
                pass

        # Return to Default layer

        rs.CurrentLayer(rs.AddLayer('Default'))
        rs.LayerVisible(layer, False)
        rs.EnableRedraw(True)

    except Exception:

        print('\n***** Error encountered during data processing or plotting *****')


def plot_principal_stresses(structure, step, sp, stype, scale, layer=None):
    """
    Plots the principal stresses of the elements.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    sp : str
        'sp1' or 'sp5' for stection point 1 or 5.
    stype : str
        'max' or 'min' for maximum or minimum principal stresses.
    scale : float
        Scale on the length of the line markers (usually 10^6).
    layer : str
        Layer name for plotting.

    Returns
    -------
    None

    Notes
    -----
    - Centroids are taken on the undeformed geometry.

    """

    data = structure.results[step]['element']
    axes = data['axes']
    spr, e = functions.principal_stresses(data)

    stresses = spr[sp][stype]
    max_stress = max([abs(i) for i in stresses])
    vectors = list(zip([e[sp][stype][0][i]*stresses[i]/scale for i in range(len(stresses))],
                       [e[sp][stype][1][i]*stresses[i]/scale for i in range(len(stresses))]))

    if not layer:
        layer = '{0}_{1}_principal_{2}'.format(step, sp, stype)
    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    centroids = [structure.element_centroid(i) for i in sorted(structure.elements, key=int)]

    for c, centroid in enumerate(centroids):
        f2 = Frame(centroid, axes[c][0], axes[c][1])
        T = Transformation.from_frame(f2)
        v_plus = Vector(vectors[c][0]*0.5, vectors[c][1]*0.5, 0.).transformed(T)
        v_minus = Vector(-vectors[c][0]*0.5, -vectors[c][1]*0.5, 0.).transformed(T)
        id1 = rs.AddLine(add_vectors(centroid, v_minus), add_vectors(centroid, v_plus))
        col1 = colorbar(stresses[c] / max_stress, input='float', type=255)
        rs.ObjectColor(id1, col1)
    rs.EnableRedraw(True)


def plot_voxels(structure, step, field='smises', cbar=[None, None], iptype='mean', nodal='mean', vdx=None, mode=''):
    """
    Voxel 4D visualisation.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    field : str
        Field to plot, e.g. 'smises'.
    cbar : list
        Minimum and maximum limits on the colorbar.
    iptype : str
        'mean', 'max' or 'min' of an element's integration point data.
    nodal : str
        'mean', 'max' or 'min' for nodal values.
    vdx : float
        Voxel spacing.
    mode : int
        mode or frequency number to plot, in case of modal, harmonic or buckling analysis.

    Returns
    -------
    None

    """

    # Node and element data

    xyz = structure.nodes_xyz()
    elements = [structure.elements[i].nodes for i in sorted(structure.elements, key=int)]
    nodal_data = structure.results[step]['nodal']
    nkeys = sorted(structure.nodes, key=int)

    ux = [nodal_data['ux{0}'.format(mode)][i] for i in nkeys]
    uy = [nodal_data['uy{0}'.format(mode)][i] for i in nkeys]
    uz = [nodal_data['uz{0}'.format(mode)][i] for i in nkeys]

    try:
        data = [nodal_data[field + str(mode)][key] for key in nkeys]
        dtype = 'nodal'

    except(Exception):
        data = structure.results[step]['element'][field]
        dtype = 'element'

    # Postprocess

    result = functions.postprocess(xyz, elements, ux, uy, uz, data, dtype, 1, cbar, 255, iptype, nodal)

    try:
        toc, U, cnodes, fabs, fscaled, celements, eabs = result
        print('\n***** Data processed : {0} s *****'.format(toc))

    except Exception:
        print('\n***** Error post-processing *****')

    try:
        functions.plotvoxels(values=fscaled, U=U, vdx=vdx)
        print('\n***** Voxels finished *****')

    except Exception:
        print('\n***** Error plotting voxels *****')


def weld_meshes_from_layer(layer_input, layer_output):
    """
    Grab meshes on an input layer and weld them onto an output layer.

    Parameters
    ----------
    layer_input : str
        Layer containing the Rhino meshes to weld.
    layer_output : str
        Layer to plot single welded mesh.

    Returns
    -------
    None

    """

    print('Welding meshes on layer:{0}'.format(layer_input))

    mdl = Structure(path=' ')

    add_nodes_elements_from_layers(mdl, mesh_type='ShellElement', layers=layer_input)

    faces = []

    for element in mdl.elements.values():
        enodes = element.nodes

        if len(enodes) == 3:
            enodes.append(enodes[-1])

        if len(enodes) == 4:
            faces.append(enodes)

    rs.DeleteObjects(rs.ObjectsByLayer(layer_output))
    rs.CurrentLayer(layer_output)
    rs.AddMesh(mdl.nodes_xyz(), faces)

# ==============================================================================
# Debugging
# ==============================================================================


if __name__ == "__main__":

    pass
