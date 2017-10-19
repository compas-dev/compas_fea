"""
compas_fea.utilities.functions
Support functions for the compas_fea package.
"""

from __future__ import print_function
from __future__ import absolute_import

from compas.datastructures.network.algorithms.traversal import network_dijkstra_path

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
    print('***** NumPy functions not imported *****')

try:
    from scipy.interpolate import griddata
    from scipy.sparse import csr_matrix
    from scipy.sparse import find
    from scipy.spatial import Delaunay
    from scipy.spatial import distance_matrix
except ImportError:
    print('***** SciPy functions not imported *****')

try:
    from mayavi import mlab
except ImportError:
    print('***** mayavi not imported *****')

import json


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'colorbar',
    'combine_all_sets',
    'discretise_faces',
    'extrude_mesh',
    'group_keys_by_attribute',
    'group_keys_by_attributes',
    'load_data',
    'network_order',
    'normalise_data',
    'postprocess',
    'process_data',
    'voxels',
]


node_fields = ['RF', 'RM', 'U', 'UR', 'CF', 'CM']
element_fields = ['SF', 'SM', 'SK', 'SE', 'S', 'E', 'PE', 'RBFOR']


def colorbar(fsc, input='array', type=255):
    """ Creates RGB color information from -1 to 1 scaled values.

    Parameters:
        fsc (array, float): (n x 1) array of normalised data, or single float value
        input (str): Input given as an 'array' of numbers or a 'float'.
        type (int): 255 for RGB or 1 for normalised.

    Returns:
        array, list: (n x 3) array of RGB values or single RGB list.
    """
    red = abs(fsc + 0.25) * 2 - 0.5
    green = -abs(fsc - 0.25) * 2 + 1.5
    blue = -(fsc - 0.25) * 2
    if input == 'array':
        rgb = hstack([red, green, blue])
        rgb[rgb > 1] = 1
        rgb[rgb < 0] = 0
        return rgb * type
    elif input == 'float':
        red = max([0, min([1, red])])
        green = max([0, min([1, green])])
        blue = max([0, min([1, blue])])
        return [i * type for i in [red, green, blue]]


def combine_all_sets(sets_a, sets_b):
    """ Combines two nested lists of node or element sets into the minimum
    ammount of set combinations. Is used to determine the necesary element
    property sets, given sets of materials and sections.

    Parameters:
        sets_a (list): First nested list containing lists of element or node keys.
        sets_b (list): Second nested list containing lists of element or node keys.

    Returns:
        dict: A dictionary containing the minimum number of set combinations.
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

    Parameters:
        vertices (list): Co-ordinates of coarse mesh vertices.
        faces (list): Vertex numbers of each face of the coarse mesh.
        target (float): Target length of each triangle.
        min_angle (float): Minimum internal angle of triangles.
        factor (float): Factor on the maximum area of each triangle.
        iterations (int): Number of iterations per face.

    Returns:
        list: Vertices of discretised faces.
        list: Triangles of discretised faces.
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


def extrude_mesh(structure, mesh, nz, dz):
    """ Extrudes a Mesh into cells of many layers.

    Note:
        - Extrusion is along the vertex normals.
        - Elements are added automatically to Structure object.

    Parameters:
        structure (obj): Structure object to update.
        mesh (obj): Mesh datastructure to extrude.
        nz (int): Number of layers.
        dz (float): Layer thickness.

    Returns:
        None
    """
    ki = {}
    for key in list(mesh.vertices()):
        normal = normalize_vector(mesh.vertex_normal(key))
        xyz = mesh.vertex_coordinates(key)
        x, y, z = xyz
        mesh.add_vertex(key='{0}_0'.format(key), attr_dict={'x': x, 'y': y, 'z': z})
        ki['{0}_0'.format(key)] = structure.add_node(xyz)
        for i in range(nz):
            xyzi = add_vectors(xyz, scale_vector(normal, (i + 1) * dz))
            x, y, z = xyzi
            mesh.add_vertex(key='{0}_{1}'.format(key, i + 1), attr_dict={'x': x, 'y': y, 'z': z})
            ki['{0}_{1}'.format(key, i + 1)] = structure.add_node(xyzi)
    for face in list(mesh.faces()):
        vs = mesh.face_vertices(face, ordered=True)
        if len(vs) == 3:
            element_type = 'PentahedronElement'
        elif len(vs) == 4:
            element_type = 'HexahedronElement'
        for i in range(nz):
            bot = ['{0}_{1}'.format(j, i + 0) for j in vs]
            top = ['{0}_{1}'.format(j, i + 1) for j in vs]
            nodes = [ki[j] for j in bot + top]
            structure.add_element(nodes, element_type, acoustic=False, thermal=False)


def group_keys_by_attribute(adict, name, tol='3f'):
    """ Make group keys by shared attribute values.

    Parameters:
        adict (dic): Attribute dictionary.
        name (str): Attribute of interest.
        tol (float): Float tolerance.

    Returns:
        dic: Group dictionary.
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

    Parameters:
        adict (dic): Attribute dictionary.
        name (str): Attributes of interest.
        tol (float): Float tolerance.

    Returns:
        dic: Group dictionary.
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


def load_data(temp, name, step, field, component):
    """ Load data from .json results files.

    Parameters:
        temp (str): Folder where .json results files are stored.
        name (str): Structure name.
        step (str): Name of the Step.
        field (str): Results to plot, e.g. 'U', 'S', 'SM'.
        component (str): The component to plot, e.g. 'U1', 'RF2'.

    Returns:
        array: Original nodal [x, y, z] co-ordinates.
        array: Relative nodal displacements [Ux, Uy, Uz].
        list: Node numbers of each element.
        dic: Complete unprocessed data for field and component.
        int: Number of nodes
    """
    with open('{0}{1}-nodes.json'.format(temp, name), 'r') as f:
        nodes = json.load(f)
    with open('{0}{1}-elements.json'.format(temp, name), 'r') as f:
        elements = json.load(f)
    with open('{0}{1}-{2}-U.json'.format(temp, name, step), 'r') as f:
        u = json.load(f)
    with open('{0}{1}-{2}-{3}.json'.format(temp, name, step, field), 'r') as f:
        data = json.load(f)[component]

    nkeys = sorted(nodes, key=int)
    ekeys = sorted(elements, key=int)
    X = array([nodes[nkey] for nkey in nkeys])
    U = array([[u[i][nkey] for i in ['U1', 'U2', 'U3']] for nkey in nkeys])
    enodes = [elements[ekey] for ekey in ekeys]

    return X, U, enodes, data, len(nkeys)


def network_order(sp_xyz, structure, network):
    """ Extract node and element orders from a Network for a given start-point.

    Parameters:
        sp_xyz (list): Start point co-ordinates.
        structure (obj): Structure object.
        network (obj): Network object.

    Returns:
        list: Ordered nodes.
        list: Ordered elements.
        list: Cumulative lengths at element mid-points.
        float: Total length.
    """
    nodes, elements, arclengths, L = [], [], [], 0
    sp_gkey = geometric_key(sp_xyz, '{0}f'.format(structure.tol))
    leaves = network.leaves()
    leaves_xyz = [network.vertex_coordinates(i) for i in leaves]
    leaves_gkey = [geometric_key(i, '{0}f'.format(structure.tol)) for i in leaves_xyz]
    sp = leaves[leaves_gkey.index(sp_gkey)]
    leaves.remove(sp)
    ep = leaves[0]
    weight = dict(((u, v), 1) for u, v in network.edges())
    weight.update({(v, u): weight[(u, v)] for u, v in network.edges()})
    path = network_dijkstra_path(network.adjacency, weight, sp, ep)
    nodes = [structure.check_node_exists(network.vertex_coordinates(i)) for i in path]

    for i in range(len(nodes) - 1):
        sp = nodes[i]
        ep = nodes[i + 1]
        elements.append(structure.check_element_exists([sp, ep]))
        xyz_sp = structure.node_xyz(sp)
        xyz_ep = structure.node_xyz(ep)
        dL = distance_point_point(xyz_sp, xyz_ep)
        arclengths.append(L + dL / 2.)
        L += dL
    return nodes, elements, arclengths, L


def normalise_data(data, cmin, cmax):
    """ Normalise a vector of data to between -1 and 1.

    Parameters:
        data (array): Unscaled (n x 1) data.
        cmin (float): Cap data values >= cmin.
        cmax (float): Cap data values <= cmax.

    Returns:
        array: -1 to 1 scaled data.
        float: The maximum absolute unscaled value.
    """
    f = asarray(data)
    fmax = cmax if cmax is not None else max(abs(f))
    fmin = cmin if cmin is not None else min(abs(f))
    fabs = max([abs(fmin), abs(fmax)])
    fscaled = f / fabs if fabs else f
    fscaled[fscaled > +1] = +1
    fscaled[fscaled < -1] = -1
    return fscaled, fabs


def postprocess(temp, name, step, field, component, scale, iptype, nodal, cmin, cmax, type, input='array'):
    """ Post-process data from analysis results for given step and field.

    Parameters:
        temp (str): Folder of saved raw data.
        name (str): Structure name.
        step (str): Name of the Step.
        field (str): Results to plot, e.g. 'U', 'S', 'SM'.
        component (str): The component to plot, e.g. 'U1', 'RF2'.
        scale (float): Scale displacements for the deformed plot.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        cmin (float): Minimum cap on colorbar.
        cmax (float): Maximum cap on colorbar.
        type (int): RGB type, 1 or 255.

    Returns:
        float: toc for time taken to process data.
        array: Colors for node data.
        array: Colors for element data.
        array: Colors for nodal data.
        float: Absolute max node or element data value.
        float: Absolute max nodal data value.
        array: Scaled nodal displacements.
        array: Scaled node or element data.
        array: Scaled nodal data.
    """
    tic = time()

    X, dU, enodes, data, n = load_data(temp, name, step, field, component)
    U = X + dU * float(scale)
    fnodes, felements, fnodal = process_data(field, data, iptype, nodal, enodes, n)

    if field in node_fields:
        fscaled, fabs = normalise_data(data=fnodes, cmin=cmin, cmax=cmax)
        cnodes = colorbar(fsc=fscaled, input=input, type=type)
        cnodal, celements = None, None
        nabs, nscaled = None, None

    elif field in element_fields:
        fscaled, fabs = normalise_data(data=felements, cmin=cmin, cmax=cmax)
        nscaled, nabs = normalise_data(data=fnodal, cmin=cmin, cmax=cmax)
        cnodes = None
        celements = colorbar(fsc=fscaled, input=input, type=type)
        cnodal = colorbar(fsc=nscaled, input=input, type=type)

    toc = time() - tic
    return toc, cnodes, celements, cnodal, fabs, nabs, U, fscaled, nscaled


def process_data(field, data, iptype, nodal, enodes, n):
    """ Processes the raw data.

    Parameters:
        field (str): Data field to process, e.g. 'U', 'S', 'SM'.
        data (dic): Unprocessed data.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        enodes (list): Node numbers for each element.
        n (int): Number of nodes.

    Returns:
        array: Data at each node.
        array: Data at each element.
        array: Data at each node from elements.
    """
    dkeys = sorted(data, key=int)

    if field in node_fields:
        felements, fnodal = None, None
        fnodes = array([data[dkey] for dkey in dkeys])[:, newaxis]

    elif field in element_fields:
        fnodes = None
        m = len(dkeys)
        felements = zeros((m, 1))
        for dkey in dkeys:
            fdata = list(data[dkey].values())
            for i in range(len(fdata)):
                if fdata[i] is None:
                    fdata[i] = 0
            if iptype == 'max':
                value = max(fdata)
            elif iptype == 'min':
                value = min(fdata)
            elif iptype == 'mean':
                value = sum(fdata) / len(fdata)
            felements[int(dkey)] = value
        srows, scols = [], []
        for c, i in enumerate(enodes):
            srows.extend([c] * len(i))
            scols.extend(i)
        sdata = [1] * len(srows)
        A = csr_matrix((sdata, (srows, scols)), shape=(m, n))
        AT = A.transpose()
        if nodal == 'mean':
            fnodal = AT.dot(felements) / sum(AT, 1)
        else:
            rows, cols, vals = find(AT)
            dic = {i: [] for i in range(n)}
            for row, col in zip(rows, cols):
                dic[row].append(felements[col, 0])
            fnodal = zeros((n, 1))
            for i in range(n):
                if nodal == 'max':
                    fnodal[i] = max(dic[i])
                elif nodal == 'min':
                    fnodal[i] = min(dic[i])
    return fnodes, felements, fnodal


def voxels(values, vmin, U, vdx, plot=None, indexing=None):
    """ Plot normalised [0 1] values as voxel data.

    Parameters:
        values (array): Normalised data at nodes.
        vmin (float): Cull values below vmin.
        U (array): Nodal co-ordinates.
        vdx (float): Spacing of voxel grid.
        plot (str): 'mayavi'.

    Returns:
        None
    """
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
    return Am


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    vertices = [[1, 3, 4], [2, 0, 3], [4, 4, 1], [3, 3, 3]]
    faces = [[0, 1, 2], [1, 2, 3]]
    pts, fcs = discretise_faces(vertices, faces, target=0.2, min_angle=15, factor=3, iterations=200)
