import rhinoscriptsyntax as rs
import os
import compas_rhino as rhino
from compas_fea import structure
from compas_fea.fea import ansys
from compas_fea.fea.ansys.reading import get_nodes_elements_from_result_files
from compas_fea.fea.ansys.reading import get_harmonic_data_from_result_files
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import HarmonicStep
from compas_fea.structure import HarmonicPointLoad
from compas.datastructures.mesh.mesh import Mesh
from math import sqrt
from compas.utilities.colors import i_to_rgb


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


def harmonic(mesh, pts, lpts, freq_range, freq_steps, damping, path, filename):
    # add shell elements from mesh ---------------------------------------------
    s = structure.Structure()
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
    for lpt in lpts:
        nkeys.append(s.check_node_exists(lpt))
    load = HarmonicPointLoad(name='harmonic_load', nodes=nkeys, z=-1)
    s.add_load(load)

    # add modal step -----------------------------------------------------------
    step = HarmonicStep(name='harmonic_analysis', displacements=['supports'],
                        loads=['harmonic_load'], freq_range=freq_range, freq_steps=freq_steps,
                        damping=damping)
    s.add_step(step)
    fnm = path + filename
    ansys.inp_generate(s, filename=fnm, output_path=path)
    s.analyse(path=path, name=filename, fields=None, software='ansys')
    return s


def draw_harmonic_disp(path, amp, name):
    nodes, elements = get_nodes_elements_from_result_files(path)
    har_disp, freqs = get_harmonic_data_from_result_files(path)
    vkeys = sorted(nodes.keys(), key=int)
    vert = [[nodes[k]['x'], nodes[k]['y'], nodes[k]['z']] for k in vkeys]
    fkeys = sorted(elements.keys(), key=int)
    faces = [elements[k]['topology'] for k in fkeys]
    dkeys = sorted(har_disp.keys(), key=int)
    for freq in freqs:
        print freq
        lname = 'freq ' + str(round(freq, 2)) + 'Hz'
        rs.AddLayer(lname)
        rs.CurrentLayer(lname)
        disp = [har_disp[k][freq]['real'] for k in dkeys]
        disp = [[disp[k]['x'] * amp, disp[k]['y'] * amp, disp[k]['z'] * amp] for k in dkeys]
        dvert = []
        dlens = []
        for i in range(len(vert)):
            v = vert[i]
            d = disp[i]
            dlens.append(sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]))
            dvert.append([v[0] + d[0], v[1] + d[1], v[2] + d[2]])
        colors = []
        maxd = max(dlens)
        mind = min(dlens)
        if mind == maxd:
            colors = [0, 0, 0] * len(vert)
        else:
            for dlen in dlens:
                value = (dlen - mind) / (maxd - mind)
                colors.append(i_to_rgb(value))
        rs.AddMesh(dvert, faces, vertex_colors=colors)


if __name__ == '__main__':
    layers = ['s1', 's2']
    path = os.path.dirname(os.path.abspath(__file__)) + '/'
    freq_range = [10, 200]
    freq_steps = 19
    damping = 0.0003
    for layer in layers:
        filename = layer + '.inp'
        pts = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer(layer + '_pts')]
        lpts = [list(rs.PointCoordinates(pt)) for pt in rs.ObjectsByLayer(layer + '_l')]
        guid = rs.ObjectsByLayer(layer)[0]
        mesh = rhino.mesh_from_guid(Mesh, guid)
        harmonic(mesh, pts, lpts, freq_range, freq_steps, damping, path, filename)
        draw_harmonic_disp(path, 10000000, layer)

