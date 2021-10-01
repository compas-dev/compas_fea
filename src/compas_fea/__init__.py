"""
********************************************************************************
compas_fea
********************************************************************************

.. currentmodule:: compas_fea


.. toctree::
    :maxdepth: 1

    compas_fea.cad
    compas_fea.fea
    compas_fea.structure
    compas_fea.utilities

"""
from __future__ import print_function

import os

__author__ = ['Andrew Liew (github.com/andrewliew), Tomas Mendez Echenagucia (github.com/tmsmendez)']
__copyright__ = 'Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = ''
__version__ = '0.3.1'

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


__all__ = ['HOME', 'DATA', 'DOCS', 'TEMP']
