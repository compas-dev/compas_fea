import rhinoscriptsyntax as rs
import os
from compas_rhino.helpers.mesh import mesh_from_guid
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import ModalStep
from compas_fea.cad.rhino import plot_mode_shapes
from compas.datastructures.mesh.mesh import Mesh
from math import sqrt


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


def modal(mesh, pts, num_modes, path, name):
    # add shell elements from mesh ---------------------------------------------
    s = structure.Structure(name=name, path=path)
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

    # add displacements --------------------------------------------------------
    nkeys = []
    for pt in pts:
        nkeys.append(s.check_node_exists(pt))
    s.add_set(name='support_nodes', type='NODE', selection=nkeys)
    supports = PinnedDisplacement(name='supports', nodes='support_nodes')
    s.add_displacement(supports)

    # add materials and sections -----------------------------------------------
    E35 = 35 * 10**9
    concrete = ElasticIsotropic(name='MAT_CONCRETE', E=E35, v=0.2, p=2400)
    s.add_material(concrete)
    section = ShellSection(name='SEC_CONCRETE', t=0.050)
    s.add_section(section)
    prop = ElementProperties(material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add modal step -----------------------------------------------------------

    step = ModalStep(name='modal_analysis', displacements=['supports'], modes=num_modes)
    s.add_step(step)
    s.set_steps_order(['modal_analysis'])

    # analyse ------------------------------------------------------------------
    fields = 'all'
    s.write_input_file(software='ansys', fields=fields)
    s.analyse(software='ansys', cpus=4)
    s.extract_data(software='ansys', fields=fields, steps='last')
    return s

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) + '/'
    num_modes = 6
    name = 's1'
    pts = rs.ObjectsByLayer(name + '_pts')
    pts = [list(rs.PointCoordinates(pt)) for pt in pts]
    guid = rs.ObjectsByLayer(name)[0]
    mesh = mesh_from_guid(Mesh, guid)
    s = modal(mesh, pts, num_modes, path, name)
    plot_mode_shapes(s, 'modal_analysis', layer='mode',scale=100)
