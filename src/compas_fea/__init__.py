"""
.. _compas_fea:

********************************************************************************
compas_fea
********************************************************************************

.. module:: compas_fea


Interfaces to Finite Element Analysis software built on COMPAS.


.. toctree::
    :maxdepth: 1
    :titlesonly:

    compas_fea.app
    compas_fea.cad
    compas_fea.fea
    compas_fea.structure
    compas_fea.utilities


"""

import os


# Author(s): Andrew Liew (github.com/andrewliew), Tomás Méndez Echenagucia (github.com/tmsmendez)


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


def get(filename):
    filename = filename.strip('/')
    return os.path.abspath(os.path.join(DATA, filename))


__all__ = []
