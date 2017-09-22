"""
compas_fea.utilities.postprocess
A sub-process to analyse the output FE data.
"""

import sys
import json
# sys.path.append('F:/')

from compas_fea.utilities.functions import postprocess
from compas_fea.utilities.functions import voxels


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


# Arguments

args = sys.argv
component   = args[-1]
field       = args[-2]
step        = args[-3]
name        = args[-4]
temp        = args[-5]
scale       = args[-6]
iptype      = args[-7]
nodal       = args[-8]
cmax        = args[-9]
cmin        = args[-10]
voxel       = args[-11]
vdx         = sys.argv[-12]
cmin = None if cmin == 'None' else float(cmin)
cmax = None if cmax == 'None' else float(cmax)

# Process data

toc, cnodes, celements, cnodal, fabs, nabs, U, fscaled, nscaled = postprocess(
    temp, name, step, field, component, scale, iptype, nodal, cmin, cmax, 255, 'array')

# mayavi plot for voxels

if voxel != 'None':
    if field in ['RF', 'RM', 'U', 'UR', 'CF', 'CM']:
        vdata = fscaled
    elif field in ['SF', 'SM', 'SK', 'SE', 'S', 'E', 'PE', 'RBFOR']:
        vdata = nscaled
    voxels(values=vdata, vmin=float(voxel), U=U, vdx=float(vdx), plot='mayavi')

# Save results

postprocess = {
    'U':         [list(i) for i in list(U)],
    'cnodes':    [list(i) for i in list(cnodes)] if cnodes is not None else [],
    'cnodal':    [list(i) for i in list(cnodal)] if cnodal is not None else [],
    'celements': [list(i) for i in list(celements)] if celements is not None else [],
    'fabs':      fabs,
    'nabs':      nabs,
    'toc':       toc}
with open('{0}{1}-postprocess.json'.format(temp, name), 'w') as f:
    json.dump(postprocess, f)
