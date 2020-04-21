import json
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import ModalStep
from compas_fea.structure import HarmonicStep
from compas_fea.structure import PointLoad
from compas.datastructures import Mesh


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def static(geom_file):
    # add shell elements from mesh ---------------------------------------------
    with open(geom_file, 'rb') as fh:
        geom_data = json.load(fh)
    mesh = Mesh.from_data(geom_data['mesh'])
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

    # add displacements --------------------------------------------------------
    pts = geom_data['pts']
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
    prop = ElementProperties(type='SHELL', material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add loads ----------------------------------------------------------------
    f_pts = geom_data['f_pts']
    nodes = [s.check_node_exists(pt) for pt in f_pts]
    s.add_set(name='load_nodes', type='NODE', selection=nodes)
    load = PointLoad(name='pload', nodes='load_nodes', x=0, y=0, z=1, xx=0, yy=0, zz=0)
    s.add_load(load)

    # add static step -----------------------------------------------------------
    step = GeneralStep(name='static_analysis', displacements=['supports'], loads=['pload'], type='STATIC')
    s.add_step(step)
    fnm = path + 'static.inp'
    ansys.inp_generate(s, filename=fnm)
    # temp = path+'_Temp/'
    # s.analyse(path=path, name='static.inp', temp=None, software='ansys')
    return s


def harmonic(geom_file, freq_range, freq_steps, damping):
    # add shell elements from mesh ---------------------------------------------
    with open(geom_file, 'rb') as fh:
        geom_data = json.load(fh)
    mesh = Mesh.from_data(geom_data['mesh'])
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

    # add displacements --------------------------------------------------------
    pts = geom_data['pts']
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
    prop = ElementProperties(type='SHELL', material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add loads ----------------------------------------------------------------
    f_pts = geom_data['f_pts']
    nodes = [s.check_node_exists(pt) for pt in f_pts]
    s.add_set(name='load_nodes', type='NODE', selection=nodes)
    load = PointLoad(name='hload', nodes='load_nodes', x=0, y=0, z=1, xx=0, yy=0, zz=0)
    s.add_load(load)

    # add modal step -----------------------------------------------------------
    step = HarmonicStep(name='harmonic_analysis', displacements=['supports'], loads=['hload'],
                        freq_range=freq_range, freq_steps=freq_steps, damping=damping)
    s.add_step(step)
    fnm = path + 'harmonic.inp'
    ansys.inp_generate(s, filename=fnm)
    # temp = path+'_Temp/'
    s.analyse(path=path, name='harmonic.inp', temp=None, software='ansys')
    return s


def modal(geom_file, num_modes, path):
    # add shell elements from mesh ---------------------------------------------
    with open(geom_file, 'rb') as fh:
        geom_data = json.load(fh)
    mesh = Mesh.from_data(geom_data['mesh'])
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

    # add displacements --------------------------------------------------------
    pts = geom_data['pts']
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
    prop = ElementProperties(type='SHELL', material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add modal step -----------------------------------------------------------

    step = ModalStep(name='modal_analysis', displacements=['supports'], num_modes=num_modes)
    s.add_step(step)
    fnm = path + 'modal.inp'
    ansys.inp_generate(s, filename=fnm)
    # temp = path + '_Temp/'
    s.analyse(path=path, name='modal.inp', temp=None, software='ansys')
    return s


if __name__ == '__main__':
    # path = 'C:/Users/user/Documents/ansys_test/'
    path = '/Users/mtomas/Desktop/ansys_test/'
    # geom_path = '//Mac/Home/Documents/compas/packages/compas_fea/_data/'
    geom_path = '../_data/'
    freq_range = (10, 200)
    freq_steps = 190
    gfile = 'flat_full_support.json'
    thick = 0.02
    damping = 0.003
    num_modes = 20
    static(geom_path + gfile)
    # modal(geom_path + gfile, num_modes, path)
    # harmonic(geom_path + gfile, freq_range, freq_steps, damping=damping)
