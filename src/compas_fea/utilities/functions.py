from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.geometry import distance_point_point
from compas.topology import dijkstra_path
from compas.utilities import geometric_key

from time import time

from operator import itemgetter
from itertools import groupby

try:
    import numpy as np
except ImportError:
    pass


try:
    # from scipy.interpolate import griddata
    from scipy.sparse import csr_matrix
except ImportError:
    pass


# Author(s): Andrew Liew (github.com/andrewliew)


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
    'mesh_from_shell_elements'
]


def process_data(data, dtype, iptype, nodal, elements, n):
    """Process the raw data.

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

        vn = np.array(data)[:, np.newaxis]
        ve = None

    elif dtype == 'element':

        m = len(elements)
        lengths = np.zeros(m, dtype=np.int64)
        data_array = np.zeros((m, 20), dtype=np.float64)

        iptypes = {'max': 0, 'min': 1, 'mean': 2, 'abs': 3}

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

        A = csr_matrix((vals, (rows, cols)), shape=(m, n))
        AT = A.transpose()

        def _process(data_array, lengths, iptype):

            m = len(lengths)
            ve = np.zeros((m, 1))

            for i in range(m):

                if iptype == 0:
                    ve[i] = max(data_array[i, :lengths[i]])

                elif iptype == 1:
                    ve[i] = min(data_array[i, :lengths[i]])

                elif iptype == 2:
                    ve[i] = np.mean(data_array[i, :lengths[i]])

                elif iptype == 3:
                    ve[i] = max(abs(data_array[i, :lengths[i]]))

            return ve

        def _nodal(rows, cols, nodal, ve, n):

            vn = np.zeros((n, 1))

            for i in range(len(rows)):

                node = cols[i]
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
            vsum = np.asarray(AT.dot(ve))
            vn = vsum / sum(AT, 1)

        else:
            vn = _nodal(rows, cols, 0 if nodal == 'max' else 1, ve, n)

    return vn, ve


def identify_ranges(data):
    """Identifies continuous interger series from a list and returns a list of ranges.

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
    """Creates RGB color information from -1 to 1 scaled values.

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

        rgb = np.hstack([r, g, b])
        rgb[rgb > 1] = 1
        rgb[rgb < 0] = 0

        return rgb * type

    elif input == 'float':

        r = max([0, min([1, r])])
        g = max([0, min([1, g])])
        b = max([0, min([1, b])])

        return [i * type for i in [r, g, b]]


def mesh_from_shell_elements(structure):
    """Returns a Mesh datastructure object from a Structure's ShellElement objects.

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


def _angle(A, B, C):
    AB = B - A
    BC = C - B
    th = np.arccos(sum(AB * BC) / (np.sqrt(sum(AB**2)) * np.sqrt(sum(BC**2)))) * 180 / np.pi
    return th


def _centre(p1, p2, p3):
    ax, ay = p1[0], p1[1]
    bx, by = p2[0], p2[1]
    cx, cy = p3[0], p3[1]
    a = bx - ax
    b = by - ay
    c = cx - ax
    d = cy - ay
    e = a * (ax + bx) + b * (ay + by)
    f = c * (ax + cx) + d * (ay + cy)
    g = 2 * (a * (cy - by) - b * (cx - bx))
    centerx = (d * e - b * f) / g
    centery = (a * f - c * e) / g
    r = np.sqrt((ax - centerx)**2 + (ay - centery)**2)

    return [centerx, centery, 0], r


def combine_all_sets(sets_a, sets_b):
    """Combines two nested lists of node or element sets into the minimum ammount of set combinations.

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


def group_keys_by_attribute(adict, name, tol='3f'):
    """Make group keys by shared attribute values.

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
    """Make group keys by shared values of attributes.

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
    """Extract node and element orders from a Network for a given start-point.

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

    adjacency = {i: network.neighbors(i) for i in network.nodes()}
    weight = {(u, v): 1 for u, v in network.edges()}
    weight.update({(v, u): weight[(u, v)] for u, v in network.edges()})
    path = dijkstra_path(adjacency, weight, start, end)
    nodes = [structure.check_node_exists(network.node_coordinates(i)) for i in path]
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
    """Normalise a vector of data to between -1 and 1.

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
    f = np.asarray(data)
    fmax = cmax if cmax is not None else max(abs(f))
    fmin = cmin if cmin is not None else min(abs(f))
    fabs = max([abs(fmin), abs(fmax)])
    fscaled = f / fabs if fabs else f
    fscaled[fscaled > +1] = +1
    fscaled[fscaled < -1] = -1

    return fscaled, fabs


def postprocess(nodes, elements, ux, uy, uz, data, dtype, scale, cbar, ctype, iptype, nodal):
    """Post-process data from analysis results for given step and field.

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

    dU = np.hstack((np.array(ux)[:, np.newaxis], np.array(uy)[:, np.newaxis], np.array(uz)[:, np.newaxis]))
    U = [list(i) for i in list(np.array(nodes) + scale * dU)]

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

    toc = time() - tic
    cnodes_ = [list(i) for i in list(cnodes)]
    fabs_ = float(fabs)
    fscaled_ = [float(i) for i in list(fscaled)]

    return toc, U, cnodes_, fabs_, fscaled_, celements_, float(eabs)


# def plotvoxels(values, U, vdx, indexing=None):
#     """Plot values as voxel data.

#     Parameters
#     ----------
#     values : array
#         Normalised data at nodes.
#     U : array
#         Nodal co-ordinates.
#     vdx : float
#         Representative volume size for a voxel.

#     Returns
#     -------
#     None

#     """

#     U = np.array(U)
#     x = U[:, 0]
#     y = U[:, 1]
#     z = U[:, 2]
#     xmin, xmax = min(x), max(x)
#     ymin, ymax = min(y), max(y)
#     zmin, zmax = min(z), max(z)
#     X = np.linspace(xmin, xmax, (xmax - xmin) / vdx)
#     Y = np.linspace(ymin, ymax, (ymax - ymin) / vdx)
#     Z = np.linspace(zmin, zmax, (zmax - zmin) / vdx)
#     Xm, Ym, Zm = np.meshgrid(X, Y, Z)
#     # Zm, Ym, Xm = meshgrid(X, Y, Z, indexing='ij')

#     f = abs(np.asarray(values))
#     Am = np.squeeze(griddata(U, f, (Xm, Ym, Zm), method='linear', fill_value=0))
#     Am[np.isnan(Am)] = 0

#     voxels = VtkViewer(data={'voxels': Am})
#     voxels.setup()
#     voxels.start()

#     return Am


def principal_stresses(data):
    """ Performs principal stress calculations solving the eigenvalues problem.

    Parameters
    ----------
    data : dic
        Element data from structure.results for the Step.

    Returns
    -------
    spr: dict
        dictionary with the principal stresses of each element organised per
        `stress_type` ('max', 'min') and `section_point` ('sp1, 'sp5').
        {section_point: {stress_type: array([element_0, elemnt_1, ...])}}
    e: dict
        dictionary with the principal stresses vector components in World coordinates
        of each element organised per `stress_type` ('max', 'min') and
        `section_point` ('sp1, 'sp5').
        {section_point: {stress_type: array([element_0_x, elemnt_1_x, ...],
        [element_0_y, elemnt_1_y, ...])}}

    Warnings
    --------
    The function is experimental and works only for shell elements at the moment.
    """
    components = ['sxx', 'sxy', 'syy']
    stype = ['max', 'min']
    section_points = ['sp1', 'sp5']

    stress_results = list(zip(*[data[stress_name].values() for stress_name in components]))
    spr = {sp: {st: np.zeros((len(stress_results))) for st in stype} for sp in section_points}
    e = {sp: {k: np.zeros((2, len(stress_results))) for k in stype} for sp in section_points}
    for sp in section_points:
        for c, element_stresses in enumerate(stress_results):
            # Stresses are computed as mean values of the integration points
            stress_vector = [np.mean(np.array([v for k, v in i.items() if sp in k])) for i in element_stresses]
            # The principal stresses and their directions are computed solving the eigenvalues problem
            stress_matrix = np.array([(stress_vector[0], stress_vector[1]),
                                      (stress_vector[1], stress_vector[2])])
            w_sp, v_sp = np.linalg.eig(stress_matrix)
            for v, k in enumerate(stype):
                spr[sp][k][c] += w_sp[v]
                e[sp][k][:, c] += v_sp[:, v]

    return spr, e
