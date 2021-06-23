"""
Principal stressess extraction from compas_fea results file.
Author(s): Francesco Ranaudo (github.com/franaudo)

This example shows how to extract the principal stresses from the compas_fea
results file. In the first part, a simple planar structure is generated using
shell elements. Once the analysis is complete, the principal stresses and their
directions are extracted and printed.
"""

import matplotlib.pyplot as plt
from compas_fea.utilities import functions
import numpy as np
from scipy.linalg import hankel
import json
from math import atan2, degrees
from pathlib import Path

from compas_fea.structure import ElasticIsotropic
from compas_fea.structure import ElementProperties as Properties
from compas_fea.structure import GeneralStep
from compas_fea.structure import GravityLoad
from compas_fea.structure import PinnedDisplacement
from compas_fea.structure import ShellSection
from compas_fea.structure import Structure


folder = 'C:/temp/principal_stresses/'
name = 'principal_stresses'

## ------------------------------ PART 1 -------------------------------------##
# Create empty Structure object (nxn plate)

mdl = Structure(name=name, path=folder)

minX, maxX, minY, maxY = 0., 1., 0., 1.
discretization = 5
x = np.linspace(minX, maxX, int((maxX-minX)*discretization+1))
y = np.linspace(minY, maxY,  int((maxY-minY)*discretization+1))
X, Y = np.meshgrid(x, y)
X = X.reshape((np.prod(X.shape),))
Y = Y.reshape((np.prod(Y.shape),))
Z = np.zeros_like(X)
mdl.add_nodes([node for node in zip(X, Y, Z)])

for j in range(int(maxY*discretization)):
    for i in range(int(maxX*discretization)):
        mdl.add_element(nodes=[int(i+((maxX*discretization+1)*j)),
                               int(i+((maxX*discretization+1)*j)+1),
                               int(i+((maxX*discretization+1)*j)+maxX*discretization+2),
                               int(i+((maxX*discretization+1)*j)+maxX*discretization+1)],
                        type='ShellElement')
mdl.add_set(name='nset_base', type='node', selection=[0,
                                                      int(maxX*discretization),
                                                      int((maxX*discretization+1)*(maxY*discretization)),
                                                      int((maxX*discretization+1)*(maxY*discretization+1)-1)])
mdl.add_set(name='elset_shell', type='element', selection=[i for i in mdl.elements.keys()])
mdl.add([ShellSection(name='sec_shell', t=0.05), ])
mdl.add(ElasticIsotropic(name='mat_elastic', E=10*10**9, v=0.3, p=1500))
mdl.add([Properties(name='ep_shell', material='mat_elastic', section='sec_shell', elset='elset_shell'), ])
mdl.add([GravityLoad(name='load_gravity', elements='elset_shell'), ])
mdl.add(PinnedDisplacement(name='disp_pinned', nodes='nset_base'))
mdl.add([
    GeneralStep(name='step_bc', displacements=['disp_pinned']),
    GeneralStep(name='step_loads', loads=['load_gravity']),
])
mdl.steps_order = ['step_bc', 'step_loads']
mdl.summary()
mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])


## ------------------------------ PART 2 -------------------------------------##
# Read the results file
with open(Path(folder).joinpath(name, f"{name}-results.json"), "r") as f:
    results = json.load(f)

step = 'step_loads'
data = results[step]['element']

spr, e = functions.principal_stresses(data)

# check the results for an element
id = 0
stype = 'max'
sp = 'sp1'
print(f'the {stype} principal stress for element {id} is: ', spr[sp][stype][id])
print('principal axes (basis):\n', e[sp][stype][:, id])
print('and its inclination w.r.t. World is: ', degrees(atan2(*e[sp][stype][:, id][::-1])))

# Plot the vectors
X, Y = np.meshgrid(x, y)
x = X[:-1, :-1]+0.5
y = Y[:-1, :-1]+0.5
for stype in ['max', 'min']:
    color = 'r' if stype == 'max' else 'b'
    z = spr[sp][stype]
    u = np.array(np.split(e[sp][stype][0]*spr['sp1'][stype]/2, 5))
    v = np.array(np.split(e[sp][stype][1]*spr['sp1'][stype]/2, 5))
    plt.quiver(x, y, u, v, color=color, width=1*10**-3)
    plt.quiver(x, y, -u, -v, color=color, width=1*10**-3)
plt.show()
