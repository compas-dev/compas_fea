import compas_fea
from compas.datastructures import VolMesh

from compas_fea.structure import Structure
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import SolidSection
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties
from compas_fea.structure import GravityLoad
from compas_fea.structure import GeneralStep


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


# get mesh from json file ------------------------------------------------------

filepath = compas_fea.get('volmesh_torus.json')
volmesh = VolMesh.from_json(filepath)

# add shell elements from mesh -------------------------------------------------
s = Structure(path=compas_fea.TEMP, name='torus')
s.add_nodes_elements_from_volmesh(volmesh, elset='solids')

# add supports --------------------------------------------------------------

nkeys = list(volmesh.vertices_where({'z': 0}))
s.add_set(name='support_nodes', type='NODE', selection=nkeys)
supppots = FixedDisplacement(name='supports', nodes='support_nodes')
s.add_displacement(supppots)

# add materials and sections -----------------------------------------------
E = 35 * 10 ** 9
v = .02
p = 2400
matname = 'concrete'
concrete = ElasticIsotropic(name=matname, E=E, v=v, p=p)
s.add_material(concrete)
section = SolidSection(name='concrete_sec')
s.add_section(section)
prop = ElementProperties(name='floor', material=matname, section='concrete_sec', elsets=['solids'])
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
