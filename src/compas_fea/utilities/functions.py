
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.topology import dijkstra_path

from compas.geometry import add_vectors
from compas.geometry import angles_points_xy
from compas.geometry import area_polygon_xy
from compas.geometry import centroid_points
from compas.geometry import circle_from_points_xy
from compas.geometry import cross_vectors
from compas.geometry import distance_point_point
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas.utilities import geometric_key

from time import time

try:
    from numpy import abs
    from numpy import arccos
    from numpy import arctan2
    from numpy import array
    from numpy import asarray
    from numpy import cos
    from numpy import dot
    from numpy import hstack
    from numpy import isnan
    from numpy import linspace
    from numpy import meshgrid
    from numpy import min
    from numpy import max
    from numpy import newaxis
    from numpy import pi
    from numpy import sin
    from numpy import squeeze
    from numpy import sum
    from numpy import vdot
    from numpy import vstack
    from numpy import zeros
    from numpy.linalg import inv
except ImportError:
    pass

try:
    from scipy.interpolate import griddata
    from scipy.sparse import csr_matrix
    from scipy.sparse import find
    from scipy.spatial import Delaunay
    from scipy.spatial import distance_matrix
except ImportError:
    pass

try:
    from mayavi import mlab
except ImportError:
    pass

try:
    from meshpy.tet import build
    from meshpy.tet import MeshInfo
except ImportError:
    pass


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'colorbar',
    'combine_all_sets',
    'discretise_faces',
    'extrude_mesh',
    'group_keys_by_attribute',
    'group_keys_by_attributes',
    'network_order',
    'normalise_data',
    'postprocess',
    'process_data',
    'tets_from_vertices_faces',
    'voxels',
]


def colorbar(fsc, input='array', type=255):

    """ Creates RGB color information from -1 to 1 scaled values.

    Parameters
    ----------
    fsc : array, float
        (n x 1) array of normalised data, or a single float value.
    input : str
        Input given as an 'array' of numbers or a 'float'.
    type : int
        RGB as 255 or 1 scaled.

    Returns
    -------
    array, list
        (n x 3) array of RGB values or single RGB list.

    """

    r = abs(fsc + 0.25) * 2 - 0.5
    g = -abs(fsc - 0.25) * 2 + 1.5
    b = -(fsc - 0.25) * 2

    if input == 'array':
        rgb = hstack([r, g, b])
        rgb[rgb > 1] = 1
        rgb[rgb < 0] = 0
        return rgb * type

    elif input == 'float':
        r = max([0, min([1, r])])
        g = max([0, min([1, g])])
        b = max([0, min([1, b])])
        return [i * type for i in [r, g, b]]


def combine_all_sets(sets_a, sets_b):

    """ Combines two nested lists of node or element sets into the minimum
    ammount of set combinations. Used to determine the necesary element
    property sets, given sets of materials and sections.

    Parameters
    ----------
    sets_a : list
        First nested list containing lists of element or node keys.
    sets_b : list
        Second nested list containing lists of element or node keys.

    Returns
    -------
    dic
        A dictionary containing the minimum number of set combinations.

    """

    comb = {}
    for i in sets_a:
        for j in sets_b:
            for x in sets_a[i]:
                if x in sets_b[j]:
                    comb.setdefault(str(i) + ',' + str(j), []).append(x)
    return comb


def discretise_faces(vertices, faces, target, min_angle=15, factor=3, iterations=100):

    """ Make an FE mesh from an input coarse mesh data.

    Parameters
    ----------
    vertices : list
        Co-ordinates of coarse mesh vertices.
    faces : list
        Vertex numbers of each face of the coarse mesh.
    target : float
        Target length of each triangle.
    min_angle : float
        Minimum internal angle of triangles.
    factor : float
        Factor on the maximum area of each triangle.
    iterations : int
        Number of iterations per face.

    Returns
    -------
    list
        Vertices of discretised faces.
    list
        Triangles of discretised faces.

    """

    points_all = []
    faces_all = []

    for count, face in enumerate(faces):

        # Prepare points and facets

        face.append(face[0])
        points = []
        for i in range(len(face) - 1):
            u = face[i + 0]
            v = face[i + 1]
            sp = vertices[u]
            ep = vertices[v]
            vec = subtract_vectors(ep, sp)
            l = length_vector(vec)
            n = max([1, int(l / target)])
            for j in range(n):
                points.append(add_vectors(sp, scale_vector(vec, j / float(n))))

        # Starting orientation

        centroid = centroid_points(points)
        vec1 = subtract_vectors(points[1], points[0])
        vecc = subtract_vectors(centroid, points[0])
        vecn = cross_vectors(vec1, vecc)

        # Rotate about x

        points = array(points).transpose()
        phi = -arctan2(vecn[2], vecn[1]) + pi / 2
        Rx = array([[1., 0., 0.], [0., cos(phi), -sin(phi)], [0., sin(phi), cos(phi)]])
        vecn_x = dot(Rx, array(vecn)[:, newaxis])
        points_x = dot(Rx, points)

        # Rotate about y

        psi = +arctan2(vecn_x[2, 0], vecn_x[0, 0]) - pi / 2
        Ry = array([[cos(psi), 0., sin(psi)], [0., 1., 0.], [-sin(psi), 0., cos(psi)]])
        points_y = dot(Ry, points_x)

        # Algorithm

        V = points_y.transpose()
        z = float(V[0, 2])
        Amax = factor * 0.5 * target**2
        it = 0
        while it < iterations:
            DT = Delaunay(V[:, :2], furthest_site=False, incremental=False)
            tris = DT.simplices
            change = False
            for u, v, w in tris:
                # v1 = V[v, :] - V[u, :]
                # v2 = V[w, :] - V[v, :]
                # v3 = V[u, :] - V[w, :]
                # th1 = arccos(vdot(+v1, -v3)) * 180 / pi
                # th2 = arccos(vdot(+v2, -v2)) * 180 / pi
                # th3 = arccos(vdot(+v3, -v3)) * 180 / pi
                p1 = [float(i) for i in V[u, :2]]
                p2 = [float(i) for i in V[v, :2]]
                p3 = [float(i) for i in V[w, :2]]
                th1 = angles_points_xy(p1, p2, p3)[0] * 180 / pi
                th2 = angles_points_xy(p2, p1, p3)[0] * 180 / pi
                th3 = angles_points_xy(p3, p1, p2)[0] * 180 / pi
                thm = min([th1, th2, th3])
                c, r, _ = circle_from_points_xy(p1, p2, p3)
                c = list(c)
                c[2] = z
                A = area_polygon_xy([p1, p2, p3])
                if (thm < min_angle) or (A > Amax):
                    change = True
                    dist = distance_matrix(array([c]), V, threshold=10**5)
                    if len(dist[dist <= r]) <= 3:
                        V = vstack([V, array([c])])
                        break
            if not change:
                break
            it += 1
        print('Iterations for face {0}: {1}'.format(count, it))

        # Rotate back to global

        Rxinv = inv(Rx)
        Ryinv = inv(Ry)
        points_x = dot(Ryinv, V.transpose())
        points = dot(Rxinv, points_x)

        # Save

        points_new = [list(i) for i in list(points.transpose())]
        faces_new = [[int(i) for i in tri] for tri in list(tris)]
        points_all.append(points_new)
        faces_all.append(faces_new)

    return points_all, faces_all


def extrude_mesh(structure, mesh, nz, dz, setname=None, cap=None, links=None):

    """ Extrudes a Mesh into cells of many layers and adds to Structure.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    mesh : obj
        Mesh datastructure to extrude.
    nz : int
        Number of layers.
    dz : float
        Layer thickness.
    setname : str
        Name of set for added solid elements.
    cap : str
        Name of set for a capping mesh on final surface.
    links : str
        Name of set for adding links along extrusion.

    Returns
    -------
    None

    Notes
    -----
    - Extrusion is along the Mesh vertex normals.
    - Elements are added automatically to the Structure object.

    """

    ki = {}
    elements = []
    cap_faces = []
    link_springs = []

    for key in mesh.vertices():
        normal = normalize_vector(mesh.vertex_normal(key))
        xyz = mesh.vertex_coordinates(key)
        ki['{0}_0'.format(key)] = structure.add_node(xyz)
        for i in range(nz):
            xyzi = add_vectors(xyz, scale_vector(normal, (i + 1) * dz))
            ki['{0}_{1}'.format(key, i + 1)] = structure.add_node(xyzi)
        if links:
            node1 = ki['{0}_{1}'.format(key, 0)]
            node2 = ki['{0}_{1}'.format(key, nz)]
            ez_sp = structure.node_xyz(node1)
            ez_ep = structure.node_xyz(node2)
            ez = normalize_vector(subtract_vectors(ez_ep, ez_sp))
            try:  # ths needs checking
                ey = cross_vectors(ez, [1, 0, 0])
            except:
                pass
            ekey = structure.add_element(nodes=[node1, node2], type='SpringElement', acoustic=False, thermal=False,
                                         axes={'ez': ez, 'ey': ey})
            link_springs.append(ekey)

    for face in mesh.faces():
        vs = mesh.face_vertices(face)
        if len(vs) == 3:
            type = 'PentahedronElement'
        elif len(vs) == 4:
            type = 'HexahedronElement'
        for i in range(nz):
            bot = ['{0}_{1}'.format(j, i + 0) for j in vs]
            top = ['{0}_{1}'.format(j, i + 1) for j in vs]
            nodes = [ki[j] for j in bot + top]
            ekey = structure.add_element(nodes=nodes, type=type, acoustic=False, thermal=False)
            elements.append(ekey)
            if (i == nz - 1) and cap:
                nodes = [ki[j] for j in top]
                ekey = structure.add_element(nodes=nodes, type='ShellElement', acoustic=False, thermal=False)
                cap_faces.append(ekey)

    structure.add_set(name=setname, type='element', selection=elements)
    if cap:
        structure.add_set(name=cap, type='element', selection=cap_faces)
    if links:
        structure.add_set(name=links, type='element', selection=link_springs)


def group_keys_by_attribute(adict, name, tol='3f'):

    """ Make group keys by shared attribute values.

    Parameters
    ----------
    adict : dic
        Attribute dictionary.
    name : str
        Attribute of interest.
    tol : float
        Float tolerance.

    Returns
    -------
    dic
        Group dictionary.

    """

    groups = {}
    for key, item in adict.items():
        if name in item:
            value = item[name]
            if type(value) == float:
                value = '{0:.{1}}'.format(value, tol)
            groups.setdefault(value, []).append(key)
    return groups


def group_keys_by_attributes(adict, names, tol='3f'):

    """ Make group keys by shared values of attributes.

    Parameters
    ----------
    adict : dic
        Attribute dictionary.
    name : str
        Attributes of interest.
    tol : float
        Float tolerance.

    Returns
    -------
    dic
        Group dictionary.

    """

    groups = {}
    for key, item in adict.items():
        values = []
        for name in names:
            if name in item:
                value = item[name]
                if type(value) == float:
                    value = '{0:.{1}}'.format(value, tol)
                else:
                    value = str(value)
            else:
                value = '-'
            values.append(value)
        vkey = '_'.join(values)
        groups.setdefault(vkey, []).append(key)
    return groups


def network_order(sp_xyz, structure, network):

    """ Extract node and element orders from a Network for a given start-point.

    Parameters
    ----------
    sp_xyz : list
        Start point co-ordinates.
    structure : obj
        Structure object.
    network : obj
        Network object.

    Returns
    -------
    list
        Ordered nodes.
    list
        Ordered elements.
    list
        Cumulative lengths at element mid-points.
    float
        Total length.

    """

    gkey_key = network.gkey_key()
    start = gkey_key[geometric_key(sp_xyz, '{0}f'.format(structure.tol))]
    leaves = network.leaves()
    leaves.remove(start)
    end = leaves[0]

    adjacency = {key: network.vertex_neighbours(key) for key in network.vertices()}
    weight = {(u, v): network.edge_length(u, v) for u, v in network.edges()}
    weight.update({(v, u): weight[(u, v)] for u, v in network.edges()})
    path = dijkstra_path(adjacency, weight, start, end)
    nodes = [structure.check_node_exists(network.vertex_coordinates(i)) for i in path]
    elements, arclengths, length = [], [], 0

    for i in range(len(nodes) - 1):
        sp = nodes[i]
        ep = nodes[i + 1]
        elements.append(structure.check_element_exists([sp, ep]))
        xyz_sp = structure.node_xyz(sp)
        xyz_ep = structure.node_xyz(ep)
        dL = distance_point_point(xyz_sp, xyz_ep)
        arclengths.append(length + dL / 2.)
        length += dL

    return nodes, elements, arclengths, length


def normalise_data(data, cmin, cmax):

    """ Normalise a vector of data to between -1 and 1.

    Parameters
    ----------
    data : array
        Unscaled (n x 1) data.
    cmin : float
        Cap data values >= cmin.
    cmax : float
        Cap data values <= cmax.

    Returns
    -------
    array
        -1 to 1 scaled data.
    float
        The maximum absolute unscaled value.

    """

    f = asarray(data)
    fmax = cmax if cmax is not None else max(abs(f))
    fmin = cmin if cmin is not None else min(abs(f))
    fabs = max([abs(fmin), abs(fmax)])

    fscaled = f / fabs if fabs else f
    fscaled[fscaled > +1] = +1
    fscaled[fscaled < -1] = -1

    return fscaled, fabs


def postprocess(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, ctype, iptype, nodal):

    """ Post-process data from analysis results for given step and field.

    Parameters
    ----------
    nodes : list
        [[x, y, z], ..] co-ordinates of each node.
    elements : list
        Node numbers that each element connects.
    ux : list
        List of nodal x displacements.
    uy : list
        List of nodal y displacements.
    uz : list
        List of nodal z displacements.
    data : dic
        Unprocessed data.
    dtype : str
        'nodal' or 'elemental'.
    scale : float
        Scale displacements for the deformed plot.
    cbar : list
        Minimum and maximum limits on the colorbar.
    ctype : int
        RGB color type, 1 or 255.
    iptype : str
        'mean', 'max' or 'min' of an element's integration point data.
    nodal : str
        'mean', 'max' or 'min' for nodal values.

    Returns
    -------
    float
        Time taken to process data.
    list
        Scaled deformed nodal co-ordinates.
    list
        Nodal colors.
    float
        Absolute maximum data value.
    list
        Normalised data values.

    """

    tic = time()

    dU = hstack([array(ux)[:, newaxis], array(uy)[:, newaxis], array(uz)[:, newaxis]])
    U = [list(i) for i in list(array(nodes) + scale * dU)]

    values, values_ = process_data(data=data, dtype=dtype, iptype=iptype, nodal=nodal, elements=elements, n=len(nodes))
    fscaled, fabs = normalise_data(data=values, cmin=cbar[0], cmax=cbar[1])
    if values_ is not None:
        escaled, eabs = normalise_data(data=values_, cmin=cbar[0], cmax=cbar[1])
    else:
        escaled = None
    fscaled_ = [float(i) for i in list(fscaled)]
    fabs = float(fabs)

    cnodes = colorbar(fsc=fscaled, input='array', type=ctype)
    cnodes_ = [list(i) for i in list(cnodes)]
    if escaled is not None:
        celements = colorbar(fsc=escaled, input='array', type=ctype)
        celements_ = [list(i) for i in list(celements)]
    else:
        celements_ = []

    toc = time() - tic

    return toc, U, cnodes_, fabs, fscaled_, celements_


def process_data(data, dtype, iptype, nodal, elements, n):

    """ Processes the raw data.

    Parameters
    ----------
    data : dic
        Unprocessed data.
    dtype : str
        'nodal' or 'elemental'.
    iptype : str
        'mean', 'max' or 'min' of an element's integration point data.
    nodal : str
        'mean', 'max' or 'min' for nodal values.
    elements : list
        Node numbers that each element connects.
    n : int
        Number of nodes.

    Returns
    -------
    array
        Data values at each node.
    array
        Data values at each element.

    """

    if dtype == 'nodal':
        values = array(data)[:, newaxis]
        values_ = None

    elif dtype == 'element':
        m = len(list(data.keys()))
        values_ = zeros((m, 1))
        values = zeros((n, 1))

        for dkey, item in data.items():
            fdata = list(item.values())
            for i, c in enumerate(fdata):
                if c is None:
                    fdata[i] = 0
            if iptype == 'max':
                value = max(fdata)
            elif iptype == 'min':
                value = min(fdata)
            elif iptype == 'mean':
                value = sum(fdata) / len(fdata)
            values_[int(dkey)] = value

        srows, scols = [], []
        for c, i in enumerate(elements):
            srows.extend([c] * len(i))
            scols.extend(i)
        sdata = [1] * len(srows)
        A = csr_matrix((sdata, (srows, scols)), shape=(m, n))
        AT = A.transpose()

        if nodal == 'mean':
            values = asarray(AT.dot(values_) / sum(AT, 1))

        else:
            rows, cols, vals = find(AT)
            dic = {i: [] for i in range(n)}
            for row, col in zip(rows, cols):
                dic[row].append(values_[col, 0])
            for i in range(n):
                if nodal == 'max':
                    values[i] = max(dic[i])
                elif nodal == 'min':
                    values[i] = min(dic[i])

    return values, values_


def voxels(values, vmin, U, vdx, plot=None, indexing=None):

    """ Plot normalised [0 1] values as voxel data.

    Parameters
    ----------
    values : array
        Normalised data at nodes.
    vmin : float
        Cull values below vmin.
    U : array
        ist): Nodal co-ordinates.
    vdx : float
        Spacing of voxel grid.
    plot : str
        'mayavi'.
    indexing : str
        Meshgrid indexing type.

    Returns
    -------
    None

    """
    U = array(U)
    x = U[:, 0]
    y = U[:, 1]
    z = U[:, 2]
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)
    zmin, zmax = min(z), max(z)
    X = linspace(xmin, xmax, (xmax - xmin) / vdx)
    Y = linspace(ymin, ymax, (ymax - ymin) / vdx)
    Z = linspace(zmin, zmax, (zmax - zmin) / vdx)
    if indexing is None:
        Xm, Ym, Zm = meshgrid(X, Y, Z)
    else:
        Zm, Ym, Xm = meshgrid(X, Y, Z, indexing=indexing)

    f = abs(asarray(values))
    Am = squeeze(griddata(U, f, (Xm, Ym, Zm), method='linear', fill_value=0))
    Am[isnan(Am)] = 0
    if plot == 'mayavi':
        mlab.pipeline.volume(mlab.pipeline.scalar_field(Am), vmin=vmin)
        mlab.show()
    else:
        return Am


def tets_from_vertices_faces(vertices, faces, volume=None):

    """ Generate tetrahedron points and elements with MeshPy (TetGen).

    Parameters
    ----------
    vertices : list
        List of lists of vertex co-ordinates of input surface mesh.
    faces : list
        List of lists of face indices of input surface mesh.
    volume : float
        Volume constraint for each tetrahedron element.

    Returns
    -------
    list
        Points of the tetrahedrons.
    list
        Indices of points for each tetrahedron element.

    """

    info = MeshInfo()
    info.set_points(vertices)
    info.set_facets(faces)
    tets = build(info, max_volume=volume)
    tets_points = [list(i) for i in list(tets.points)]
    tets_elements = [list(i) for i in list(tets.elements)]
    return tets_points, tets_elements


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    pass
#     vertices = [[1, 3, 4], [2, 0, 3], [4, 4, 1], [3, 3, 3]]
#     faces = [[0, 1, 2], [1, 2, 3]]
#     pts, fcs = discretise_faces(vertices, faces, target=0.2, min_angle=15, factor=3, iterations=200)
