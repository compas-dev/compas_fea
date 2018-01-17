
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'write_input_steps',
]


comments = {
    'abaqus':   '**',
    'opensees': '#',
    'sofistik': '$',
    'ansys':    '!',
}

middle = {
    'abaqus':   '**\n',
    'opensees': '}\n',
    'sofistik': '$',
    'ansys':    '!',
}

dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']
node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def write_input_steps(f, software, structure, steps, loads, displacements, sets, fields, ndof=6):

    """ Writes the Steps information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the .tcl file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        The Structure object to read from.
    steps : dic
        Step objects from structure.steps.
    loads : dic
        Load objects from structure.loads.
    displacements : dic
        Displacement objects from structure.displacements.
    sets : dic
        Sets from strctures.sets.
    fields : list
        Requested fields output.
    ndof : int
        Number of degrees-of-freedom per node.

    Returns
    -------
    None

    """

    c = comments[software]

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Steps\n'.format(c))

    keys = list(structure.steps_order[1:])

    temp = '{0}{1}/'.format(structure.path, structure.name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    for key in keys:

        step = steps[key]
        stype = step.__name__
        step_index = step.index
        factor = step.factor
        increments = step.increments
        tolerance = step.tolerance
        iterations = step.iterations
        method = step.type
        nlgeom = 'YES' if step.nlgeom else 'NO'
        perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''

        headers = {
            'abaqus':   '*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments) +
                        '*{0}\n'.format(method.upper()),
            'opensees': 'timeSeries Constant {0} -factor 1.0\n'.format(step_index) +
                        'pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'),
            'sofistik': '$',
            'ansys':    '!',
        }

        f.write('{0}\n'.format(c))
        f.write('{0} {1}\n'.format(c, key))
        f.write('{0} '.format(c) + '-' * len(key) + '\n')
        f.write('{0}\n'.format(c))
        f.write(headers[software])
        f.write('{0}\n'.format(c))

        # Mechanical

        if stype in ['GeneralStep', 'BucklingStep']:

            # Loads

            try:
                for k in step.loads:

                    load = loads[k]
                    ltype = load.__name__
                    com = load.components
                    # axes = load.axes
                    nset = load.nodes
                    elset = load.elements

                    # Point load

                    if ltype == 'PointLoad':

                        if software == 'opensees':
                            coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])
                            for node in sets[nset]['selection']:
                                f.write('load {0} {1}\n'.format(node + 1, coms))

                        elif software == 'abaqus':
                            f.write('*CLOAD\n')
                            for ci, dof in enumerate(dofs, 1):
                                if com[dof]:
                                    f.write('{0}, {1}, {2}'.format(nset, ci, factor * com[dof]) + '\n')

                        elif software == 'sofistik':
                            pass

                    # Line load

                    elif ltype == 'LineLoad':
                        pass

                        # if axes == 'global':
                        #     raise NotImplementedError

                        # elif axes == 'local':
                        #     elements = ' '.join([str(i + 1) for i in sets[elset]['selection']])
                        #     f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, -com['y'], -com['x']))

                    # Gravity load

                    elif ltype == 'GravityLoad':

                        g = load.g
                        gx = com['x'] if com['x'] else 0
                        gy = com['y'] if com['y'] else 0
                        gz = com['z'] if com['z'] else 0

                        if software == 'opensees':
                            pass

                        elif software == 'sofistik':
                            pass

                        elif software == 'abaqus':
                            f.write('{0}, GRAV, {1}, {2}, {3}, {4}\n'.format(elset, factor * g, gx, gy, gz))

            except:
                pass

            # Displacements

            try:
                for k in step.displacements:

                    displacement = displacements[k]
                    com = displacement.components
                    nset = displacement.nodes

                    f.write('{0}\n'.format(c))
                    f.write('{0} {1}\n'.format(c, k))
                    f.write('{0} '.format(c) + '-' * len(k) + '\n')
                    f.write('{0}\n'.format(c))

                    if software == 'abaqus':

                        f.write('*BOUNDARY\n')
                        f.write('**\n')
                        for ci, dof in enumerate(dofs, 1):
                            if com[dof] is not None:
                                f.write('{0}, {1}, {1}, {2}\n'.format(nset, ci, com[dof] * factor))

                    elif software == 'opensees':
                        pass

                    elif software == 'sofistik':
                        pass
            except:
                pass

        f.write(middle[software])
        f.write('{0}\n'.format(c))

        if software == 'opensees':

            nodal = {}
            elemental = {}
            nodes = '1 {0}'.format(structure.node_count())
            elements = '1 {0}'.format(structure.element_count())

            if 'u' in fields:
                nodal['node_u.out'] = '1 2 3 disp'
            if 'rf' in fields:
                nodal['node_rf.out'] = '1 2 3 reaction'
            if ndof == 6:
                if 'ur' in fields:
                    nodal['node_ur.out'] = '4 5 6 disp'
                if 'rm' in fields:
                    nodal['node_rm.out'] = '4 5 6 reaction'
            if 'sf' in fields:
                elemental['element_sf.out'] = 'basicForces'

            for k, j in nodal.items():
                f.write('recorder Node -file {0}{1}_{2} -time -nodeRange {3} -dof {4}\n'.format(temp, k, key, nodes, j))
            for k, j in elemental.items():
                f.write('recorder Element -file {0}{1}_{2} -time -eleRange {3} {4}\n'.format(temp, k, key, elements, j))

            f.write('#\n')
            f.write('constraints Plain\n')
            f.write('numberer RCM\n')
            f.write('system ProfileSPD\n')
            f.write('test NormUnbalance {0} {1} 5\n'.format(tolerance, iterations))
            f.write('algorithm NewtonLineSearch\n')
            f.write('integrator LoadControl {0}\n'.format(1./increments))
            f.write('analysis Static\n')
            f.write('analyze {0}\n'.format(increments))

        elif software == 'abaqus':

            if isinstance(fields, list):
                fields = structure.fields_dic_from_list(fields)
            # if 'spf' in fields:
                # fields['ctf'] = 'all'
                # del fields['spf']

            f.write('**\n')
            f.write('*OUTPUT, FIELD\n')
            f.write('*NODE OUTPUT\n')
            f.write(', '.join([i.upper() for i in node_fields if i in fields]) + '\n')
            f.write('*ELEMENT OUTPUT\n')
            f.write(', '.join([i.upper() for i in element_fields if (i in fields and i != 'rbfor')]) + '\n')
            if 'rbfor' in fields:
                f.write('*ELEMENT OUTPUT, REBAR\n')
                f.write('RBFOR\n')
            f.write('**\n')
            f.write('*END STEP\n')

        elif software == 'sofistik':
            pass

    f.write('{0}\n'.format(c))
    f.write('{0}\n'.format(c))




#     for key, load in loads.items():

#         if load.__name__ in ['PrestressLoad']:

#             f.write('**\n')
#             f.write('** {0}\n'.format(key))
#             f.write('** ' + '-' * len(key) + '\n')
#             f.write('**\n')

#             com = load.components
#             f.write('*INITIAL CONDITIONS, TYPE=STRESS\n')
#             f.write('{0}, '.format(load.elements))
#             if com['sxx']:
#                 f.write('{0}\n'.format(com['sxx']))




#                 if stype == 'BucklingStep':

#                     modes = step.modes
#                     f.write('{0}, {1}, {2}, {3}\n'.format(modes, modes, 2 * modes, increments))



#                     # Type

#                     if ltype in ['PointLoad', 'TributaryLoad']:
#                         f.write('*CLOAD\n')
#                         f.write('** NSET, dof, CLOAD\n')

#                     if ltype in ['LineLoad', 'AreaLoad', 'GravityLoad', 'BodyLoad']:
#                         f.write('*DLOAD\n')
#                         f.write('** ELSET, component, DLOAD\n')

#                     f.write('**\n')

#                     # Line load

#                     elif ltype == 'LineLoad':

#                         if axes == 'global':
#                             for dof in dofs[:3]:
#                                 if com[dof]:
#                                     f.write('{0}, P{1}, {2}'.format(elset, dof.upper(), lf * com[dof]) + '\n')

#                         elif axes == 'local':
#                             if com['x']:
#                                 f.write('{0}, P1, {1}'.format(elset, lf * com['x']) + '\n')
#                             if com['y']:
#                                 f.write('{0}, P2, {1}'.format(elset, lf * com['y']) + '\n')

#                     # Area load

#                     elif ltype == 'AreaLoad':

#                         if axes == 'global':
#                             raise NotImplementedError

#                         elif axes == 'local':
#                             # x COMPONENT
#                             # y COMPONENT
#                             if com['z']:
#                                 f.write('{0}, P, {1}'.format(elset, lf * com['z']) + '\n')

#                     # Body load

#                     elif ltype == 'BodyLoad':
#                         raise NotImplementedError



#                     # Tributary load

#                     elif ltype == 'TributaryLoad':

#                         for node in sorted(com, key=int):
#                             for c, dof in enumerate(dofs[:3], 1):
#                                 if com[node][dof]:
#                                     ni = node + 1
#                                     dl = com[node][dof] * lf
#                                     f.write('{0}, {1}, {2}\n'.format(ni, c, dl))



#                 # Temperatures

#                 # try:
#                 #     duration = step.duration
#                 # except:
#                 #     duration = 1
#                 #     temperatures = steps[key].temperatures
#                 #     if temperatures:
#                 #         file = misc[temperatures].file
#                 #         einc = str(misc[temperatures].einc)
#                 #         f.write('**\n')
#                 #         f.write('*TEMPERATURE, FILE={0}, BSTEP=1, BINC=1, ESTEP=1, EINC={1}, INTERPOLATE\n'.format(file, einc))



#             # Thermal

#             # elif stype == 'HeatStep':
#             #     temp0 = step.temp0
#             #     duration = step.duration
#             #     deltmx = steps[key].deltmx
#             #     interaction = interactions[step.interaction]
#             #     amplitude = interaction.amplitude
#             #     interface = interaction.interface
#             #     sink_t = interaction.sink_t
#             #     film_c = interaction.film_c
#             #     ambient_t = interaction.ambient_t
#             #     emissivity = interaction.emissivity

#             #     # Initial T

#             #     f.write('*INITIAL CONDITIONS, TYPE=TEMPERATURE\n')
#             #     f.write('NSET_ALL, {0}\n'.format(temp0))
#             #     f.write('**\n')

#             #     # Interface

#             #     f.write('*STEP, NAME={0}, INC={1}\n'.format(sname, increments))
#             #     f.write('*{0}, END=PERIOD, DELTMX={1}\n'.format(method, deltmx))
#             #     f.write('1, {0}, 5.4e-05, {0}\n'.format(duration))
#             #     f.write('**\n')
#             #     f.write('*SFILM, AMPLITUDE={0}\n'.format(amplitude))
#             #     f.write('{0}, F, {1}, {2}\n'.format(interface, sink_t, film_c))
#             #     f.write('**\n')
#             #     f.write('*SRADIATE, AMPLITUDE={0}\n'.format(amplitude))
#             #     f.write('{0}, R, {1}, {2}\n'.format(interface, ambient_t, emissivity))

#             #     # fieldOutputs

#             #     f.write('**\n')
#             #     f.write('** OUTPUT\n')
#             #     f.write('** ------\n')
#             #     f.write('*OUTPUT, FIELD\n')
#             #     f.write('**\n')
#             #     f.write('*NODE OUTPUT\n')
#             #     f.write('NT\n')
#             #     f.write('**\n')
#             #     f.write('*END STEP\n')

#         f.write('**\n')
