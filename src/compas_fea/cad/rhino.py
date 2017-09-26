"""
compas_fea.cad.rhino : Rhinoceros specific functions.
"""

from subprocess import Popen
from subprocess import PIPE

from compas.datastructures.mesh import Mesh
from compas.datastructures.network import Network

from compas_rhino.helpers.mesh import mesh_from_guid

from compas.geometry import add_vectors
from compas.geometry import centroid_points
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_fea import utilities
from compas_fea.utilities.functions import colorbar
from compas_fea.utilities.functions import extrude_mesh
from compas_fea.utilities.functions import network_order

from math import atan2
from math import cos
from math import sin
from math import pi

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.system() == 'Windows':
        raise

import json


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'add_element_set',
    'add_node_set',
    'add_nodes_elements_from_layers',
    'add_sets_from_layers',
    'mesh_extrude',
    'network_from_lines',
    'ordered_lines',
    'plot_axes',
    'plot_data',
    'plot_principal_stresses',
]


def add_element_set(structure, guids, name, explode=False):
    """ Adds element set information from Rhino curve and mesh guids.

    Note:
        - Meshes representing solids must have 'solid' in their name.

    Parameters:
        structure (obj): Structure object to update.
        guids (list): Rhino curve and Rhino mesh guids.
        name (str): Set name.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    elements = []
    for guid in guids:

        if rs.IsCurve(guid):
            sp = structure.check_node_exists(rs.CurveStartPoint(guid))
            ep = structure.check_node_exists(rs.CurveEndPoint(guid))
            element = structure.check_element_exists([sp, ep])
            if element is not None:
                elements.append(element)

        if rs.IsMesh(guid):
            vertices = rs.MeshVertices(guid)
            faces = rs.MeshFaceVertices(guid)

            if 'solid' in rs.ObjectName(guid):
                nodes = [structure.check_node_exists(i) for i in vertices]
                element = structure.check_element_exists(nodes)
                if element is not None:
                    elements.append(element)

            else:
                for face in faces:
                    nodes = [structure.check_node_exists(vertices[i]) for i in face]
                    if nodes[2] == nodes[3]:
                        nodes = nodes[:-1]
                    element = structure.check_element_exists(nodes)
                    if element is not None:
                        elements.append(element)

    structure.add_set(name=name, type='element', selection=elements, explode=explode)


def add_node_set(structure, guids, name, explode=False):
    """ Adds node set information from Rhino point guids.

    Parameters:
        structure (obj): Structure object to update.
        guids (list): Rhino point guids.
        name (str): Set name.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    nodes = []
    for guid in guids:
        node = structure.check_node_exists(rs.PointCoordinates(guid))
        if node is not None:
            nodes.append(node)
    structure.add_set(name=name, type='node', selection=nodes, explode=explode)


def add_nodes_elements_from_layers(structure, element_type, layers, acoustic=False, thermal=False):
    """ Adds node and element data from Rhino layers to Structure object.

    Note:
        - The element_type should be applicable to all objects in the given layers.

    Parameters:
        structure (obj): Structure object to update.
        element_type (str): Element type: 'TetrahedronElement', 'ShellElement', 'TrussElement' etc.
        layers (list): Layer names to extract nodes or elements from.
        acoustic (bool): Acoustic properties on or off.
        thermal (bool): Thermal properties on or off.

    Returns:
        None: Nodes and elements are updated in the Structure object.
    """
    if isinstance(layers, str):
        layers = [layers]
    for layer in layers:
        guids = rs.ObjectsByLayer(layer)
        for guid in guids:

            if rs.IsCurve(guid):
                sp = structure.add_node(rs.CurveStartPoint(guid))
                ep = structure.add_node(rs.CurveEndPoint(guid))
                try:
                    dic = json.loads(rs.ObjectName(guid).replace("'", '"'))
                    ex = dic.get('ex', None)
                    ey = dic.get('ey', None)
                    axes = {'ex': ex, 'ey': ey}
                except:
                    axes = {}
                structure.add_element(nodes=[sp, ep], type=element_type, acoustic=acoustic, thermal=thermal, axes=axes)

            elif rs.IsMesh(guid):
                vertices = rs.MeshVertices(guid)
                nodes = [structure.add_node(vertex) for vertex in vertices]
                if element_type in ['HexahedronElement', 'TetrahedronElement', 'SolidElement', 'PentahedronElement']:
                    structure.add_element(nodes=nodes, type=element_type, acoustic=acoustic, thermal=thermal)
                else:
                    faces = rs.MeshFaceVertices(guid)
                    for face in faces:
                        nodes = [structure.check_node_exists(vertices[i]) for i in face]
                        if nodes[-1] == nodes[-2]:
                            del nodes[-1]
                        structure.add_element(nodes=nodes, type=element_type, acoustic=acoustic, thermal=thermal)


def add_sets_from_layers(structure, layers, explode=False):
    """ Add node or element sets to the Structure object from layers.

    Note:
        - Layers should exclusively contain nodes or elements.
        - Sets will inherit the layer names as their keys.

    Parameters:
        structure (obj): Structure object to update.
        list (list): List of layer names to take objects from.
        explode (bool): Explode the set into sets for each member of selection.

    Returns:
        None
    """
    if isinstance(layers, str):
        layers = [layers]
    for layer in layers:
        guids = rs.ObjectsByLayer(layer)
        if guids:
            check_points = [rs.IsPoint(guid) for guid in guids]
            name = layer.split('::')[-1] if '::' in layer else layer
            if all(check_points):
                add_node_set(structure=structure, guids=guids, name=name, explode=explode)
            elif not all(check_points):
                add_element_set(structure=structure, guids=guids, name=name, explode=explode)


def mesh_extrude(structure, guid, nz, dz):
    """ Extrudes a Rhino mesh into cells of many layers.

    Note:
        - Extrusion is along the vertex normals.
        - Elements are added automatically to the Structure object.

    Parameters:
        structure (obj): Structure object to update.
        guid (guid): Rhino mesh guid.
        nz (int): Number of layers.
        dz (float): Layer thickness.

    Returns:
        None
    """
    mesh = mesh_from_guid(Mesh(), guid)
    extrude_mesh(structure, mesh, nz, dz)


def network_from_lines(guids):
    """ Creates a Network datastructure object from a list of curve guids.

    Parameters:
        guids (list): guids of the Rhino curves to be made into a Network.

    Returns:
        obj: Network datastructure object.
    """
    lines = [[rs.CurveStartPoint(guid), rs.CurveEndPoint(guid)] for guid in guids]
    return Network.from_lines(lines)


def ordered_lines(structure, network, layer):
    """ Extract node and element orders from a Network for a given start-point.

    Note:
        - Function is for a Network representing a single structural element.

    Parameters:
        structure (obj): Structure object.
        network (obj): Network object.
        layer (str): Layer to extract start-point (Rhino point).

    Returns:
        list: Ordered nodes.
        list: Ordered elements.
        list: Cumulative lengths at element mid-points.
        float: Total length.
    """
    sp_xyz = rs.PointCoordinates(rs.ObjectsByLayer(layer))
    return network_order(sp_xyz, structure, network)


def plot_axes(xyz, e11, e22, e33, sc=1):
    """ Plots a set of axes.

    Note:
        - Axes are plotted in the active layer.

    Parameters:
        xyz (list): Origin of the axes.
        e11 (list): First axis component [x, y, z].
        e22 (list): Second axis component [x, y, z].
        e33 (list): Third axis component [x, y, z].
        sc (float) : Size of the axis lines.

    Returns:
        None
    """
    ex = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e11, sc)))
    ey = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e22, sc)))
    ez = rs.AddLine(xyz, add_vectors(xyz, scale_vector(e33, sc)))
    rs.ObjectColor(ex, [255, 0, 0])
    rs.ObjectColor(ey, [0, 255, 0])
    rs.ObjectColor(ez, [0, 0, 255])


def plot_data(structure, path, name, step, field='U', component='magnitude', scale=1.0, radius=0.05,
              iptype='mean', nodal='mean', cbar=[None, None], layer=None, voxel=None, vdx=0):
    """ Plots analysis results on the deformed shape of the Structure.

    Note:
        - Pipe visualisation of line elements is not based on the element section.

    Parameters:
        structure (obj): Structure object.
        path (str): Folder to saved data.
        name (str): Structure name.
        step (str): Name of the Step.
        field (str): Field to plot, e.g. 'U', 'S', 'SM'.
        component (str): Component to plot, e.g. 'U1', 'RF2'.
        scale (float): Scale displacements for the deformed plot.
        radius (float): Radius of the pipe visualisation meshes.
        iptype (str): 'mean', 'max' or 'min' of an element's integration point data.
        nodal (str): 'mean', 'max' or 'min' for nodal values.
        cbar (list): Minimum and maximum limits on the colorbar.
        layer (str): Layer name for plotting.
        voxel (float): Plot voxel data, and cull values below value voxel (0 1].
        vdx (float): Voxel spacing.

    Returns:
        None
    """

    node_fields = ['RF', 'RM', 'U', 'UR', 'CF', 'CM']
    element_fields = ['SF', 'SM', 'SK', 'SE', 'S', 'E', 'PE', 'RBFOR']

    # Create and clear Rhino layer

    if not layer:
        layer = '{0}-{1}-{2}'.format(step, field, component)
    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))
    rs.EnableRedraw(False)

    # Start postprocess

    script = utilities.__file__.replace('__init__.py', 'postprocess.py')
    temp = '{0}{1}/'.format(path, name)
    cmin = str(cbar[0]) if cbar[0] is not None else 'None'
    cmax = str(cbar[1]) if cbar[1] is not None else 'None'
    voxel = str(voxel) if voxel is not None else 'None'
    args = ['python', script, '--', str(vdx), voxel, cmin, cmax, nodal, iptype, str(scale), temp, name,
            step, field, component]
    p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        line = line.strip()
        print(line)
    stdout, stderr = p.communicate()
    print(stdout)
    print(stderr)

    # Return results

    with open('{0}{1}-elements.json'.format(temp, name), 'r') as f:
        elements = json.load(f)
    with open('{0}{1}-postprocess.json'.format(temp, name), 'r') as f:
        data = json.load(f)
    toc       = data['toc']
    cnodes    = data['cnodes']
    celements = data['celements']
    cnodal    = data['cnodal']
    fabs      = data['fabs']
    nabs      = data['nabs']
    U         = data['U']

    # Print info

    with open('{0}{1}-{2}-info.json'.format(temp, name, step), 'r') as f:
        info = json.load(f)
    print('Step summary: {0}'.format(step))
    print('--------------' + '-' * len(step))
    print('Frame description: {0}'.format(info['description']))
    print('Analysis time: {0:.3f}'.format(info['toc_analysis']))
    print('Extraction time: {0:.3f}'.format(info['toc_extraction']))
    print('Processing time: {0:.3f}'.format(toc))

    # Plot meshes

    mesh_faces = []
    beam_faces = [[0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
    block_faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    for ekey, nodes in elements.items():
        n = len(nodes)

        if n == 2:
            u, v = nodes
            sp, ep = U[u], U[v]
            plane = rs.PlaneFromNormal(sp, subtract_vectors(ep, sp))
            xa = plane.XAxis
            ya = plane.YAxis
            r = radius
            xa_pr = scale_vector(xa, +r)
            xa_mr = scale_vector(xa, -r)
            ya_pr = scale_vector(ya, +r)
            ya_mr = scale_vector(ya, -r)
            pts = [add_vectors(sp, xa_pr), add_vectors(sp, ya_pr),
                   add_vectors(sp, xa_mr), add_vectors(sp, ya_mr),
                   add_vectors(ep, xa_pr), add_vectors(ep, ya_pr),
                   add_vectors(ep, xa_mr), add_vectors(ep, ya_mr)]
            guid = rs.AddMesh(pts, beam_faces)
            if field in node_fields:
                col1 = cnodes[u]
                col2 = cnodes[v]
                rs.MeshVertexColors(guid, [col1] * 4 + [col2] * 4)
            elif field in element_fields:
                col = celements[int(ekey)]
                rs.MeshVertexColors(guid, [col] * 8)
        
        elif n == 3:
            mesh_faces.append(nodes + [nodes[-1]])

        elif n == 4:
            mesh_faces.append(nodes)

        elif n == 8:
            for block in block_faces:
                mesh_faces.append([nodes[i] for i in block])
    if mesh_faces:
        id_mesh = rs.AddMesh(U, mesh_faces)
        if field in node_fields:
            rs.MeshVertexColors(id_mesh, cnodes)
        elif field in element_fields:
            rs.MeshVertexColors(id_mesh, cnodal)

    if field in element_fields:
        fabs = max([fabs, nabs])

    # Plot colorbar

    try:
        guid = rs.ObjectsByLayer('colorbar')
    except:
        rs.CurrentLayer(rs.AddLayer('colorbar'))
        rs.DeleteObjects(rs.ObjectsByLayer('colorbar'))
        x = [i * 0.1 for i in range(11)]
        y = [i * 0.1 - 1 for i in range(2)]
        vertices = [[xi, yi, 0] for yi in y for xi in x]
        faces = [[j * 11 + i, j * 11 + i + 1, (j + 1) * 11 + i + 1, (j + 1) * 11 + i + 0]
                 for i in range(10) for j in range(1)]
        guid = rs.AddMesh(vertices, faces)
        rs.CurrentLayer(layer)

    vertices = rs.MeshVertices(guid)
    n = len(vertices)
    x = [i[0] for i in vertices]
    y = [i[1] for i in vertices]
    xmin = min(x)
    xmax = max(x)
    xran = xmax - xmin
    ymin = min(y)
    colors = [colorbar((x[c] - xmin - xran / 2.) / (xran / 2.), input='float') for c in range(n)]
    id = rs.AddMesh(vertices, rs.MeshFaceVertices(guid))
    rs.MeshVertexColors(id, colors)
    h = xran / 20.
    rs.AddText('{0:.4g}'.format(+fabs), [xmax, ymin - 1.5 * h, 0], height=h)
    rs.AddText('{0:.4g}'.format(-fabs), [xmin, ymin - 1.5 * h, 0], height=h)
    rs.AddText('0', [xmin + xran / 2., ymin - 1.5 * h, 0], height=h)

    # Return to Default layer

    rs.CurrentLayer(rs.AddLayer('Default'))
    rs.LayerVisible('colorbar', False)
    rs.LayerVisible(layer, False)
    rs.EnableRedraw(True)


def plot_principal_stresses(structure, path, name, step, ptype, scale, layer):
    """ Plots the principal stresses of the elements.

    Note:
        - Currently alpha script and for only four-noded S4 shell elements.

    Parameters:
        structure (obj): Structure object.
        path (str): Folder where results files are stored.
        name (str): Structure name.
        step (str): Name of the Step.
        ptype (str): 'max' 'min' for maxPrincipal or minPrincipal stresses.
        scale (float): Scale on the length of the line markers.
        layer (str): Layer name for plotting.

    Returns:
        None
    """

    # Clear and create layer

    if not layer:
        layer = '{0}_principal_{1}'.format(step, ptype)
    rs.CurrentLayer(rs.AddLayer(layer))
    rs.DeleteObjects(rs.ObjectsByLayer(layer))

    # Process and plot

    rs.EnableRedraw(False)

    temp = '{0}{1}/'.format(path, name)
    with open('{0}{1}-{2}-S.json'.format(temp, name, step), 'r') as f:
        S = json.load(f)
    S11, S22, S12, axes = S['S11'], S['S22'], S['S12'], S['axes']
    SPr = S['{0}Principal'.format(ptype)]
    sp1_keys = ['ip3_sp1', 'ip4_sp1', 'ip2_sp1', 'ip1_sp1']
    sp5_keys = ['ip3_sp5', 'ip2_sp5', 'ip4_sp5', 'ip1_sp5']
    ipkeys = sp1_keys + sp5_keys

    for ekey in SPr:
        if len(structure.elements[int(ekey)].nodes) == 4:
            th1 = [0.5 * atan2(S12[ekey][ip], 0.5 * (S11[ekey][ip] - S22[ekey][ip])) for ip in sp1_keys]
            th5 = [0.5 * atan2(S12[ekey][ip], 0.5 * (S11[ekey][ip] - S22[ekey][ip])) for ip in sp5_keys]
            th1m = sum(th1) / len(th1) + pi / 2
            th5m = sum(th5) / len(th5) + pi / 2
            pr1 = [i for i in [SPr[ekey][ip] for ip in sp1_keys] if i is not None]
            pr5 = [i for i in [SPr[ekey][ip] for ip in sp5_keys] if i is not None]
            e11 = centroid_points([axes[ekey][ip][0] for ip in ipkeys])
            e22 = centroid_points([axes[ekey][ip][1] for ip in ipkeys])
            # e33 = centroid_points([axes[ekey][ip][2] for ip in ipkeys])
            c = structure.element_centroid(int(ekey))
            if pr1:
                pr1m = sum(pr1) / len(pr1)
                ex1 = scale_vector(e11, cos(th1m))
                ey1 = scale_vector(e22, sin(th1m))
                er1 = add_vectors(ex1, ey1)
                vec1 = add_vectors(c, scale_vector(er1, (pr1m * scale / 10**7) + 0.0001))
                id1 = rs.AddLine(c, vec1)
                col1 = [255, 0, 0] if pr1m > 0 else [0, 0, 255]
                rs.ObjectColor(id1, col1)
            if pr5:
                pr5m = sum(pr5) / len(pr5)
                ex5 = scale_vector(e11, cos(th5m))
                ey5 = scale_vector(e22, sin(th5m))
                er5 = add_vectors(ex5, ey5)
                vec5 = add_vectors(c, scale_vector(er5, (pr5m * scale / 10**7) + 0.0001))
                id5 = rs.AddLine(c, vec5)
                col5 = [255, 0, 0] if pr5m > 0 else [0, 0, 255]
                rs.ObjectColor(id5, col5)

    rs.EnableRedraw(True)
