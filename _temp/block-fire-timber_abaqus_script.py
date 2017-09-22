"""An example scripted compas_fea package use."""

# Note that the script is based on Python 3.

from compas_fea.fea.abaq import abaq
from compas_fea.structure import ThermalMaterial
from compas_fea.structure import HeatTransfer
from compas_fea.structure import Amplitude
from compas_fea.structure import CircularSection
from compas_fea.structure import SolidSection
from compas_fea.structure import ElementProperties
from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ConcreteDamagedPlasticity
from compas_fea.structure import HeatStep
from compas_fea.structure import GeneralStep
from compas_fea.structure import TieConstraint
from compas_fea.structure import PointLoad
from compas_fea.structure import GravityLoad
from compas_fea.structure import Temperature
from compas_fea.structure import RollerY_Displacement
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import GeneralDisplacement
from compas_fea.structure import FixedDisplacement
from compas_fea.structure import structure

from math import sin
from math import pi


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Parameters ------------------------------------------------------------------

nx = 10  # number of divisions in x
ny = 100  # number of divisions in y
nz = 10  # number of divisions in z (should be compatible/divisible with layer properties)
L = 5.0  # length of column
b = 0.5  # width of column
h = 0.5  # height of column
d0 = 0.1  # initial mid-span deflection
dpin = 0.100  # distance of pin from ends
r = 1.000  # radius of pin (controls stiffness)
conductivity = [  # conductivity of each layer
    [[0.12, 20], [0.15, 200], [0.07, 350], [0.09, 500], [0.35, 800], [1.50, 1200]],
    [[0.12, 20], [0.15, 200], [0.07, 350], [0.09, 500], [0.35, 800], [1.50, 1200]],
    [[0.12, 20], [0.15, 200], [0.07, 350], [0.09, 500], [0.35, 800], [1.50, 1200]],
    [[0.12, 20], [0.15, 200], [0.07, 350], [0.09, 500], [0.35, 800], [1.50, 1200]],
    [[0.12, 20], [0.15, 200], [0.07, 350], [0.09, 500], [0.35, 800], [1.50, 1200]]
]
density = [  # density of each layer
    [[450, 20], [450, 99], [450, 100], [402, 120], [402, 121], [402, 200], [374, 250], [305, 300], [209, 350], [153, 400], [113, 600], [104, 800], [0, 1200]],
    [[450, 20], [450, 99], [450, 100], [402, 120], [402, 121], [402, 200], [374, 250], [305, 300], [209, 350], [153, 400], [113, 600], [104, 800], [0, 1200]],
    [[450, 20], [450, 99], [450, 100], [402, 120], [402, 121], [402, 200], [374, 250], [305, 300], [209, 350], [153, 400], [113, 600], [104, 800], [0, 1200]],
    [[450, 20], [450, 99], [450, 100], [402, 120], [402, 121], [402, 200], [374, 250], [305, 300], [209, 350], [153, 400], [113, 600], [104, 800], [0, 1200]],
    [[450, 20], [450, 99], [450, 100], [402, 120], [402, 121], [402, 200], [374, 250], [305, 300], [209, 350], [153, 400], [113, 600], [104, 800], [0, 1200]]
]
sheat = [  # specific heat of each layer
    [[1530, 20], [1770, 99], [13600, 100], [13500, 120], [2120, 121], [2000, 200], [1620, 250], [710, 300], [850, 350], [1000, 400], [1400, 600], [1650, 800], [1650, 1200]],
    [[1530, 20], [1770, 99], [13600, 100], [13500, 120], [2120, 121], [2000, 200], [1620, 250], [710, 300], [850, 350], [1000, 400], [1400, 600], [1650, 800], [1650, 1200]],
    [[1530, 20], [1770, 99], [13600, 100], [13500, 120], [2120, 121], [2000, 200], [1620, 250], [710, 300], [850, 350], [1000, 400], [1400, 600], [1650, 800], [1650, 1200]],
    [[1530, 20], [1770, 99], [13600, 100], [13500, 120], [2120, 121], [2000, 200], [1620, 250], [710, 300], [850, 350], [1000, 400], [1400, 600], [1650, 800], [1650, 1200]],
    [[1530, 20], [1770, 99], [13600, 100], [13500, 120], [2120, 121], [2000, 200], [1620, 250], [710, 300], [850, 350], [1000, 400], [1400, 600], [1650, 800], [1650, 1200]]
]
amplitude = [  # fire curve amplitude
    [0, 0.0191],
    [360, 0.5749],
    [720, 0.6725],
    [1080, 0.7299],
    [1440, 0.7707],
    [1800, 0.8024],
    [2160, 0.8284],
    [2520, 0.8503],
    [2880, 0.8694],
    [3240, 0.8861],
    [3600, 0.9011],
    [3960, 0.9147],
    [4320, 0.9271],
    [4680, 0.9386],
    [5040, 0.9491],
    [5400, 0.9590],
    [5760, 0.9682],
    [6120, 0.9768],
    [6480, 0.9850],
    [6840, 0.9927],
    [7200, 1]]
E = [  # Young's modulus of each layer
    [[30 * 10**9, 20], [15 * 10**9, 100], [300 * 10**6, 300]],
    [[30 * 10**9, 20], [15 * 10**9, 100], [300 * 10**6, 300]],
    [[30 * 10**9, 20], [15 * 10**9, 100], [300 * 10**6, 300]],
    [[30 * 10**9, 20], [15 * 10**9, 100], [300 * 10**6, 300]],
    [[30 * 10**9, 20], [15 * 10**9, 100], [300 * 10**6, 300]]
]
v = [  # Poisson's ratio of each layer
    [[0.3, 20], [0.3, 100], [0.3, 300]],
    [[0.3, 20], [0.3, 100], [0.3, 300]],
    [[0.3, 20], [0.3, 100], [0.3, 300]],
    [[0.3, 20], [0.3, 100], [0.3, 300]],
    [[0.3, 20], [0.3, 100], [0.3, 300]]
]
damage = [  # damage parameters of each layer
    [35, 0.15, 1.16, 0.66, 0.0],
    [35, 0.15, 1.16, 0.66, 0.0],
    [35, 0.15, 1.16, 0.66, 0.0],
    [35, 0.15, 1.16, 0.66, 0.0],
    [35, 0.15, 1.16, 0.66, 0.0]]
hardening = [  # hardening parameters of each layer
    [[55 * 10**6, 0, ' ', 20], [13.8 * 10**6, 0, ' ', 100], [0.5 * 10**6, 0, ' ', 300]],
    [[55 * 10**6, 0, ' ', 20], [13.8 * 10**6, 0, ' ', 100], [0.5 * 10**6, 0, ' ', 300]],
    [[55 * 10**6, 0, ' ', 20], [13.8 * 10**6, 0, ' ', 100], [0.5 * 10**6, 0, ' ', 300]],
    [[55 * 10**6, 0, ' ', 20], [13.8 * 10**6, 0, ' ', 100], [0.5 * 10**6, 0, ' ', 300]],
    [[55 * 10**6, 0, ' ', 20], [13.8 * 10**6, 0, ' ', 100], [0.5 * 10**6, 0, ' ', 300]]]
stiffening = [  # stiffening parameters of each layer
    [[50.0 * 10**6, 1.0, ' ', 20], [32.5 * 10**6, 1.0, ' ', 100], [0.5 * 10**6, 1.0, ' ', 300]],
    [[50.0 * 10**6, 1.0, ' ', 20], [32.5 * 10**6, 1.0, ' ', 100], [0.5 * 10**6, 1.0, ' ', 300]],
    [[50.0 * 10**6, 1.0, ' ', 20], [32.5 * 10**6, 1.0, ' ', 100], [0.5 * 10**6, 1.0, ' ', 300]],
    [[50.0 * 10**6, 1.0, ' ', 20], [32.5 * 10**6, 1.0, ' ', 100], [0.5 * 10**6, 1.0, ' ', 300]],
    [[50.0 * 10**6, 1.0, ' ', 20], [32.5 * 10**6, 1.0, ' ', 100], [0.5 * 10**6, 1.0, ' ', 300]]]
increments = 10000000  # max number of increments in step
t0 = 20  # ambient temperature before fire
dt = 10  # times step in seconds
duration = 4000  # duration of the fire
sink_t = 1049.04  # sink temperature
film_c = 25  # film coefficient
ambient_t = 1049.04  # ambient temperature (better name?)
emissivity = 0.8  # emissivity
total_load = -50000  # total applied load in Newtons

# Mesh ------------------------------------------------------------------------

# Create base grid

dx = b / nx
dy = L / ny
dz = h / nz
x = [i * dx for i in range(nx + 1)]
y = [i * dy for i in range(ny + 1)]
points = [[xi, yi, 0] for yi in y for xi in x]
faces = [[(j + 0) * (nx + 1) + i + 0, (j + 0) * (nx + 1) + i + 1,
          (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 0]
         for i in range(nx) for j in range(ny)]

# Extrude grid

vertices = {}
for c, xyz in enumerate(points):
    x, y, z = xyz
    for i in range(nz + 1):
        xyz_ = [x, y, z + i * dz]
        vertices['{0}_{1}'.format(c, i)] = xyz_
nlayers = len(density)
divisions = nz / nlayers
layer_sets = {str(i): [] for i in range(nlayers)}
blocks = []
for face in faces:
    for i in range(nz):
        bot = ['{0}_{1}'.format(j, i + 0) for j in face]
        top = ['{0}_{1}'.format(j, i + 1) for j in face]
        layer_sets[str(int(i // divisions))].append(len(blocks))
        blocks.append(bot + top)

# Create a Structure object named mdl and add nodes and elements

mdl = structure.Structure()
for block in blocks:
    xyzs = [vertices[i] for i in block]
    nodes = [mdl.add_node(i) for i in xyzs]
    mdl.add_element(nodes, 'HexahedronElement', thermal=True)

# Outer surface

surface_nodes = []
for node in mdl.nodes:
    x = mdl.nodes[node]['x']
    z = mdl.nodes[node]['z']
    if (x == 0) or (x == b) or (z == 0) or (z == h):
        surface_nodes.append(node)
surface_nodes = set(surface_nodes)
mdl.sets['OUTER_SURFACE'] = {'type': 'SURFACE', 'selection': {}}
faces = {'S1': [0, 1, 2, 3], 'S2': [4, 5, 6, 7], 'S3': [0, 1, 4, 5],
         'S4': [1, 2, 5, 6], 'S5': [2, 3, 6, 7], 'S6': [0, 3, 4, 7]}
for element in mdl.elements:
    sids = []
    enodes = mdl.elements[element].nodes
    for skey in faces:
        fnodes = set([enodes[i] for i in faces[skey]])
        if fnodes <= surface_nodes:
            sids.append(skey)
    if sids:
        mdl.sets['OUTER_SURFACE']['selection'][element] = sids
for i in layer_sets.keys():
    mdl.add_set('ELSET_LAYER_{0}'.format(i), 'ELEMENT', layer_sets[i])

# Add sets

nodes_top = []
nodes_bot = []
for node in mdl.nodes.keys():
    y = mdl.nodes[node]['y']
    if y == 0:
        nodes_bot.append(node)
    elif y == L:
        nodes_top.append(node)
mdl.add_set('NSET_TOP', 'NODE', nodes_top)
mdl.add_set('NSET_BOT', 'NODE', nodes_bot)

# Create imperfection

for node in mdl.nodes:
    mdl.nodes[node]['z'] += d0 * sin(pi * mdl.nodes[node]['y'] / L)

# Thermal ---------------------------------------------------------------------

# Folders and Structure name

name = 'block_thermal'
path = '/home/al/Dropbox/'
temp = '/home/al/Temp/'

# Add sections

mdl.add_section(SolidSection(name='SEC_SOLID'))

# Add materials

for i in range(nlayers):
    mname = 'MAT_THERMAL_{0}'.format(i)
    ename = 'ELSET_LAYER_{0}'.format(i)
    mdl.add_material(ThermalMaterial(mname, conductivity[i], density[i], sheat[i]))
    mdl.add_element_properties(ElementProperties(type='HEXAHEDRON', material=mname, section='SEC_SOLID', elsets=ename))

# Add amplitude

mdl.add_misc(Amplitude(name='AMPLITUDE', values=amplitude))

# Create heat transfer

mdl.add_interaction(HeatTransfer(name='HEAT_TRANSFER', amplitude='AMPLITUDE', interface='OUTER_SURFACE', sink_t=sink_t,
                                 film_c=film_c, ambient_t=ambient_t,emissivity=emissivity))

# Add steps

mdl.add_step(HeatStep(name='STEP_HEAT', increments=increments, duration=duration, interaction='HEAT_TRANSFER', temp0=t0, deltmx=dt))
mdl.set_steps_order(['STEP_HEAT'])

# Structure summary

mdl.summary()

# Generate .inp file

fnl = path + name + '.inp'
abaq.inp_generate(mdl, filename=fnl)

# Run
# success = mdl.analyse(path, name, temp, software='abaqus', cpus=2)

# Mechanical ------------------------------------------------------------------

# Turn off thermal

mdl.element_properties = {}
mdl.misc = {}
mdl.materials = {}
mdl.interactions = {}
mdl.steps = {}
for element in mdl.elements:
    mdl.elements[element].thermal = False

# Create pins

x = [i * dx for i in range(nx + 1)]
nodes_pin_top = [mdl.add_node([i, L + dpin, h / 2]) for i in x]
nodes_pin_bot = [mdl.add_node([i, 0 - dpin, h / 2]) for i in x]
elements_pin_top = [mdl.add_element([nodes_pin_top[i], nodes_pin_top[i + 1]], 'BeamElement') for i in range(nx)]
elements_pin_bot = [mdl.add_element([nodes_pin_bot[i], nodes_pin_bot[i + 1]], 'BeamElement') for i in range(nx)]

# Create sets

mdl.add_set(name='ELSET_PIN_TOP', type='ELEMENT', selection=elements_pin_top)
mdl.add_set(name='ELSET_PIN_BOT', type='ELEMENT', selection=elements_pin_bot)
mdl.add_set(name='NSET_PIN_TOP_ENDS', type='NODE', selection=[nodes_pin_top[0], nodes_pin_top[-1]])
mdl.add_set(name='NSET_PIN_BOT_ENDS', type='NODE', selection=[nodes_pin_bot[0], nodes_pin_bot[-1]])
mdl.add_set(name='NSET_PIN_TOP_INTERNAL', type='NODE', selection=nodes_pin_top[1:-1])
mdl.add_set(name='NSET_PIN_BOT_INTERNAL', type='NODE', selection=nodes_pin_bot[1:-1])

# Add materials

mdl.add_material(ElasticIsotropic(name='MAT_STEEL', E=210 * 10**9, v=0.3, p=10.**(-10)))
for i in range(nlayers):
    mname = 'MAT_TIMBER_{0}'.format(i)
    ename = 'ELSET_LAYER_{0}'.format(i)
    mdl.add_material(ConcreteDamagedPlasticity(mname, E=E[i], v=v[i], p=density[i], damage=damage[i],
                                               hardening=hardening[i], stiffening=stiffening[i]))
    mdl.add_element_properties(ElementProperties(type='HexahedronElement', material=mname, section='SEC_SOLID', elsets=ename))

# Add tie constraints

mdl.add_constraint(TieConstraint(name='CON_TIE_BOT', master='NSET_PIN_BOT_INTERNAL', slave='NSET_BOT', tol=1.0))
mdl.add_constraint(TieConstraint(name='CON_TIE_TOP', master='NSET_PIN_TOP_INTERNAL', slave='NSET_TOP', tol=1.0))

# Add sections

mdl.add_section(CircularSection(name='SEC_BAR', r=r))
mdl.add_element_properties(ElementProperties(type='BeamElement', material='MAT_STEEL', section='SEC_BAR', elsets='ELSET_PIN_BOT'))
mdl.add_element_properties(ElementProperties(type='BeamElement', material='MAT_STEEL', section='SEC_BAR', elsets='ELSET_PIN_TOP'))

# Add temperatures

mdl.add_misc(Temperature(name='THERMAL_TEMPS', file='{0}{1}.odb'.format(temp, name), einc=4000))

# Add loads

N = total_load / len(nodes_pin_top)
mdl.add_load(PointLoad(name='LOAD_TOP', nodes='NSET_TOP', y=N))
mdl.add_load(GravityLoad(name='LOAD_GRAVITY', elements='ELSET_ALL', x=0, y=1, z=0))

# Add displacements

mdl.add_displacement(RollerY_Displacement(name='DISP_TOP_INTERNAL', nodes='NSET_PIN_TOP_INTERNAL'))
mdl.add_displacement(PinnedDisplacement(name='DISP_BOT_INTERNAL', nodes='NSET_PIN_BOT_INTERNAL'))
mdl.add_displacement(GeneralDisplacement(name='DISP_TOP_ENDS', nodes='NSET_PIN_TOP_ENDS', x=0, z=0, xx=0, yy=0, zz=0))
mdl.add_displacement(FixedDisplacement(name='DISP_BOT_ENDS', nodes='NSET_PIN_BOT_ENDS'))

# Add steps

mdl.add_step(GeneralStep(name='BC', nlgeom=False, type='STATIC', displacements=['DISP_TOP_INTERNAL', 'DISP_BOT_INTERNAL',
                        'DISP_TOP_ENDS', 'DISP_BOT_ENDS']))
mdl.add_step(GeneralStep(name='LOADS', nlgeom=False, type='STATIC', loads=['LOAD_GRAVITY', 'LOAD_TOP']))
mdl.add_step(GeneralStep(name='OVEN', nlgeom=False, type='STATIC', temperatures='THERMAL_TEMPS', increments=1000, duration=4000))
mdl.set_steps_order(['BC', 'LOADS', 'OVEN'])

# Structure summary

mdl.summary()

# Generate .inp file

name = 'block_mechanical'
fnl = path + name + '.inp'
abaq.inp_generate(mdl, filename=fnl)

# Process data ----------------------------------------------------------------
