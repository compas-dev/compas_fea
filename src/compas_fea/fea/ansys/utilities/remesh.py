import os

from compas.datastructures import Mesh
from compas.datastructures import VolMesh

from compas_fea.structure import Structure

from compas_fea.fea.ansys.writing.ansys_process import ansys_open_pre_process

from compas_fea.fea.ansys.writing.ansys_nodes_elements import write_request_mesh_areas
from compas_fea.fea.ansys.writing.ansys_nodes_elements import write_request_mesh_volume

from compas_fea.fea.ansys.reading import get_nodes_elements_from_result_files

from compas_fea.fea.ansys import ansys_launch_process


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def areas_from_mesh(structure, mesh):
    areas = {}
    fkeys = sorted(mesh.faces(), key=int)
    for fkey in fkeys:
        face = mesh.face_vertices(fkey)
        areas[fkey] = face
    structure.areas = areas
    return structure


def mesh_from_ansys_results(output_path, name):
    output_path = os.path.join(output_path, name + '_output')
    nodes, elements = get_nodes_elements_from_result_files(output_path)
    nkeys = sorted(nodes.keys(), key=int)
    vertices = [[nodes[k]['x'], nodes[k]['y'], nodes[k]['z']] for k in nkeys]
    fkeys = sorted(elements.keys(), key=int)
    faces = []
    for fk in fkeys:
        face = elements[fk]['nodes']
        face = face[:3]
        faces.append(face)
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    return mesh


def volmesh_from_ansys_results(output_path, name):
    output_path = os.path.join(output_path, name + '_output')
    nodes, elements = get_nodes_elements_from_result_files(output_path)
    nkeys = sorted(nodes.keys(), key=int)
    vertices = [[nodes[k]['x'], nodes[k]['y'], nodes[k]['z']] for k in nkeys]
    ckeys = sorted(elements.keys(), key=int)
    cells = []
    for ck in ckeys:
        i, j, k, l, m, n, o, p = elements[ck]['nodes']
        if k == l:
            cells.append([[i, j, k],
                          [i, j, m],
                          [j, k, m],
                          [k, i, m]])
        else:
            cells.append([[i, j, k, l],
                          [i, j, n, m],
                          [j, k, o, n],
                          [k, l, p, o],
                          [l, i, m, p],
                          [m, n, o, p]])

    mesh = VolMesh.from_vertices_and_cells(vertices, cells)
    return mesh


def ansys_remesh_2d(mesh, output_path, name, size=None):
    s = Structure(output_path, name=name)

    s.add_nodes_elements_from_mesh(mesh, 'ShellElement')
    s = areas_from_mesh(s, mesh)
    filename = name + '.txt.'
    ansys_open_pre_process(output_path, filename)
    write_request_mesh_areas(s, output_path, name, size=size, smart_size=None, div=None)
    ansys_launch_process(output_path, name, cpus=4, license='teaching', delete=True)

    mesh = mesh_from_ansys_results(output_path, name)
    return mesh


def ansys_remesh_3d(mesh, output_path, name, size=None, hex=False, div=None):

    s = Structure(output_path, name=name)

    s.add_nodes_elements_from_mesh(mesh, 'ShellElement')
    s = areas_from_mesh(s, mesh)
    filename = name + '.txt.'
    ansys_open_pre_process(output_path, filename)
    write_request_mesh_volume(s, output_path, name, size=size, hex=hex, div=div)
    ansys_launch_process(output_path, name, cpus=4, license='teaching', delete=True)
    mesh = volmesh_from_ansys_results(output_path, name)
    return mesh
