"""An example compas_fea package use for beam elements."""
import compas_fea
from compas_fea.fea.ansys import ansys
from compas_fea.cad.rhino import rhino
from compas_fea import structure
from math import pi
import rhinoscriptsyntax as rs


# Folders and Structure name
name = 'beam'
path = 'Mac/Home/Desktop/ansys_test/'
temp = 'C:/Temp/'

# Create an empty Structure object named mdl
mdl = structure.Structure()

rs.EnableRedraw(False)

# Clear layers
rs.DeleteObjects(rs.ObjectsByLayer('LINES'))
rs.DeleteObjects(rs.ObjectsByLayer('NSET_LEFT'))
rs.DeleteObjects(rs.ObjectsByLayer('NSET_RIGHT'))

# Create Network from lines
L = 1.0
nx = 100
dx = L / nx
x = [i * dx for i in range(nx + 1)]
rs.CurrentLayer(rs.AddLayer('LINES'))
for i in range(nx):
    rs.AddLine([x[i], 0, 0], [x[i + 1], 0, 0])
network = rhino.network_from_lines(rs.ObjectsByLayer('LINES'))

# Beam ends
rs.CurrentLayer('NSET_LEFT')
rs.AddPoint([x[0], 0, 0])
rs.CurrentLayer('NSET_RIGHT')
rs.AddPoint([x[-1], 0, 0])

# Balls
spacing = 10
ball_weight = -0.1
rs.DeleteObjects(rs.ObjectsByLayer('NSET_BALLS'))
rs.CurrentLayer('NSET_BALLS')
for xi in x[spacing::spacing]:
    rs.AddPoint([xi, 0, 0])

rs.EnableRedraw(True)

# Add beam element and geometry to Structure
rhino.add_nodes_elements_from_network(mdl, network=network, element_type='BEAM')

# Add node and element sets to the Structure object
rhino.sets_from_layers(mdl, layers=['NSET_LEFT', 'NSET_RIGHT', 'NSET_BALLS'])

# Add materials
structure.add_ElasticIsotropic(mdl, name='MAT_ELASTIC', E=20*10**9, v=0.3, p=1500)

# Add sections via function
nodes, elements, elsets, arclengths, L = rhino.ordered_lines(mdl,
    network=network, layer='NSET_LEFT')

for c, i in enumerate(arclengths):
    ri = (((i / L) - 0.5)**2 + 0.4) * 0.01
    sec_name = 'SEC_ROD_{0}_{1}'.format(c, 'NSET_LEFT')
    structure.add_Circular(mdl, name=sec_name, r=ri)
    mdl.add_element_properties(type='BEAM', material='MAT_ELASTIC',
                               section=sec_name, elsets=[elsets[c]])

# Add loads
structure.add_PointLoad(mdl, name='LOAD_BALLS', nodes='NSET_BALLS', z=ball_weight)
structure.add_GravityLoad(mdl, name='LOAD_GRAVITY', elements='ELSET_ALL')

# Add displacements
structure.add_Displacement(mdl, name='DISP_LEFT', nodes='NSET_LEFT',
    x=0, y=0, z=0, xx=0, yy=45*pi/180, zz=0)
structure.add_Displacement(mdl, name='DISP_RIGHT', nodes='NSET_RIGHT',
    x='-', y=0.1, z=0.2, xx='-', yy=0, zz=25*pi/180)

# Add steps
structure.add_Step(mdl, name='S1_BC', nlgeom=True, type='STATIC',
    displacements=['DISP_LEFT', 'DISP_RIGHT'])
structure.add_Step(mdl, name='S2_LOAD', nlgeom=True, type='STATIC',
    loads=['LOAD_GRAVITY', 'LOAD_BALLS'])

# Set steps order
order = ['S1_BC','S2_LOAD']
mdl.set_steps_order(order)

# Structure summary
#mdl.summary()

# Generate .inp file
fnm = path + name + '.inp'
ansys.inp_generate(mdl, filename=fnm)

# # Run and extract data
mdl.analyse(path=path, name=name+'.inp', temp=temp, software='ansys')

# # Load data
# fnm = path + name + '.obj'
# mdl = structure.load(fnm)

# # Plot displacements
# fo, U = rhino.plot_deformed_data(mdl, step='S2_LOAD', field='U',
#     component='magnitude', radius=0.01)
# fo, U = rhino.plot_deformed_data(mdl, step='S2_LOAD', field='UR',
#     component='UR2', radius=0.01)

# # Plot section forces/moments
# fo, U = rhino.plot_deformed_data(mdl, step='S2_LOAD', field='SF',
#     component='SF1', radius=0.01)
# fo, U = rhino.plot_deformed_data(mdl, step='S2_LOAD', field='SF',
#     component='SF3', radius=0.01)
# fo, U = rhino.plot_deformed_data(mdl, step='S2_LOAD', field='SM',
#     component='SM2', radius=0.01)

# # Reactions
# RF = mdl.extract_results('S2_LOAD', field='RF')
# RM = mdl.extract_results('S2_LOAD', field='RM')
# inc = RF.keys()[0]
# l_node = mdl.sets['NSET_LEFT']['selection'][0]
# r_node = mdl.sets['NSET_RIGHT']['selection'][0]
# print('Left reactions')
# print(RF[inc][l_node])
# print(RM[inc][l_node])
# print('Right reactions')
# print(RF[inc][r_node])
# print(RM[inc][r_node])

# print('\nSCRIPT FINISHED\n')
