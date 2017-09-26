"""
compas_fea.fea.opensees : OpenSEES file creator.
"""

from __future__ import print_function
from __future__ import absolute_import


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Aryan Rezaei Rad <aryan.rezaeirad@epfl.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
]


# Notes for future file maker

wipe;
model basic -ndm 3 -ndf 6;

# No. x[m] y[m] z[m]
node 1 0.0 0.0 0.0;
node 2 1.0 1.0 1.0;

# No. x y z xx yy zz
fix 1 1 1 1 0 0 0;  # 1 fixed, 0 free

# equalDOF rigidDiaphragm rigidLink for tie constraints etc
