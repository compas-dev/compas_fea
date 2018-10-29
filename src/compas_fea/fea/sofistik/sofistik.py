
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import Writer


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
]


def input_generate(structure, fields=None):

    """ Creates the Sofistik .dat file from the Structure object.

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.

    Returns
    -------
    None

    """

    filename = '{0}{1}.dat'.format(structure.path, structure.name)

    with Writer(structure=structure, software='sofistik', filename=filename) as writer:

        writer.write_heading()
        writer.write_nodes()

    #     write_input_bcs(f, 'sofistik', structure, steps, displacements, sets)
    #     write_input_elements(f, 'sofistik', sections, properties, elements, structure, materials)
    #     write_input_steps(f, 'sofistik', structure, steps, loads, displacements, sets, fields, 6, properties)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))
