from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import add_vectors
from compas.geometry import centroid_points
from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

try:
    from numpy import array
    from numpy import arctan2
    from numpy import cos
    from numpy import dot
    from numpy import newaxis
    from numpy import pi
    from numpy import sin
    from numpy.linalg import inv
except ImportError:
    pass

try:
    from meshpy.tet import MeshInfo
    from meshpy.tet import build
    from meshpy.triangle import MeshInfo as MeshInfo_tri
    from meshpy.triangle import build as build_tri
except ImportError:
    pass


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'discretise_faces',
    'extrude_mesh',
    'tets_from_vertices_faces',
]


def extrude_mesh(structure, mesh, layers, thickness, mesh_name, links_name, blocks_name):
    """Extrudes a Mesh and adds elements to a Structure.

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
    faces = []
    links = []
    blocks = []
    slices = {i: [] for i in range(layers)}

    for key in mesh.vertices():

        normal = normalize_vector(mesh.vertex_normal(key))
        xyz = mesh.vertex_coordinates(key)
        ki['{0}_0'.format(key)] = structure.add_node(xyz)

        for i in range(layers):

            xyzi = add_vectors(xyz, scale_vector(normal, (i + 1) * thickness))
            ki['{0}_{1}'.format(key, i + 1)] = structure.add_node(xyzi)

            if links_name:

                node1 = ki['{0}_{1}'.format(key, i + 0)]
                node2 = ki['{0}_{1}'.format(key, i + 1)]
                L = subtract_vectors(xyzi, xyz)
                ez = normalize_vector(L)
                try:
                    ey = cross_vectors(ez, [1, 0, 0])
                except Exception:
                    pass
                axes = {'ez': ez, 'ey': ey}

                ekey = structure.add_element(nodes=[node1, node2], type='SpringElement', thermal=False, axes=axes)
                structure.elements[ekey].A = mesh.vertex_area(key)
                structure.elements[ekey].L = L
                links.append(ekey)

    for face in mesh.faces():

        vs = mesh.face_vertices(face)

        for i in range(layers):

            bot = ['{0}_{1}'.format(j, i + 0) for j in vs]
            top = ['{0}_{1}'.format(j, i + 1) for j in vs]

            if blocks_name:

                etype = 'PentahedronElement' if len(vs) == 3 else 'HexahedronElement'
                nodes = [ki[j] for j in bot + top]
                ekey = structure.add_element(nodes=nodes, type=etype, thermal=False)
                blocks.append(ekey)
                slices[i].append(ekey)

            if (i == layers - 1) and mesh_name:
                nodes = [ki[j] for j in top]
                ekey = structure.add_element(nodes=nodes, type='ShellElement', acoustic=False, thermal=False)
                faces.append(ekey)

    if blocks_name:
        structure.add_set(name=blocks_name, type='element', selection=blocks)
        for i in range(layers):
            structure.add_set(name='{0}_layer_{1}'.format(blocks_name, i), type='element', selection=slices[i])

    if mesh_name:
        structure.add_set(name=mesh_name, type='element', selection=faces)

    if links:
        structure.add_set(name=links_name, type='element', selection=links)


def discretise_faces(vertices, faces, target, min_angle=15, factor=3):
    """Make discretised triangles from input coarse triangles data.

    Parameters
    ----------
    vertices : list
        Co-ordinates of coarse vertices.
    faces : list
        Vertex indices of each face of the coarse triangles.
    target : float
        Target edge length of each triangle.
    min_angle : float
        Minimum internal angle of triangles.
    factor : float
        Factor on the maximum area of each triangle.

    Returns
    -------
    list
        Vertices of the discretised trianlges.
    list
        Vertex numbers of the discretised trianlges.

    Notes
    -----
    - An experimental script.

    """
    points_all = []
    faces_all = []

    Amax = factor * 0.5 * target**2

    for count, face in enumerate(faces):

        # Seed

        face.append(face[0])

        points = []
        facets = []

        for u, v in zip(face[:-1], face[1:]):
            sp = vertices[u]
            ep = vertices[v]
            vec = subtract_vectors(ep, sp)
            length = length_vector(vec)
            div = length / target
            n = max([1, int(div)])
            for j in range(n):
                points.append(add_vectors(sp, scale_vector(vec, j / n)))
        facets = [[i, i + 1] for i in range(len(points) - 1)]
        facets.append([len(points) - 1, 0])

        # Starting orientation

        cent = centroid_points(points)
        vec1 = subtract_vectors(points[1], points[0])
        vec2 = subtract_vectors(cent, points[0])
        vecn = cross_vectors(vec1, vec2)

        # Rotate about x

        points = array(points).transpose()
        phi = -arctan2(vecn[2], vecn[1]) + 0.5 * pi
        Rx = array([[1, 0, 0], [0, cos(phi), -sin(phi)], [0, sin(phi), cos(phi)]])
        vecn_x = dot(Rx, array(vecn)[:, newaxis])
        points_x = dot(Rx, points)
        Rx_inv = inv(Rx)

        # Rotate about y

        psi = +arctan2(vecn_x[2, 0], vecn_x[0, 0]) - 0.5 * pi
        Ry = array([[cos(psi), 0, sin(psi)], [0, 1, 0], [-sin(psi), 0, cos(psi)]])
        points_y = dot(Ry, points_x)
        Ry_inv = inv(Ry)

        V = points_y.transpose()

        try:

            new_points = [list(i) for i in list(V[:, :2])]

            info = MeshInfo_tri()
            info.set_points(new_points)
            info.set_facets(facets)

            tris = build_tri(info, allow_boundary_steiner=False, min_angle=min_angle, max_volume=Amax)
            new_points = [list(j) + [V[0, 2]] for j in tris.points]
            new_tris = [list(j) for j in tris.elements]

            V = array(new_points)
            points = dot(Ry_inv, V.transpose())
            points_all.append([list(i) for i in list(dot(Rx_inv, points).transpose())])
            faces_all.append(new_tris)

        except Exception:
            print('***** ERROR discretising face {0} *****'.format(count))

    return points_all, faces_all


def tets_from_vertices_faces(vertices, faces, volume=None):
    """Generate tetrahedron points and elements with MeshPy (TetGen).

    Parameters
    ----------
    vertices : list
        List of lists of vertex co-ordinates for the input surface mesh.
    faces : list
        List of lists of face indices for the input surface mesh.
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
        points = [list(i) for i in list(tets.points)]
        elements = [list(i) for i in list(tets.elements)]

        return points, elements

    except Exception:
        print('***** MeshPy failed *****')
