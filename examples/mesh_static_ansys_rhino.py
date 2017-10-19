import rhinoscriptsyntax as rs
import os
from compas_rhino.helpers.mesh import mesh_from_guid
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import GeneralStep
from compas_fea.structure import PointLoad
from compas.datastructures.mesh.mesh import Mesh

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def static(mesh, pts, lpts1, lpts2, path, name):

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

    # add loads ----------------------------------------------------------------
    nkeys = []
    for lpt in lpts1:
        nkeys.append(s.check_node_exists(lpt))
    load = PointLoad(name='point_load1', nodes=nkeys, z=-1)
    s.add_load(load)

    nkeys = []
    for lpt in lpts2:
        nkeys.append(s.check_node_exists(lpt))
    load = PointLoad(name='point_load2', nodes=nkeys, z=-1)
    s.add_load(load)

    # add steps ----------------------------------------------------------------
    step = GeneralStep('step1', displacements=['supports'], loads=['point_load1'],
    nlgeom=False)
    s.add_step(step)
    
    step = GeneralStep('step2', loads=['point_load2'],
    nlgeom=False)
    s.add_step(step)
    s.set_steps_order(['step1', 'step2'])
    
    # analyse ------------------------------------------------------------------
    fields = ['U']
    s.write_input_file(software='ansys', fields=fields)
    s.analyse(software='ansys', fields=fields)
    # s.extract_data(software='ansys', fields=fields)
    return s

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) + '/'
    name = 'ansys_static'
    pts = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer('pts')]
    lpts1 = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer('lpts1')]
    lpts2 = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer('lpts2')]
    guid = rs.ObjectsByLayer('mesh')[0]
    mesh = mesh_from_guid(Mesh, guid)
    static(mesh, pts, lpts1, lpts2, path, name)
