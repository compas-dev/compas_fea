
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures.mesh import Mesh
from compas.datastructures import Network
from compas.utilities import XFunc

try:
    from compas_rhino.geometry import RhinoMesh
    from compas_rhino.helpers.mesh import mesh_from_guid
except:
    pass

from compas.geometry import add_vectors
from compas.geometry import cross_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_fea import utilities
from compas_fea.utilities import colorbar
from compas_fea.utilities import extrude_mesh
from compas_fea.utilities import network_order

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.system() == 'Windows':
        raise

import json


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'add_element_set',
    'add_tets_from_mesh',
    'add_node_set',
    'discretise_mesh',
    'add_nodes_elements_from_layers',
    'add_sets_from_layers',
    'mesh_extrude',
    'network_from_lines',
    'ordered_network',
    'plot_axes',
    'plot_mode_shapes',
    'plot_data',
    'plot_voxels',
    'plot_principal_stresses',
]


def add_element_set(structure, guids, name):

    """ Adds element set information from Rhino curve and mesh guids.

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
            faces    = rs.MeshFaceVertices(guid)

            if rs.ObjectName(guid) and ('solid' in rs.ObjectName(guid)):
                nodes   = [structure.check_node_exists(i) for i in vertices]
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

    """ Adds node set information from Rhino point guids.

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


def add_nodes_elements_from_layers(structure, layers, line_type=None, mesh_type=None, thermal=False):

    """ Adds node and element data from Rhino layers to the Structure object.

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

    Returns
    -------
    list
        Node keys that were added to the Structure.
    list
        Element keys that were added to the Structure.

    """

    if isinstance(layers, str):
        layers = [layers]

    added_nodes    = set()
    added_elements = set()

    for layer in layers:

        elset = set()

        for guid in rs.ObjectsByLayer(layer):

            if line_type and rs.IsCurve(guid):

                sp_xyz = rs.CurveStartPoint(guid)
                ep_xyz = rs.CurveEndPoint(guid)
                sp = structure.add_node(sp_xyz)
                ep = structure.add_node(ep_xyz)
                added_nodes.add(sp)
                added_nodes.add(ep)

                ez = subtract_vectors(ep_xyz, sp_xyz)
                try:
                    name = rs.ObjectName(guid).replace("'", '"')
                    if name[0] in ['_', '^']:
                        name = name[1:]
                    dic = json.loads(name)
                    ex  = dic.get('ex', None)
                    ey  = dic.get('ey', None)
                    if ex and not ey:
                        ey = cross_vectors(ex, ez)
                except:
                    ex = None
                    ey = None
                axes = {'ex': ex, 'ey': ey, 'ez': ez}

                ekey = structure.add_element(nodes=[sp, ep], type=line_type, thermal=thermal, axes=axes)
                if ekey is not None:
                    added_elements.add(ekey)
                    elset.add(ekey)

            elif mesh_type and rs.IsMesh(guid):

                vertices = rs.MeshVertices(guid)
                nodes = [structure.add_node(vertex) for vertex in vertices]
                added_nodes.update(nodes)

                if mesh_type in ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']:
                    ekey = structure.add_element(nodes=nodes, type=mesh_type, thermal=thermal)
                    if ekey is not None:
                        added_elements.add(ekey)
                        elset.add(ekey)

                else:
                    try:
                        name = rs.ObjectName(guid).replace("'", '"')
                        if name[0] in ['_', '^']:
                            name = name[1:]
                        dic = json.loads(name)
                        ex  = dic.get('ex', None)
                        ey  = dic.get('ey', None)
                        ez  = dic.get('ez', None)
                        if (ex and ey) and (not ez):
                            ez = cross_vectors(ex, ey)
                    except:
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

    """ Add node and element sets to the Structure object from Rhino layers.

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


def network_from_lines(guids=[], layer=None):

    """ Creates a Network datastructure object from a list of Rhino curve guids.

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

    """ Extract vertex and edge orders from a Network for a given start-point.

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






























def discretise_mesh(structure, guid, layer, target, min_angle=15, factor=1, iterations=50, refine=True):

    """ Discretise a mesh from an input coarse mesh guid into small denser meshes.

    Parameters
    ----------
    structure : obj
        Structure object.
    guid : str
        guid of the Rhino input mesh.
    layer : str
        Layer name to plot resulting meshes on.
    target : float
        Target length of each triangle.
    min_angle : float
        Minimum internal angle of triangles.
    factor : float
        Factor on the maximum area of each triangle.
    iterations : int
        Number of iterations per face.
    refine : bool
        Refine beyond Delaunay.

    Returns
    -------
    None

    """

    rhinomesh = RhinoMesh(guid)
    pts = rhinomesh.get_vertex_coordinates()
    fcs = [face[:3] for face in rhinomesh.get_face_vertices()]

    path = structure.path
    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc('discretise', basedir=basedir, tmpdir=path)
    xfunc.funcname = 'functions.discretise_faces'

    try:
        vertices, faces = xfunc(vertices=pts, faces=fcs, target=target, min_angle=min_angle, factor=factor,
                                iterations=iterations, refine=refine)

        rs.CurrentLayer(rs.AddLayer(layer))
        rs.DeleteObjects(rs.ObjectsByLayer(layer))
        rs.EnableRedraw(False)

        for points, face in zip(vertices, faces):
            mesh_faces = []
            for i in face:
                face_ = i + [i[-1]]
                mesh_faces.append(face_)
            rs.AddMesh(points, mesh_faces)

        rs.EnableRedraw(True)

    except:
        '***** Mesh discretisation failed *****'


def add_tets_from_mesh(structure, name, mesh, draw_tets=False, volume=None, layer='Default', acoustic=False,
                       thermal=False):

    """ Adds tetrahedron elements from a Rhino mesh to the Structure object.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    name : str
        Name for the element set of tetrahedrons.
    mesh : obj
        The Rhino mesh representing the outer surface.
    draw_tets : bool
        Draw the generated tetrahedrons.
    volume : float
        Maximum volume for each tet.
    layer : str
        Layer to draw tetrahedrons if draw_tets=True.
    acoustic : bool
        Acoustic properties on or off.
    thermal : bool
        Thermal properties on or off.

    Returns
    -------
    None
        Nodes and elements are updated in the Structure object.

    """

    rhinomesh = RhinoMesh(mesh)
    vertices = rhinomesh.get_vertex_coordinates()
    faces = [face[:3] for face in rhinomesh.get_face_vertices()]

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc('tets', basedir=basedir, tmpdir=structure.path)
    xfunc.funcname = 'functions.tets_from_vertices_faces'

    try:
        tets_points, tets_elements = xfunc(vertices=vertices, faces=faces, volume=volume)

        for point in tets_points:
            structure.add_node(point)

        ekeys = []
        for element in tets_elements:
            nodes = [structure.check_node_exists(tets_points[i]) for i in element]
            ekey = structure.add_element(nodes=nodes, type='TetrahedronElement', acoustic=acoustic, thermal=thermal)
            ekeys.append(ekey)
        structure.add_set(name=name, type='element', selection=ekeys)

        if draw_tets:
            rs.EnableRedraw(False)
            rs.DeleteObjects(rs.ObjectsByLayer(layer))
            rs.CurrentLayer(layer)
            tet_faces = [[0, 2, 1, 1], [1, 2, 3, 3], [1, 3, 0, 0], [0, 3, 2, 2]]
            for i, points in enumerate(tets_elements):
                xyz = [tets_points[j] for j in points]
                rs.AddMesh(vertices=xyz, face_vertices=tet_faces)
        rs.EnableRedraw(True)

    except:
        print('***** Error using MeshPy or drawing Tets *****')


def mesh_extrude(structure, guid, layers, thickness, mesh_name='', links_name='', blocks_name='',
                 plot_blocks=False, plot_mesh=False, plot_links=False):

    """ Extrudes a Rhino mesh and adds/creates elements.

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
    blocks_name : str
        Name of set for solid elements.
    mesh_name : str
        Name of set for mesh on final surface.
    links_name : str
        Name of set for adding links along extrusion.
    plot_blocks : bool
        Plot blocks.
    plot_mesh : bool
        Plot outer mesh.
    plot_links : bool
        Plot links.

    Returns
    -------
    None

    Notes
    -----
    - Extrusion is along the vertex normals.

    """

    mesh = mesh_from_guid(Mesh(), guid)
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

        for i in structure.sets[links_name]['selection']:
            nodes = structure.elements[i].nodes
            xyz = structure.nodes_xyz(nodes)
            rs.AddLine(xyz[0], xyz[1])

    rs.EnableRedraw(True)
    rs.CurrentLayer(rs.AddLayer('Default'))


def plot_axes(xyz, e11, e22, e33, layer, sc=1):

    """ Plots a set of axes.

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


def plot_mode_shapes(structure, step, layer=None, scale=1.0):

    """ Plots modal shapes from structure.results.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    layer : str
        Each mode will be placed in a layer with this string as its base.
    scale : float
        Scale displacements for the deformed plot.

    Returns
    -------
    None

    """

    iter = structure.results[step]['frequencies']
    for c, fk in enumerate(iter, 1):
        layerk = layer + str(c)
        plot_data(structure=structure, step=step, field='um', layer=layerk, scale=scale, mode=c)


def plot_data(structure, step, field='um', layer=None, scale=1.0, radius=0.05, cbar=[None, None], iptype='mean',
              nodal='mean', mode='', colorbar_size=1):

    """ Plots analysis results on the deformed shape of the Structure.

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
    colorbar_size : float
        Scale on the size of the colorbar.

    Returns
    -------
    None

    Notes
    -----
    - Pipe visualisation of line elements is not based on the element section.

    """

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

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc('postprocess', basedir=basedir, tmpdir=structure.path)
    xfunc.funcname = 'functions.postprocess'
    result = xfunc(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, 255, iptype, nodal)

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
        s = yran * 0.1 * colorbar_size
        xmin = xr[1] + 3 * s
        ymin = yr[0]

        xl = [xmin, xmin + s]
        yl = [ymin + i * s for i in range(11)]
        verts = [[xi, yi, 0] for xi in xl for yi in yl]
        faces = [[i, i + 1, i + 12, i + 11] for i in range(10)]
        id = rs.AddMesh(verts, faces)

        y = [i[1] for i in verts]
        yn = yran * colorbar_size
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
            except:
                pass

        # Return to Default layer

        rs.CurrentLayer(rs.AddLayer('Default'))
        rs.LayerVisible(layer, False)
        rs.EnableRedraw(True)

    except:
        print('\n***** Error encountered during data processing or plotting *****')


def plot_voxels(structure, step, field='smises', cbar=[None, None], iptype='mean', nodal='mean',
                vdx=None, mode='', plot='vtk'):

    """ Voxel 4D visualisation.

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
    plot : str
        Plot voxels with 'vtk'.

    Returns
    -------
    None

    """

    # Node and element data

    nodes = structure.nodes_xyz()
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

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc('postprocess', basedir=basedir, tmpdir=structure.path)
    xfunc.funcname = 'functions.postprocess'
    result = xfunc(nodes, elements, ux, uy, uz, data, dtype, 1, cbar, 255, iptype, nodal)

    try:
        toc, U, cnodes, fabs, fscaled, celements, eabs = result
        print('\n***** Data processed : {0} s *****'.format(toc))

    except:
        print('\n***** Error post-processing *****')

    try:
        xfunc = XFunc('voxels', basedir=basedir, tmpdir=structure.path)
        xfunc.funcname = 'functions.plotvoxels'
        xfunc(values=fscaled, U=U, vdx=vdx, plot=plot)
        print('\n***** Voxels finished *****')

    except:
        print('\n***** Error plotting voxels *****')


def plot_principal_stresses(structure, step, ptype, scale, rotate=0, layer=None):

    """ Plots the principal stresses of the elements.

    Parameters
    ----------
    structure : obj
        Structure object.
    step : str
        Name of the Step.
    ptype : str
        'max' 'min' for maximum or minimum principal stresses.
    scale : float
        Scale on the length of the line markers.
    rotate : int
        Rotate lines by 90 deg, 0 or 1.
    layer : str
        Layer name for plotting.

    Returns
    -------
    None

    Notes
    -----
    - Currently an alpha script and only for triangular shell elements in Abaqus.
    - Centroids are taken on the undeformed geometry.

    """

    data = structure.results[step]['element']
    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc('principal_stresses', basedir=basedir, tmpdir=structure.path)
    xfunc.funcname = 'functions.principal_stresses'
    result = xfunc(data, ptype, scale, rotate)

    try:
        vec1, vec5, pr1, pr5 = result

        if not layer:
            layer = '{0}_principal_{1}'.format(step, ptype)
        rs.CurrentLayer(rs.AddLayer(layer))
        rs.DeleteObjects(rs.ObjectsByLayer(layer))
        centroids = [structure.element_centroid(i) for i in sorted(structure.elements, key=int)]

        rs.EnableRedraw(False)

        for c, centroid in enumerate(centroids):
            v1 = vec1[c]
            v5 = vec5[c]
            id1 = rs.AddLine(add_vectors(centroid, scale_vector(v1, -1)), add_vectors(centroid, v1))
            id5 = rs.AddLine(add_vectors(centroid, scale_vector(v5, -1)), add_vectors(centroid, v5))
            col1 = [255, 0, 0] if pr1[c] > 0 else [0, 0, 255]
            col5 = [255, 0, 0] if pr5[c] > 0 else [0, 0, 255]
            rs.ObjectColor(id1, col1)
            rs.ObjectColor(id5, col5)

        rs.EnableRedraw(True)

    except:
        print('\n***** Error calculating/plotting principal stresses *****')
