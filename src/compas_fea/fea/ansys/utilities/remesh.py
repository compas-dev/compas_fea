import compas
from compas.datastructures.mesh.mesh import Mesh
from compas_fea.structure import Structure
from compas_fea.fea.ansys.writing.ansys_process import write_preprocess
from compas_fea.fea.ansys.writing.ansys_nodes_elements import write_request_mesh_areas
from compas_fea.fea.ansys import ansys_launch_process
from compas_fea.fea.ansys.reading import get_nodes_elements_from_result_files


def areas_from_mesh(structure, mesh):
    areas = {}
    fkeys = sorted(mesh.face.keys(), key=int)
    for fkey in fkeys:
        face = mesh.face_vertices(fkey, ordered=True)
        areas[fkey] = face
    structure.areas = areas
    return structure


def mesh_from_ansys_results(output_path):
    nodes, elements = get_nodes_elements_from_result_files(output_path)
    nkeys = sorted(nodes.keys(), key=int)
    vertices = [[nodes[k]['x'], nodes[k]['y'], nodes[k]['z']] for k in nkeys]
    fkeys = sorted(elements.keys(), key=int)
    faces = []
    for fk in fkeys:
        face = elements[fk]['topology']
        face = face[:3]
        faces.append(face)
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    return mesh


def ansys_remesh(mesh, output_path, filename, size=None):
    s = Structure()
    s.add_nodes_elements_from_mesh(mesh, 'ShellElement')
    s = areas_from_mesh(s, mesh)
    write_preprocess(output_path, filename)
    write_request_mesh_areas(s, output_path, filename, size=size, smart_size=None, div=None)
    ansys_launch_process(s, output_path, filename)
    mesh = mesh_from_ansys_results(output_path)
    return mesh


if __name__ == '__main__':

    name = 'remesh.txt'
    path = '//Mac/Home/Desktop/ok/'

    mesh = Mesh.from_obj(compas.get_data('faces.obj'))
    mesh = Mesh.from_data(mesh.to_data())
    mesh = ansys_remesh(mesh, path, name, 0.5)
    mesh.plot()
