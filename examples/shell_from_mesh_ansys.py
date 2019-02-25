import os
from compas.datastructures import Mesh
from compas.geometry import closest_point_in_cloud
from compas_fea.structure import Structure
from compas_fea.fea import ansys


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


def pin_all_boundary_vertices(mesh):
    bkeys = mesh.vertices_on_boundary()
    mesh.set_vertices_attribute('UX', 0, bkeys)
    mesh.set_vertices_attribute('UY', 0, bkeys)
    mesh.set_vertices_attribute('UZ', 0, bkeys)


def applly_uniform_point_load(mesh, load):
    for vk in mesh.vertices():
        if not mesh.is_vertex_on_boundary(vk):
            mesh.set_vertex_attribute(vk, 'l', load)


def create_variable_thick_shell(mesh, minthick, maxthick):
    bkeys = mesh.vertices_on_boundary()
    bpts = [mesh.get_vertex_attributes(k, ['x', 'y', 'z']) for k in bkeys]
    fkeys = mesh.face.keys()
    dist_dict = {fkey: closest_point_in_cloud(mesh.face_centroid(fkey), bpts)[0] for fkey in mesh.face}
    min_ = min(dist_dict.values())
    max_ = max(dist_dict.values())
    for fkey in fkeys:
        thick = (((dist_dict[fkey] - min_) * (maxthick - minthick)) / (max_ - min_)) + minthick
        mesh.set_face_attribute(fkey, 'thick', thick)


def assign_structure_property_to_mesh_faces(mesh, name, value):
    for fkey in mesh.faces():
        mesh.set_face_attribute(fkey, name, value)


if __name__ == '__main__':

    filename = 'example_From_mesh'
    path = os.path.dirname(os.path.abspath(__file__)) + '/'
    mesh = Mesh.from_obj('../data/quadmesh_planar.obj')
    minthick = .002
    maxthick = .01
    load = (0, 0, -2000)
    E35 = 35 * 10**9
    v = 0.2
    p = 2400
    pin_all_boundary_vertices(mesh)
    applly_uniform_point_load(mesh, load)
    create_variable_thick_shell(mesh, minthick, maxthick)
    assign_structure_property_to_mesh_faces(mesh, 'E', E35)
    assign_structure_property_to_mesh_faces(mesh, 'v', v)
    assign_structure_property_to_mesh_faces(mesh, 'p', p)
    s = Structure.from_mesh(mesh)
    fnm = path + filename
    ansys.inp_generate(s, filename=fnm, out_path=path)
    print s


