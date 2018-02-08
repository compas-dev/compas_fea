"""
compas_fea.cad.rhino : Rhinoceros specific functions.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas.utilities import XFunc

from compas.datastructures.mesh import Mesh
from compas.datastructures import Network

from compas_rhino.helpers.mesh import mesh_from_guid
from compas_rhino.utilities import clear_layer
from compas_rhino.geometry import RhinoMesh

from compas.geometry import add_vectors
from compas.geometry import centroid_points
from compas.geometry import cross_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_fea import utilities
from compas_fea.utilities import colorbar
from compas_fea.utilities import extrude_mesh
from compas_fea.utilities import network_order

from math import atan2
from math import cos
from math import sin
from math import pi

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.system() == 'Windows':
        raise

import json


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'add_element_set',
    'add_tets_from_mesh',
    'add_node_set',
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


def add_element_set(structure, guids, name, explode=False):
    """ Adds element set information from Rhino curve and mesh guids.

    Note:
        - Meshes representing solids must have 'solid' in their name.

    Parameters
    ----------
        structure (obj): Structure object to update.
        guids (list): Rhino curve and Rhino mesh guids.
        name (str): Set name.
        explode (bool): Explode the set into sets for each member of selection.

    Returns
    -------
        None
    """
    elements = []
    for guid in guids:

        if rs.IsCurve(guid):
            sp = structure.check_node_exists(rs.CurveStartPoint(guid))
            ep = structure.check_node_exists(rs.CurveEndPoint(guid))
            element = structure.check_element_exists([sp, ep])
            if element is not None:
                        elements.append(element)

        if rs.IsMesh(guid):
            vertices = rs.MeshVertices(guid)
            faces = rs.MeshFaceVertices(guid)

            if 'solid' in rs.ObjectName(guid):
                nodes = [structure.check_node_exists(i) for i in vertices]
                element = structure.check_element_exists(nodes)
                if element is not None:
                    elements.append(element)

            else:
                for face in faces:
                    nodes = [structure.check_node_exists(vertices[i]) for i in face]
                    if nodes[2] == nodes[3]:
                        nodes = nodes[:-1]
                    element = structure.check_element_exists(nodes)
                    if element is not None:
                        elements.append(element)

    structure.add_set(name=name, type='element', selection=elements, explode=explode)


def add_tets_from_mesh(structure, name, mesh, draw_tets=False, volume=None, layer='Default', acoustic=False, thermal=False):
    """ Adds tetrahedron elements from a Rhino mesh to the Structure object.

    Parameters
    ----------
        structure (obj): Structure object to update.
        name (str): Name for the element set of tetrahedrons.
        mesh (ob): The Rhino mesh representing the outer surface.
        draw_tets (bool): Draw the generated tetrahedrons.
        volume (float): Maximum volume for tets.
        layer (str): Layer to draw tetrahedrons if draw_tets=True.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns
    -------
        None: Nodes and elements are updated in the Structure object.
    """
    rhinomesh = RhinoMesh(mesh)
    vertices = rhinomesh.get_vertex_coordinates()
    faces = [face[:3] for face in rhinomesh.get_face_vertices()]

    path = structure.path

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc(basedir=basedir, tmpdir=path, mode=1)
    xfunc.funcname = 'functions.tets_from_vertices_faces'
    result = xfunc(vertices=vertices, faces=faces, volume=volume)

    if result['error']:
        print(result['error'])
        print('\n***** Error using MeshPy *****')
    else:
        tets_points, tets_elements = result['data']

    for point in tets_points:
        structure.add_node(point)
    ekeys = []
    for element in tets_elements:
        nodes = [structure.check_node_exists(tets_points[i]) for i in element]
        ekey = structure.add_element(nodes=nodes, type='TetrahedronElement', acoustic=acoustic, thermal=thermal)
        ekeys.append(ekey)
    structure.add_set(name=name, type='element', selection=ekeys, explode=False)

    rs.EnableRedraw(False)
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.CurrentLayer(layer)
    if draw_tets:
        tet_faces = [[0, 2, 1, 1], [1, 2, 3, 3], [1, 3, 0, 0], [0, 3, 2, 2]]
        for i, points in enumerate(tets_elements):
            xyz = [tets_points[j] for j in points]
            rs.AddMesh(vertices=xyz, face_vertices=tet_faces)
    rs.EnableRedraw(True)


def add_node_set(structure, guids, name, explode=False):
    """ Adds node set information from Rhino point guids.

    Parameters
    ----------
        structure (obj): Structure object to update.
        guids (list): Rhino point guids.
        name (str): Set name.
        explode (bool): Explode the set into sets for each member of selection.

    Returns
    -------
        None
    """
    nodes = []
    for guid in guids:

        node = structure.check_node_exists(rs.PointCoordinates(guid))

        if node is not None:
            nodes.append(node)

    structure.add_set(name=name, type='node', selection=nodes, explode=explode)


def add_nodes_elements_from_layers(structure, layers, line_type=None, mesh_type=None, acoustic=False, thermal=False):
    """ Adds node and element data from Rhino layers to Structure object.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    layers : list
        Layers to extract nodes and elements.
    line_type : str
        Element type for lines.
    mesh_type : str
        Element type for meshes.
    acoustic : bool
        Acoustic properties on or off.
    thermal : bool
        Thermal properties on or off.

    Returns
    -------
    list
        Node keys that were added to the Structure.
    list
        Element keys that were added to the Structure.
    """
    solids = ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']

    if isinstance(layers, str):
        layers = [layers]

    created_nodes = set()
    created_elements = set()

    for layer in layers:
        for guid in rs.ObjectsByLayer(layer):

            if line_type and rs.IsCurve(guid):

                sp_xyz = rs.CurveStartPoint(guid)
                ep_xyz = rs.CurveEndPoint(guid)
                sp = structure.add_node(sp_xyz)
                ep = structure.add_node(ep_xyz)
                created_nodes.add(sp)
                created_nodes.add(ep)

                ez = subtract_vectors(ep_xyz, sp_xyz)
                try:
                    dic = json.loads(rs.ObjectName(guid).replace("'", '"'))
                    ex = dic.get('ex', None)
                    ey = dic.get('ey', None)
                    if ex and not ey:
                        ey = cross_vectors(ex, ez)
                except:
                    ex = None
                    ey = None
                axes = {'ex': ex, 'ey': ey, 'ez': ez}

                sp_ep = [sp, ep]
                e = structure.add_element(nodes=sp_ep, type=line_type, acoustic=acoustic, thermal=thermal, axes=axes)
                created_elements.add(e)

            elif mesh_type and rs.IsMesh(guid):

                vertices = rs.MeshVertices(guid)
                nodes = [structure.add_node(vertex) for vertex in vertices]
                created_nodes.update(nodes)

                if mesh_type in solids:
                    e = structure.add_element(nodes=nodes, type=mesh_type, acoustic=acoustic, thermal=thermal)
                    created_elements.add(e)

                else:
                    try:
                        dic = json.loads(rs.ObjectName(guid).replace("'", '"'))
                        ex = dic.get('ex', None)
                        ey = dic.get('ey', None)
                        if ex and ey:
                            ez = cross_vectors(ex, ey)
                        else:
                            ez = None
                    except:
                        ex = None
                        ey = None
                        ez = None
                    axes = {'ex': ex, 'ey': ey, 'ez': ez}

                    for face in rs.MeshFaceVertices(guid):
                        nodes = [structure.check_node_exists(vertices[i]) for i in face]
                        if nodes[-1] == nodes[-2]:
                            del nodes[-1]
                        e = structure.add_element(nodes=nodes, type=mesh_type, acoustic=acoustic, thermal=thermal,
                                                  axes=axes)
                        created_elements.add(e)

    return list(created_nodes), list(created_elements)


def add_sets_from_layers(structure, layers, explode=False):
    """ Add node or element sets to the Structure object from Rhino layers.

    Note:
        - Layers should exclusively contain nodes or elements.
        - Sets will inherit the layer names as their keys.

    Parameters
    ----------
        structure (obj): Structure object to update.
        layers (list): List of layer names to take objects from.
        explode (bool): Explode the set into sets for each member of selection.

    Returns
    -------
        None
    """
    if isinstance(layers, str):
        layers = [layers]

    for layer in layers:
        guids = rs.ObjectsByLayer(layer)
        if guids:
            check_points = [rs.IsPoint(guid) for guid in guids]
            name = layer.split('::')[-1] if '::' in layer else layer

            if all(check_points):
                add_node_set(structure=structure, guids=guids, name=name, explode=explode)

            elif not all(check_points):
                add_element_set(structure=structure, guids=guids, name=name, explode=explode)


def mesh_extrude(structure, guid, nz, dz, setname):
    """ Extrudes a Rhino mesh into cells of many layers and adds to Structure.

    Note:
        - Extrusion is along the vertex normals.
        - Elements are added automatically to the Structure object.

    Parameters
    ----------
        structure (obj): Structure object to update.
        guid (guid): Rhino mesh guid.
        nz (int): Number of layers.
        dz (float): Layer thickness.
        setname (str): Name of set for added elements.

    Returns
    -------
        None
    """
    mesh = mesh_from_guid(Mesh(), guid)
    extrude_mesh(structure=structure, mesh=mesh, nz=nz, dz=dz, setname=setname)


def network_from_lines(guids=[], layer=None):
    """ Creates a Network datastructure object from a list of curve guids.

    Parameters
    ----------
        guids (list): guids of the Rhino curves to be made into a Network.
        layer(str): Layer to grab line guids from.

    Returns
    -------
        obj: Network datastructure object.
    """
    if layer:
        guids = rs.ObjectsByLayer(layer)
    lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
    return Network.from_lines(lines)


def ordered_network(structure, network, layer):
    """ Extract node and element orders from a Network for a given start-point.

    Note:
        - Function is for a Network representing a single structural element.

    Parameters
    ----------
        structure (obj): Structure object.
        network (obj): Network object.
        layer (str): Layer to extract start-point (Rhino point).

    Returns
    -------
        list: Ordered nodes.
        list: Ordered elements.
        list: Cumulative lengths at element mid-points.
        float: Total length.
    """
    sp_xyz = rs.PointCoordinates(rs.ObjectsByLayer(layer)[0])
    return network_order(sp_xyz=sp_xyz, structure=structure, network=network)


def plot_axes(xyz, e11, e22, e33, layer, sc=1):
    """ Plots a set of axes.

    Parameters
    ----------
        xyz (list): Origin of the axes.
        e11 (list): First axis component [x1, y1, z1].
        e22 (list): Second axis component [x2, y2, z2].
        e33 (list): Third axis component [x3, y3, z3].
        layer (str): Layer to plot on.
        sc (float) : Size of the axis lines.

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
    """Plots modal shapes from structure.results

    Parameters
    ----------
        structure (obj): Structure object.
        step (str): Name of the Step.
        layer (str): Each mode will be placed in a layer with this string as its base.
        scale (float): Scale displacements for the deformed plot.

    Returns
    -------
        None
        """
    freq = structure.results[step]['frequencies']
    for fk in freq:
        layerk = layer + str(fk)
        plot_data(structure=structure, step=step, field='um', layer=layerk, scale=scale, mode=fk)


def plot_data(structure, step, field='um', layer=None, scale=1.0, radius=0.05, cbar=[None, None], iptype='mean',
              nodal='mean', mode='', colorbar_size=1):
    """ Plots analysis results on the deformed shape of the Structure.

    Note:
        - Pipe visualisation of line elements is not based on the element section.

    Parameters
    ----------
        structure (obj): Structure object.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'um', 'sxx', 'sm1'.
        layer (str): Layer name for plotting.
        scale (float): Scale displacements for the deformed plot.
        radius (float): Radius of the pipe visualisation meshes.
        cbar (list): Minimum and maximum limits on the colorbar.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        mode (int): mode or frequency number to plot, in case of modal, harmonic or buckling analysis.
        colorbar_size (float): Scale on the size of the colorbar.

    Returns
    -------
        None
    """

    path = structure.path

    # Create and clear Rhino layer

    if not layer:
        layer = '{0}-{1}'.format(step, field)
    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    # Node and element data

    nkeys = sorted(structure.nodes, key=int)
    nodes = [structure.node_xyz(nkey) for nkey in nkeys]

    ekeys = sorted(structure.elements, key=int)
    elements = [structure.elements[ekey].nodes for ekey in ekeys]

    nodal_data = structure.results[step]['nodal']
    ux = [nodal_data['ux{0}'.format(str(mode))][key] for key in nkeys]
    uy = [nodal_data['uy{0}'.format(str(mode))][key] for key in nkeys]
    uz = [nodal_data['uz{0}'.format(str(mode))][key] for key in nkeys]

    # Postprocess

    try:
        data = [nodal_data[field + str(mode)][key] for key in nkeys]
        dtype = 'nodal'
    except(Exception):
        elemental_data = structure.results[step]['element']
        data = elemental_data[field]
        dtype = 'element'

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc(funcname='functions.postprocess', basedir=basedir, tmpdir=path)
    result = xfunc(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, 255, iptype, nodal)

    try:
        toc, U, cnodes, fabs = result
        print('\n***** Data processed : {0} s *****'.format(toc))

        # Plot meshes

        mesh_faces = []
        beam_faces = [[0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
        block_faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]

        for nodes in elements:
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
                guid = rs.AddMesh(pts, beam_faces)
                col1 = cnodes[u]
                col2 = cnodes[v]
                rs.MeshVertexColors(guid, [col1] * 4 + [col2] * 4)

            elif n == 3:
                mesh_faces.append(nodes + [nodes[-1]])

            elif n == 4:
                mesh_faces.append(nodes)

            elif n == 8:
                for block in block_faces:
                    mesh_faces.append([nodes[i] for i in block])

        if mesh_faces:
            guid = rs.AddMesh(U, mesh_faces)
            rs.MeshVertexColors(guid, cnodes)

        # Plot colorbar

        xr, yr, _ = structure.node_bounds()
        yran = yr[1] - yr[0]
        if not yran:
            yran = 1
        s = yran * 0.1 * colorbar_size
        xmin = xr[1] + 3 * s
        ymin = yr[0]

        xl = [xmin, xmin + s]
        yl = [ymin + i * s for i in range(11)]
        vertices = [[xi, yi, 0] for xi in xl for yi in yl]
        faces = [[i, i + 1, i + 12, i + 11] for i in range(10)]
        y = [i[1] for i in vertices]

        yn = yran * colorbar_size
        colors = [colorbar(2 * (yi - ymin - 0.5 * yn) / yn, input='float', type=255) for yi in y]
        id = rs.AddMesh(vertices, faces)
        rs.MeshVertexColors(id, colors)

        h = 0.6 * s
        for i in range(5):
            x0 = xmin + 1.2 * s
            yu = ymin + (5.8 + i) * s
            yl = ymin + (3.8 - i) * s
            valu = float(+fabs * (i + 1) / 5.)
            vall = float(-fabs * (i + 1) / 5.)
            rs.AddText('{0:.5g}'.format(valu), [x0, yu, 0], height=h)
            rs.AddText('{0:.5g}'.format(vall), [x0, yl, 0], height=h)
            rs.AddText('0', [x0, ymin + 4.8 * s, 0], height=h)
        rs.AddText('Step:{0}   Field:{1}'.format(step, field), [xmin, ymin + 12 * s, 0], height=h)
        if mode != '':
            freq = str(round(structure.results[step]['frequencies'][mode], 3))
            rs.AddText('Mode:{0}   Freq:{1}Hz'.format(mode, freq), [xmin, ymin - 1.5 * s, 0], height=h)

        # Return to Default layer

        rs.CurrentLayer(rs.AddLayer('Default'))
        rs.LayerVisible(layer, False)
        rs.EnableRedraw(True)
        
    except:
        print('\n***** Error during post-processing *****')


def plot_voxels(structure, step, field='smises', layer=None, scale=1.0, cbar=[None, None], iptype='mean', nodal='mean',
                vmin=0, vdx=None):
    """ Plots voxels results for 4D data with mayavi.

    Parameters
    ----------
        structure (obj): Structure object.
        step (str): Name of the Step.
        field (str): Scalar field to plot, e.g. 'smises'.
        layer (str): Layer name for plotting.
        scale (float): Scale displacements for the deformed plot.
        cbar (list): Minimum and maximum limits on the colorbar.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        vmin (float): Plot voxel data, and cull values below value voxel (0 1].
        vdx (float): Voxel spacing.

    Returns
    -------
        None
    """

    path = structure.path

    # Create and clear Rhino layer

    if not layer:
        layer = '{0}-{1}'.format(step, field)
    rs.CurrentLayer(rs.AddLayer(layer))
    clear_layer(layer)
    rs.EnableRedraw(False)

    # Node and element data

    nkeys = sorted(structure.nodes, key=int)
    nodes = [structure.node_xyz(nkey) for nkey in nkeys]

    ekeys = sorted(structure.elements, key=int)
    elements = [structure.elements[ekey].nodes for ekey in ekeys]

    nodal_data = structure.results[step]['nodal']
    elemental_data = structure.results[step]['element']
    ux = [nodal_data['ux'][str(key)] for key in nkeys]
    uy = [nodal_data['uy'][str(key)] for key in nkeys]
    uz = [nodal_data['uz'][str(key)] for key in nkeys]

    # Postprocess

    try:
        data = [nodal_data[field][str(key)] for key in nkeys]
        dtype = 'nodal'
    except:
        data = elemental_data[field]
        dtype = 'elemental'

    basedir = utilities.__file__.split('__init__.py')[0]
    xfunc = XFunc(basedir=basedir, tmpdir=path, mode=1)
    xfunc.funcname = 'functions.postprocess'
    toc, U, cnodes, fabs, fscaled = xfunc(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, 255, iptype, nodal)['data']

    print('\n***** Data processed : {0} s *****'.format(toc))

    # Plot voxels

    xfunc.funcname = 'functions.voxels'
    xfunc(fscaled, vmin, U, vdx, None, None)['data']

    # Return to Default layer

    rs.CurrentLayer(rs.AddLayer('Default'))
    rs.LayerVisible('colorbar', False)
    rs.LayerVisible(layer, False)
    rs.EnableRedraw(True)


def plot_principal_stresses(structure, step, ptype, scale, layer):
    """ Plots the principal stresses of the elements.

    Note:
        - Currently alpha script and for only four-noded S4 shell elements.

    Parameters
    ----------
        structure (obj): Structure object.
        path (str): Folder where results files are stored.
        name (str): Structure name.
        step (str): Name of the Step.
        ptype (str): 'max' 'min' for maxPrincipal or minPrincipal stresses.
        scale (float): Scale on the length of the line markers.
        layer (str): Layer name for plotting.

    Returns
    -------
        None
    """
    pass  # make this function external

#     name = structure.name
#     path = structure.path

#     # Clear and create layer

#     if not layer:
#         layer = '{0}_principal_{1}'.format(step, ptype)
#     rs.CurrentLayer(rs.AddLayer(layer))
#     rs.DeleteObjects(rs.ObjectsByLayer(layer))

#     # Process and plot

#     rs.EnableRedraw(False)

#     temp = '{0}{1}/'.format(path, name)
#     with open('{0}{1}-{2}-S.json'.format(temp, name, step), 'r') as f:
#         S = json.load(f)
#     S11, S22, S12, axes = S['S11'], S['S22'], S['S12'], S['axes']
#     SPr = S['{0}Principal'.format(ptype)]
#     sp1_keys = ['ip3_sp1', 'ip4_sp1', 'ip2_sp1', 'ip1_sp1']
#     sp5_keys = ['ip3_sp5', 'ip2_sp5', 'ip4_sp5', 'ip1_sp5']
#     ipkeys = sp1_keys + sp5_keys

#     print('Plotting principal stress vectors ...')

#     for ekey in SPr:

#         if len(structure.elements[int(ekey)].nodes) == 4:
#             th1 = [0.5 * atan2(S12[ekey][ip], 0.5 * (S11[ekey][ip] - S22[ekey][ip])) for ip in sp1_keys]
#             th5 = [0.5 * atan2(S12[ekey][ip], 0.5 * (S11[ekey][ip] - S22[ekey][ip])) for ip in sp5_keys]
#             th1m = sum(th1) / len(th1) + pi / 2
#             th5m = sum(th5) / len(th5) + pi / 2
#             pr1 = [i for i in [SPr[ekey][ip] for ip in sp1_keys] if i is not None]
#             pr5 = [i for i in [SPr[ekey][ip] for ip in sp5_keys] if i is not None]
#             e11 = centroid_points([axes[ekey][ip][0] for ip in ipkeys])
#             e22 = centroid_points([axes[ekey][ip][1] for ip in ipkeys])
#             # e33 = centroid_points([axes[ekey][ip][2] for ip in ipkeys])
#             c = structure.element_centroid(int(ekey))
#             if pr1:
#                 pr1m = sum(pr1) / len(pr1)
#                 ex1 = scale_vector(e11, cos(th1m))
#                 ey1 = scale_vector(e22, sin(th1m))
#                 er1 = add_vectors(ex1, ey1)
#                 vec1 = add_vectors(c, scale_vector(er1, (pr1m * scale / 10**7) + 0.0001))
#                 id1 = rs.AddLine(c, vec1)
#                 col1 = [255, 0, 0] if pr1m > 0 else [0, 0, 255]
#                 rs.ObjectColor(id1, col1)
#             if pr5:
#                 pr5m = sum(pr5) / len(pr5)
#                 ex5 = scale_vector(e11, cos(th5m))
#                 ey5 = scale_vector(e22, sin(th5m))
#                 er5 = add_vectors(ex5, ey5)
#                 vec5 = add_vectors(c, scale_vector(er5, (pr5m * scale / 10**7) + 0.0001))
#                 id5 = rs.AddLine(c, vec5)
#                 col5 = [255, 0, 0] if pr5m > 0 else [0, 0, 255]
#                 rs.ObjectColor(id5, col5)

#     rs.EnableRedraw(True)
