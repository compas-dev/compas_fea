
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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

from compas.topology import dijkstra_path

from compas.utilities import geometric_key

from compas.datastructures import Mesh

from time import time

from operator import itemgetter
from itertools import groupby

try:
    from compas.viewers import VtkViewer
except:
    pass

try:
    from numpy import abs
    from numpy import arctan2
    from numpy import array
    from numpy import asarray
    from numpy import cos
    from numpy import dot
    from numpy import float64
    from numpy import hstack
    from numpy import isnan
    from numpy import int64
    from numpy import linspace
    from numpy import meshgrid
    from numpy import max
    from numpy import mean
    from numpy import min
    from numpy import newaxis
    from numpy import pi
    from numpy import sin
    from numpy import squeeze
    from numpy import sum
    from numpy import tile
    from numpy import vstack
    from numpy import zeros
    from numpy.linalg import inv
except ImportError:
    pass

try:
    from scipy.interpolate import griddata
    from scipy.sparse import csr_matrix
    from scipy.spatial import Delaunay
    from scipy.spatial import distance_matrix
except ImportError:
    pass

try:
    from meshpy.tet import build
    from meshpy.tet import MeshInfo
except ImportError:
    pass


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
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
    'principal_stresses',
    'plotvoxels',
    'identify_ranges',
    'mesh_from_shell_elements'
]


def process_data(data, dtype, iptype, nodal, elements, n):

    """ Process the raw data.

    Parameters
    ----------
    data : dict
        Unprocessed analysis results data.
    dtype : str
        'nodal' or 'element'.
    iptype : str
        'mean', 'max' or 'min' of an element's integration point data.
    nodal : str
        'mean', 'max' or 'min' for nodal data conversion.
    elements : list
        Node numbers for each element.
    n : int
        Number of nodes.

    Returns
    -------
    array
        Data values for each node.
    array
        Data values for each element.

    """

    if dtype == 'nodal':

        vn = array(data)[:, newaxis]
        ve = None

    elif dtype == 'element':

        m          = len(elements)
        lengths    = zeros(m, dtype=int64)
        data_array = zeros((m, 20), dtype=float64)

        iptypes = {'max': 0, 'min': 1, 'mean': 2}

        for ekey, item in data.items():
            fdata = list(item.values())
            j = int(ekey)

            if None in fdata:
                fdata = [i for i in fdata if i is not None]

            if fdata:
                length = len(fdata)
                lengths[j] = length
                data_array[j, :length] = fdata

        rows, cols = [], []

        for ekey, nodes in enumerate(elements):
            rows.extend([ekey] * len(nodes))
            cols.extend(nodes)
        vals = [1] * len(rows)

        A  = csr_matrix((vals, (rows, cols)), shape=(m, n))
        AT = A.transpose()


        def _process(data_array, lengths, iptype):

            m  = len(lengths)
            ve = zeros((m, 1))

            for i in range(m):

                if iptype == 0:
                    ve[i]  = max(data_array[i, :lengths[i]])

                elif iptype == 1:
                    ve[i]  = min(data_array[i, :lengths[i]])

                elif iptype == 2:
                    ve[i]  = mean(data_array[i, :lengths[i]])

            return ve


        def _nodal(rows, cols, nodal, ve, n):

            vn = zeros((n, 1))

            for i in range(len(rows)):

                node    = cols[i]
                element = rows[i]

                if nodal == 0:
                    if ve[element] > vn[node]:
                        vn[node] = ve[element]

                elif nodal == 1:
                    if ve[element] < vn[node]:
                        vn[node] = ve[element]

            return vn


        ve = _process(data_array, lengths, iptypes[iptype])

        if nodal == 'mean':
            vsum = asarray(AT.dot(ve))
            vn = vsum / sum(AT, 1)

        else:
            vn = _nodal(rows, cols, 0 if nodal == 'max' else 1, ve, n)

    return vn, ve


def identify_ranges(data):

    """ Identifies continuous interger series from a list and returns a list of ranges.

    Parameters
    ----------
    data : list
        The list of intergers to process.

    Returns
    -------
    list
        A list of identified ranges.

    """

    data.sort()
    data = set(data)
    ranges = []

    for k, g in groupby(enumerate(data), lambda x: x[0] - x[1]):
        group = list(map(itemgetter(1), g))
        if group[0] != group[-1]:
            ranges.append((group[0], group[-1]))
        else:
            ranges.append(group[0])

    return ranges


def colorbar(fsc, input='array', type=255):

    """ Creates RGB color information from -1 to 1 scaled values.

    Parameters
    ----------
    fsc : array, float
        (n x 1) array of scaled data, or a single float value.
    input : str
        Input given as an 'array' of numbers or a 'float'.
    type : int
        RGB as 255 or 1 scaled.

    Returns
    -------
    array, list
        (n x 3) array of RGB values or single RGB list.

    """

    r = +abs(fsc + 0.25) * 2 - 0.5
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


def mesh_from_shell_elements(structure):

    """ Returns a Mesh datastructure object from a Structure's ShellElement objects.

    Parameters
    ----------
    structure: obj
        The structure to extract a Mesh from.

    Returns
    -------
    obj
        Mesh datastructure object.

    """

    ekeys = [ekey for ekey in structure.elements if structure.elements[ekey].__name__ == 'ShellElement']
    nkeys = {nkey for ekey in ekeys for nkey in structure.elements[ekey].nodes}

    mesh = Mesh()
    for nkey in nkeys:
        x, y, z = structure.node_xyz(nkey)
        mesh.add_vertex(key=nkey, x=x, y=y, z=z)

    for ekey in ekeys:
        mesh.add_face(structure.elements[ekey].nodes, key=ekey)

    return mesh


def volmesh_from_solid_elements(structure):

    raise NotImplementedError


def network_from_line_elements(structure):

    raise NotImplementedError
























def combine_all_sets(sets_a, sets_b):

    """ Combines two nested lists of node or element sets into the minimum ammount of set combinations.

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


def discretise_faces(vertices, faces, target, min_angle=15, factor=3, iterations=100, refine=True):

    """ Make an FE mesh from input coarse mesh data.

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
    refine : bool
        Refine beyond Delaunay.

    Returns
    -------
    list
        Vertices of discretised faces.
    list
        Triangles of discretised faces.

    Notes
    -----
    - An experimental script.

    """

    points_all = []
    faces_all = []

    Amax = factor * 0.5 * target**2

    for count, face in enumerate(faces):
        print('Face {0}/{1}'.format(count + 1, len(faces)))

        # Seed

        face.append(face[0])
        points = []
        for u, v in zip(face[:-1], face[1:]):
            sp = vertices[u]
            ep = vertices[v]
            vec = subtract_vectors(ep, sp)
            l = length_vector(vec)
            n = max([1, int(l / target)])
            for j in range(n):
                points.append(add_vectors(sp, scale_vector(vec, j / n)))
        if len(points) > 3:
            points.append(centroid_points(points))

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
        Rxinv = inv(Rx)

        # Rotate about y

        psi = +arctan2(vecn_x[2, 0], vecn_x[0, 0]) - pi / 2
        Ry = array([[cos(psi), 0., sin(psi)], [0., 1., 0.], [-sin(psi), 0., cos(psi)]])
        points_y = dot(Ry, points_x)
        Ryinv = inv(Ry)

        # Refine

        V = points_y.transpose()
        z = float(V[0, 2])

        try:
            it = 0
            while it < iterations:
                DT = Delaunay(V[:, :2], furthest_site=False, incremental=False)
                tris_ = DT.simplices
                tris = []
                for tri in tris_:
                    if len(set(tri)) == 3:
                        u, v, w = tri
                        p1 = [float(i) for i in V[u, :2]]
                        p2 = [float(i) for i in V[v, :2]]
                        p3 = [float(i) for i in V[w, :2]]
                        th1 = angles_points_xy(p1, p2, p3)[0] * 180 / pi
                        th2 = angles_points_xy(p2, p3, p1)[0] * 180 / pi
                        th3 = angles_points_xy(p3, p1, p2)[0] * 180 / pi
                        if (th1 > 0.1) and (th2 > 0.1) and (th3 > 0.1):
                            tris.append(tri)
                for u, v, w in tris:
                    p1 = [float(i) for i in V[u, :2]]
                    p2 = [float(i) for i in V[v, :2]]
                    p3 = [float(i) for i in V[w, :2]]
                    # th1 = angles_points_xy(p1, p2, p3)[0] * 180 / pi
                    # th2 = angles_points_xy(p2, p3, p1)[0] * 180 / pi
                    # th3 = angles_points_xy(p3, p1, p2)[0] * 180 / pi
                    # thm = min([th1, th2, th3])
                    res = circle_from_points_xy(p1, p2, p3)
                    if res:
                        c, r, _ = res
                        c[2] = z
                        A = area_polygon_xy([p1, p2, p3])
                        # if (thm < min_angle) or (A > Amax):
                        if A > Amax:
                            dist = distance_matrix(array([c]), V, threshold=10**5)
                            ins = len(dist[dist <= r])
                            if ins <= 3:
                                V = vstack([V, array([c])])
                                break
                    else:
                        continue
                it += 1

            print('Iterations {0}'.format(it))

            points_x = dot(Ryinv, V.transpose())
            points_new = [list(i) for i in list(dot(Rxinv, points_x).transpose())]
            faces_new = [[int(i) for i in tri] for tri in list(tris)]

            points_all.append(points_new)
            faces_all.append(faces_new)

        except:
            print('***** ERROR *****')

    return points_all, faces_all


def extrude_mesh(structure, mesh, layers, thickness, mesh_name, links_name, blocks_name):

    """ Extrudes a Mesh and adds/creates elements to a Structure.

    Parameters
    ----------
    structure : obj
        Structure object to update.
    mesh : obj
        Mesh datastructure
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

    Returns
    -------
    None

    Notes
    -----
    - Extrusion is along the Mesh vertex normals.

    """

    ki = {}
    blocks = []
    mesh_faces = []
    links = []

    for key in mesh.vertices():

        normal = normalize_vector(mesh.vertex_normal(key))
        xyz = mesh.vertex_coordinates(key)
        ki['{0}_0'.format(key)] = structure.add_node(xyz)

        for i in range(layers):
            xyzi = add_vectors(xyz, scale_vector(normal, (i + 1) * thickness))
            ki['{0}_{1}'.format(key, i + 1)] = structure.add_node(xyzi)

            if links_name:
                node1 = ki['{0}_0'.format(key)]
                node2 = ki['{0}_{1}'.format(key, i + 1)]
                ez = normalize_vector(subtract_vectors(xyzi, xyz))
                try:  # check
                    ey = cross_vectors(ez, [1, 0, 0])
                except:
                    pass
                ekey = structure.add_element(nodes=[node1, node2], type='SpringElement', acoustic=False, thermal=False,
                                             axes={'ez': ez, 'ey': ey})
                structure.elements[ekey].A = mesh.vertex_area(key)
                links.append(ekey)

    for face in mesh.faces():

        vs = mesh.face_vertices(face)

        for i in range(layers):
            bot = ['{0}_{1}'.format(j, i + 0) for j in vs]
            top = ['{0}_{1}'.format(j, i + 1) for j in vs]

            if blocks_name:
                if len(vs) == 3:
                    etype = 'PentahedronElement'
                elif len(vs) == 4:
                    etype = 'HexahedronElement'
                nodes = [ki[j] for j in bot + top]
                ekey = structure.add_element(nodes=nodes, type=etype, acoustic=False, thermal=False)
                blocks.append(ekey)

            if (i == layers - 1) and mesh_name:
                nodes = [ki[j] for j in top]
                ekey = structure.add_element(nodes=nodes, type='ShellElement', acoustic=False, thermal=False)
                mesh_faces.append(ekey)

    if blocks_name:
        structure.add_set(name=blocks_name, type='element', selection=blocks)
    if mesh_name:
        structure.add_set(name=mesh_name, type='element', selection=mesh_faces)
    if links:
        structure.add_set(name=links_name, type='element', selection=links)


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


def network_order(start, structure, network):

    """ Extract node and element orders from a Network for a given start-point.

    Parameters
    ----------
    start : list
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
    start = gkey_key[geometric_key(start, '{0}f'.format(structure.tol))]
    leaves = network.leaves()
    leaves.remove(start)
    end = leaves[0]

    adjacency = {i: network.vertex_neighbours(i) for i in network.vertices()}
    weight = {(u, v): 1 for u, v in network.edges()}
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
        Raw data.
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
        'nodal' or 'element'.
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
        Absolute maximum nodal data value.
    list
        Normalised data values.
    list
        Element colors.
    float
        Absolute maximum element data value.

    """

    tic = time()

    dU = hstack([array(ux)[:, newaxis], array(uy)[:, newaxis], array(uz)[:, newaxis]])
    U = [list(i) for i in list(array(nodes) + scale * dU)]

    vn, ve = process_data(data=data, dtype=dtype, iptype=iptype, nodal=nodal, elements=elements, n=len(U))

    fscaled, fabs = normalise_data(data=vn, cmin=cbar[0], cmax=cbar[1])
    cnodes = colorbar(fsc=fscaled, input='array', type=ctype)

    if dtype == 'element':
        escaled, eabs = normalise_data(data=ve, cmin=cbar[0], cmax=cbar[1])
        celements = colorbar(fsc=escaled, input='array', type=ctype)
        celements_ = [list(i) for i in list(celements)]
    else:
        eabs = 0
        celements_ = []

    toc      = time() - tic
    cnodes_  = [list(i) for i in list(cnodes)]
    fabs_    = float(fabs)
    fscaled_ = [float(i) for i in list(fscaled)]

    return toc, U, cnodes_, fabs_, fscaled_, celements_, float(eabs)


def plotvoxels(values, U, vdx, plot=True, indexing=None):

    """ Plot values as voxel data.

    Parameters
    ----------
    values : array
        Normalised data at nodes.
    U : array
        Nodal co-ordinates.
    vdx : float
        Representative volume size for a voxel.
    plot : str
        Plot voxels using compas VtkVoxels 'vtk'.

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
    Xm, Ym, Zm = meshgrid(X, Y, Z)
    if indexing:
        Zm, Ym, Xm = meshgrid(X, Y, Z, indexing='ij')

    f = abs(asarray(values))
    Am = squeeze(griddata(U, f, (Xm, Ym, Zm), method='linear', fill_value=0))
    Am[isnan(Am)] = 0

    if plot == 'vtk':
        voxels = VtkViewer(data={'voxels': Am})
        voxels.start()

    return Am


def tets_from_vertices_faces(vertices, faces, volume=None):

    """ Generate tetrahedron points and elements with MeshPy (TetGen).

    Parameters
    ----------
    vertices : list
        List of lists of vertex co-ordinates for input surface mesh.
    faces : list
        List of lists of face indices for input surface mesh.
    volume : float
        Volume constraint for each tetrahedron element.

    Returns
    -------
    list
        Points of the tetrahedrons.
    list
        Indices of points for each tetrahedron element.

    """

    try:
        info = MeshInfo()
        info.set_points(vertices)
        info.set_facets(faces)
        tets = build(info, max_volume=volume)
        tets_points = [list(i) for i in list(tets.points)]
        tets_elements = [list(i) for i in list(tets.elements)]
        return tets_points, tets_elements
    except:
        print('***** MeshPy failed *****')


def principal_stresses(data, ptype, scale, rotate):

    """ Performs principal stress calculations.

    Parameters
    ----------
    data : dic
        Element data from structure.results for the Step.
    ptype : str
        'max' 'min' for maximum or minimum principal stresses.
    scale : float
        Scale on the length of the vectors.
    rotate : int
        Rotate lines by 90 deg, 0 or 1.

    Returns
    -------
    array
        Vectors for section point 1.
    array
        Vectors for section point 5.
    array
        Principal stresses for section point 1.
    array
        Principal stresses for section point 5.
    float
        Maxium stress magnitude.

    """

    axes = data['axes']
    s11  = data['sxx']
    s22  = data['syy']
    s12  = data['sxy']
    spr  = data['s{0}p'.format(ptype)]

    ekeys = spr.keys()
    m = len(ekeys)
    s11_sp1 = zeros(m)
    s22_sp1 = zeros(m)
    s12_sp1 = zeros(m)
    spr_sp1 = zeros(m)
    s11_sp5 = zeros(m)
    s22_sp5 = zeros(m)
    s12_sp5 = zeros(m)
    spr_sp5 = zeros(m)
    e11 = zeros((m, 3))
    e22 = zeros((m, 3))

    for ekey in ekeys:
        i = int(ekey)
        try:
            e11[i, :] = axes[ekey][0]
            e22[i, :] = axes[ekey][1]
            s11_sp1[i] = s11[ekey]['ip1_sp1']
            s22_sp1[i] = s22[ekey]['ip1_sp1']
            s12_sp1[i] = s12[ekey]['ip1_sp1']
            spr_sp1[i] = spr[ekey]['ip1_sp1']
            s11_sp5[i] = s11[ekey]['ip1_sp5']
            s22_sp5[i] = s22[ekey]['ip1_sp5']
            s12_sp5[i] = s12[ekey]['ip1_sp5']
            spr_sp5[i] = spr[ekey]['ip1_sp5']
        except:
            pass

    th1 = tile((0.5 * arctan2(s12_sp1, 0.5 * (s11_sp1 - s22_sp1)) + 0.5 * pi * rotate)[:, newaxis], (1, 3))
    th5 = tile((0.5 * arctan2(s12_sp5, 0.5 * (s11_sp5 - s22_sp5)) + 0.5 * pi * rotate)[:, newaxis], (1, 3))
    er1 = e11 * cos(th1) + e22 * sin(th1)
    er5 = e11 * cos(th5) + e22 * sin(th5)
    vec1 = er1 * (tile(spr_sp1[:, newaxis], (1, 3)) * scale / 10**7 + 0.0001)
    vec5 = er5 * (tile(spr_sp5[:, newaxis], (1, 3)) * scale / 10**7 + 0.0001)
    pmax = max([max(abs(spr_sp1)), max(abs(spr_sp5))])

    return vec1, vec5, spr_sp1, spr_sp5, pmax


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    data = [1,2,3,4,6,15,7,8,11,12,13,9,10,55,89,56,56]
    print (identify_ranges(data))
