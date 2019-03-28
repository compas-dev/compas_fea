
import compas_fea

from compas.datastructures import Mesh

from compas_fea.structure import Structure
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ShellSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import GravityLoad
from compas_fea.structure import GeneralStep


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


# get mesh from json file ------------------------------------------------------

mesh = Mesh.from_json(compas_fea.get('flat20x20.json'))

# add shell elements from mesh -------------------------------------------------

name = 'shell_example'
s = Structure(name=name, path=compas_fea.TEMP)
shell_keys = s.add_nodes_elements_from_mesh(mesh, element_type='ShellElement')
s.add_set('shell', 'element', shell_keys)

# add supports --------------------------------------------------------------

nkeys = mesh.vertices_on_boundaries()[0]
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

print s.results
