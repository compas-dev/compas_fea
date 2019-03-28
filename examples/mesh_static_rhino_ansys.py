import rhinoscriptsyntax as rs

import compas_fea

from compas_fea.cad import rhino

from compas.datastructures import Mesh

from compas_fea.structure import Structure
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import GravityLoad
from compas_fea.structure import GeneralStep

from compas_rhino.helpers import mesh_from_guid


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


# get mesh from rhino layer ----------------------------------------------------

mesh = mesh_from_guid(Mesh, rs.ObjectsByLayer('mesh')[0])

# add shell elements from mesh -------------------------------------------------

name = 'shell_example'
s = Structure(name=name, path=compas_fea.TEMP)
shell_keys = s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')
s.add_set('shell', 'element', shell_keys)

# add supports from rhino layer-------------------------------------------------

pts = rs.ObjectsByLayer('pts')
pts = [rs.PointCoordinates(pt) for pt in pts]
nkeys = []
for pt in pts:
    nkeys.append(s.check_node_exists(pt))
s.add_set(name='support_nodes', type='NODE', selection=nkeys)
supppots = FixedDisplacement(name='supports', nodes='support_nodes')
s.add_displacement(supppots)

# add materials and sections -----------------------------------------------
E = 40 * 10 ** 9
v = .02
p = 2400
thickness = .02
matname = 'concrete'
concrete = ElasticIsotropic(name=matname, E=E, v=v, p=p)
s.add_material(concrete)
section = ShellSection(name='concrete_sec', t=thickness)
s.add_section(section)
prop = ElementProperties(name='floor', material=matname, section='concrete_sec', elsets=['shell'])
s.add_element_properties(prop)

# add gravity load -------------------------------------------------------------

s.add_load(GravityLoad(name='load_gravity', elements=['shell']))

# add steps --------------------------------------------------------------------

step = GeneralStep(name='gravity_step',
                         nlgeom=False,
                         displacements=['supports'],
                         loads=['load_gravity'],
                        type='static')

s.add_steps([step])

s.steps_order = ['gravity_step']

# analyse ----------------------------------------------------------------------

fields = 'all'
s.write_input_file(software='ansys', fields=fields)
s.analyse(software='ansys', cpus=4, delete=True)
s.extract_data(software='ansys', fields=fields, steps='last')

# visualise results ------------------------------------------------------------

rhino.plot_data(s, step='gravity_step', field='uz', scale=100, colorbar_size=0.3)
rhino.plot_reaction_forces(s, step='gravity_step', scale=.001)
