
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea.heading import Heading
from compas_fea.fea.nodes import Nodes
from compas_fea.fea.elements import Elements
from compas_fea.fea.sets import Sets
from compas_fea.fea.bcs import BCs
from compas_fea.fea.materials import Materials
from compas_fea.fea.steps import Steps


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Writer',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}


class Writer(Steps, Materials, BCs, Sets, Elements, Nodes, Heading):

    """ Initialises base file writer.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """

    def __init__(self, structure, software, filename, fields, ndof=6):

        self.comment   = comments[software]
        self.filename  = filename
        self.ndof      = ndof
        self.software  = software
        self.structure = structure
        self.fields    = fields
        self.spacer    = {'abaqus': ', ', 'opensees': ' ', 'sofistik': ' ', 'ansys':    ' '}


    def __enter__(self):

        self.file = open(self.filename, 'w')
        return self


    def __exit__(self, type, value, traceback):

        self.file.close()


    def blank_line(self):

        self.file.write('{0}\n'.format(self.comment))


    def divider_line(self):

        self.file.write('{0}------------------------------------------------------------------\n'.format(self.comment))


    def write_line(self, line):

        self.file.write('{0}\n'.format(line))


    def write_section(self, section):

        self.divider_line()
        self.write_line('{0} {1}'.format(self.comment, section))
        self.divider_line()


    def write_subsection(self, subsection):

        self.write_line('{0} {1}'.format(self.comment, subsection))
        self.write_line('{0}-{1}'.format(self.comment, '-' * len(subsection)))
        self.blank_line()
