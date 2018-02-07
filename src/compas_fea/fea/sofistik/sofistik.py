
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea import write_input_bcs
from compas_fea.fea import write_input_elements
from compas_fea.fea import write_input_heading
from compas_fea.fea import write_input_materials
from compas_fea.fea import write_input_nodes
from compas_fea.fea import write_input_steps


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'input_generate',
]


dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']


def input_generate(structure, fields, units='m'):

    """ Creates the Sofistik .dat file from the Structure object.

    Parameters
    ----------
    structure : obj
        The Structure object to read from.
    fields : list
        Data field requests.
    units : str
        Units of the nodal co-ordinates 'm','cm','mm'.

    Returns
    -------
    None

    """

    filename = '{0}{1}.dat'.format(structure.path, structure.name)

    if isinstance(fields, str):
        fields = [fields]

    with open(filename, 'w') as f:

        constraints   = structure.constraints
        displacements = structure.displacements
        elements      = structure.elements
        interactions  = structure.interactions
        loads         = structure.loads
        materials     = structure.materials
        misc          = structure.misc
        nodes         = structure.nodes
        properties    = structure.element_properties
        sections      = structure.sections
        sets          = structure.sets
        steps         = structure.steps

        write_input_heading(f, software='sofistik')
        write_input_materials(f, 'sofistik', materials, sections, properties)
        write_input_nodes(f, 'sofistik', nodes)
        write_input_bcs(f, 'sofistik', structure, steps, displacements)
        write_input_elements(f, 'sofistik', sections, properties, elements, structure, materials)
        write_input_steps(f, 'sofistik', structure, steps, loads, displacements, sets, fields,
                          properties=properties, sections=sections)

    print('***** Sofistik input file generated: {0} *****\n'.format(filename))
