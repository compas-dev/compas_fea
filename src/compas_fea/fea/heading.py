
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Heading',
]


class Heading(object):

    def __init__(self):

        pass


    def write_heading(self):

        header = {
            'abaqus':   '*PHYSICAL CONSTANTS, ABSOLUTE ZERO=-273.15, STEFAN BOLTZMANN=5.67e-8',
            'opensees': 'wipe\nmodel basic -ndm 3 -ndf {0}'.format(self.ndof),
            'sofistik': '$',
            'ansys':    '!',
        }

        self.write_section('Heading')
        self.blank_line()
        self.write_line(header[self.software])
        self.blank_line()
        self.blank_line()
