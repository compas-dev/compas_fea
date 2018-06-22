import json
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import HarmonicStep
from compas_fea.structure import PointLoad
from compas.datastructures.mesh.mesh import Mesh

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def harmonic(mesh, freq_range, freq_steps, damping):
    # add shell elements from mesh ---------------------------------------------
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

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
    prop = ElementProperties(type='SHELL', material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add loads ----------------------------------------------------------------
    # f_pts = geom_data['f_pts']
    # nodes = [s.check_node_exists(pt) for pt in f_pts]
    # s.add_set(name='load_nodes', type='NODE', selection=nodes)
    # load = PointLoad(name='hload', nodes='load_nodes', x=0, y=0, z=1, xx=0, yy=0, zz=0)
    # s.add_load(load)

    # add modal step -----------------------------------------------------------
    step = HarmonicStep(name='harmonic_analysis', displacements=['supports'], loads=['hload'],
                        freq_range=freq_range, freq_steps=freq_steps, damping=damping)
    s.add_step(step)
    fnm = path + 'harmonic.inp'
    ansys.inp_generate(s, filename=fnm)
    # temp = path+'_Temp/'
    s.analyse(path=path, name='harmonic.inp', temp=None, software='ansys')
    return s


if __name__ == '__main__':

    import compas_fea

    with open(compas_fea.get('flat20x20.json'), 'r') as fp:
        data = json.load(fp)
    mesh = Mesh.from_data(data['mesh'])
    pts = data['pts']

    path = compas_fea.TEMP
    freq_range = (50, 55)
    freq_steps = 5
    thick = 0.02
    damping = 0.003
    print mesh
    # harmonic(mesh, freq_range, freq_steps, damping=damping)
