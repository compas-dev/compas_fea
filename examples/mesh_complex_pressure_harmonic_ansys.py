import json
from compas_fea import structure
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import HarmonicStep
from compas_fea.structure import HarmonicPressureLoad
from compas.datastructures.mesh.mesh import Mesh
import math


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


def harmonic_pressure(mesh, pts, freq_list, path, name, damping):
    # add shell elements from mesh ---------------------------------------------
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')
    s.add_set(name='all_elements', type='element', selection=s.elements.keys())

    # add virtual elements -----------------------------------------------------

    for fkey in list(mesh.faces()):
        face = [s.check_node_exists(mesh.vertex_coordinates(i)) for i in mesh.face[fkey]]
        s.add_virtual_element(nodes=face, type='FaceElement')

    # add displacements --------------------------------------------------------
    nkeys = []
    for pt in pts:
        nkeys.append(s.check_node_exists(pt))
    s.add_set(name='support_nodes', type='NODE', selection=nkeys)
    supppots = FixedDisplacement(name='supports', nodes='support_nodes')
    s.add_displacement(supppots)

    # add materials and sections -----------------------------------------------
    E35 = 35 * 10**9
    concrete = ElasticIsotropic(name='MAT_CONCRETE', E=E35, v=0.2, p=2400)
    s.add_material(concrete)
    section = ShellSection(name='SEC_CONCRETE', t=0.020)
    s.add_section(section)
    prop = ElementProperties(name='shell_props', material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['all_elements'])
    s.add_element_properties(prop)

    # add loads ----------------------------------------------------------------

    load = HarmonicPressureLoad(name='pressureload', elements=['virtual_elements'], pressure=3., phase=math.pi / 2.)
    s.add_load(load)

    # add modal step -----------------------------------------------------------
    step = HarmonicStep(name='harmonic_analysis', displacements=['supports'], loads=['pressureload'],
                        freq_list=freq_list, damping=damping)
    s.add_step(step)
    s.set_steps_order(['harmonic_analysis'])

    # analysis -----------------------------------------------------------------
    s.path = path
    s.name = name
    fields = ['all']
    s.write_input_file('ansys', fields=fields)
    s.analyse(software='ansys', cpus=4)
    s.extract_data(software='ansys', fields=fields, steps='last')
    return s


if __name__ == '__main__':

    import compas_fea

    with open(compas_fea.get('flat20x20.json'), 'r') as fp:
        data = json.load(fp)
    mesh = Mesh.from_data(data['mesh'])
    pts = data['pts']

    freq_list = [50, 51, 52, 55]
    thick = 0.02
    damping = 0.003

    path = compas_fea.TEMP
    name = 'harmonic_pressure'

    harmonic_pressure(mesh, pts, freq_list, path, name, damping=damping)
