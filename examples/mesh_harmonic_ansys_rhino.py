import rhinoscriptsyntax as rs
import os
import compas_rhino as rhino
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import HarmonicStep

from compas.datastructures.mesh.mesh import Mesh


__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def harmonic(mesh, pts, lpts, num_modes, path, filename):
    # add shell elements from mesh ---------------------------------------------
    s = structure.Structure()
    s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')

    # add displacements --------------------------------------------------------
    nkeys = []
    for pt in pts:
        nkeys.append(s.check_node_exists(pt))
    s.add_set(name='support_nodes', type='NODE', selection=nkeys)
    supppots = PinnedDisplacement(name='supports', nodes='support_nodes')
    s.add_displacement(supppots)

    # add materials and sections -----------------------------------------------
    E35 = 35 * 10**9
    concrete = ElasticIsotropic(name='MAT_CONCRETE', E=E35, v=0.2, p=2400)
    s.add_material(concrete)
    section = ShellSection(name='SEC_CONCRETE', t=0.050)
    s.add_section(section)
    prop = ElementProperties(material='MAT_CONCRETE', section='SEC_CONCRETE', elsets=['ELSET_ALL'])
    s.add_element_properties(prop)

    # add loads ----------------------------------------------------------------
    loads = []

    # add modal step -----------------------------------------------------------
    freq_range = []
    freq_steps = []
    damping = []
    step = HarmonicStep(name='harmonic_analysis', displacements=['supports'], 
                        loads=loads, freq_range=freq_range, freq_steps=freq_steps,
                        damping=damping)
    s.add_step(step)
    fnm = path + filename
    ansys.inp_generate(s, filename=fnm, out_path=path)
    s.analyse(path=path, name=filename, fields=None, software='ansys')
    return s


if __name__ == '__main__':
    # layers = ['s1', 's2']
    layers = ['s1']
    path = os.path.dirname(os.path.abspath(__file__)) + '/'

    for layer in layers:
        filename = layer + '.inp'
        pts = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer(layer + '_pts')]
        lpts = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer(layer + '_l')]
        guid = rs.ObjectsByLayer(layer)[0]
        mesh = rhino.mesh_from_guid(Mesh, guid)
        harmonic(mesh, pts, lpts, num_modes, path, filename)
