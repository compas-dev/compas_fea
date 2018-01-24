
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
    'abaqus':   '',
    'opensees': '}\n',
    'sofistik': '',
    'ansys':    '',
}

headers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': '+PROG ASE\n',
    'ansys':    '',
}

footers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': 'END\n',
    'ansys':    '',
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

    if software == 'sofistik':

        f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
        f.write('{0} ----------------------------------------------------------------------- Loads\n'.format(c))
        f.write('+PROG SOFILOAD\n')

        for k in loads:

            load = loads[k]
            load_index = load.index + 1
            ltype = load.__name__
            com = load.components

            if ltype != 'GravityLoad':

                f.write('$\n')
                f.write('$ {0}\n'.format(k))
                f.write('$ ' + '-' * len(k) + '\n')
                f.write('$\n')
                f.write("LC {0} TITL '{1}'\n".format(load_index, k))
                f.write('$\n')

                if ltype == 'TributaryLoad':

                    for node in sorted(com, key=int):
                        ni = node + 1
                        f.write('    NODE NO {0} TYPE '.format(ni))
                        for ci, dof in enumerate(dofs[:3], 1):
                            if com[node][dof]:
                                dl = com[node][dof] / 1000.
                                f.write('P{0}{0} {1}\n'.format(dof.upper(), dl))

                # f.write('\n')
                # components = ''
                # if com['x']:
                #     pass
                # if com['y']:
                #     pass
                # if com['z']:
                #     components += ' PZZ {0}'.format(0.001 * com['z'] * lf)
                # f.write('    QUAD GRP {0}{1}\n'.format(set_index, components))

        f.write('$\n')
        f.write('END\n')
        f.write('$\n')
        f.write('$\n')

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Steps\n'.format(c))

    if headers[software]:
        f.write(headers[software])

    keys = list(structure.steps_order[1:])

    temp = '{0}{1}/'.format(structure.path, structure.name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    for key in keys:

        step       = steps[key]
        stype      = step.__name__
        step_index = step.index
        factor     = getattr(step, 'factor', None)
        increments = getattr(step, 'increments', None)
        tolerance  = getattr(step, 'tolerance', None)
        iterations = getattr(step, 'iterations', None)
        method     = getattr(step, 'type', None)
        nlgeom     = 'YES' if getattr(step, 'nlgeom', None) else 'NO'
        perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''

        # Mechanical

        if (stype in ['GeneralStep', 'BucklingStep']) and (stype != 'DesignStep'):

            f.write('{0}\n'.format(c))
            f.write('{0} {1}\n'.format(c, key))
            f.write('{0} '.format(c) + '-' * len(key) + '\n')
            f.write('{0}\n'.format(c))

            if software == 'abaqus':

                f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
                f.write('*{0}\n'.format(method.upper()))

            elif software == 'opensees':

                f.write('timeSeries Constant {0} -factor 1.0\n'.format(step_index))
                f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'))

            elif software == 'sofistik':

                f.write('CTRL SOLV 1\n')
                f.write('CTRL CONC\n')
                if nlgeom == 'YES':
                    f.write('SYST PROB TH2 ITER {0} TOL {1} NMAT YES\n'.format(increments, tolerance))
                f.write('$\n')
                f.write("LC 10{0} TITL '{1}' FACT {2}".format(step_index, key, factor))

                DLX, DLY, DLZ = 0, 0, 0
                for key, load in loads.items():
                    if load.__name__ in ['GravityLoad']:
                        com = load.components
                        gx = com['x'] if com['x'] else 0
                        gy = com['y'] if com['y'] else 0
                        gz = com['z'] if com['z'] else 0
                        DLX += gx
                        DLY += gy
                        DLZ += gz
                f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX * factor, DLY * factor, DLZ * factor))

            # Loads

            try:
                for k in step.loads:

                    load = loads[k]
                    load_index = load.index + 1
                    ltype = load.__name__
                    com = load.components
                    # axes = load.axes
                    nset = load.nodes
                    elset = load.elements

                    if software != 'sofistik':
                        f.write('{0}\n'.format(c))
                        f.write('{0} {1}\n'.format(c, k))
                        f.write('{0} '.format(c) + '-' * len(k) + '\n')
                        f.write('{0}\n'.format(c))
                    else:
                        if ltype != 'GravityLoad':
                            f.write('    LCC {0}\n'.format(load_index))

                    # Point load

                    if ltype == 'PointLoad':

                        if software == 'opensees':
                            f.write('#\n')
                            coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])
                            for node in sets[nset]['selection']:
                                f.write('load {0} {1}\n'.format(node + 1, coms))

                        elif software == 'abaqus':
                            f.write('*CLOAD\n')
                            f.write('**\n')
                            for ci, dof in enumerate(dofs, 1):
                                if com[dof]:
                                    f.write('{0}, {1}, {2}'.format(nset, ci, factor * com[dof]) + '\n')
                            f.write('**\n')

                    # Line load

                    elif ltype == 'LineLoad':
                        pass

                        # if axes == 'global':
                        #     raise NotImplementedError

                        # elif axes == 'local':
                        #     elements = ' '.join([str(i + 1) for i in sets[elset]['selection']])
                        #     f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, -com['y'], -com['x']))

                    elif ltype == 'AreaLoad':

                        if software == 'opensees':

                            pass

                        elif software == 'abaqus':

                            pass

                    # Gravity load

                    elif ltype == 'GravityLoad':

                        g = load.g
                        gx = com['x'] if com['x'] else 0
                        gy = com['y'] if com['y'] else 0
                        gz = com['z'] if com['z'] else 0

                        if software == 'opensees':
                            pass

                        elif software == 'abaqus':
                            f.write('*DLOAD\n')
                            f.write('**\n')
                            f.write('{0}, GRAV, {1}, {2}, {3}, {4}\n'.format(elset, factor * g, gx, gy, gz))
                            f.write('**\n')

                    # Tributary load

                    elif ltype == 'TributaryLoad':

                        if software == 'opensees':

                            pass

                        elif software == 'abaqus':

                            f.write('*CLOAD\n')
                            f.write('**\n')
                            for node in sorted(com, key=int):
                                for ci, dof in enumerate(dofs[:3], 1):
                                    if com[node][dof]:
                                        ni = node + 1
                                        dl = com[node][dof] * factor
                                        f.write('{0}, {1}, {2}\n'.format(ni, ci, dl))

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

            if middle[software]:
                f.write(middle[software])

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
                    f.write('recorder Node -file {0}{1}_{2} -time -nodeRange {3} -dof {4}\n'.format(temp, key, k, nodes, j))
                for k, j in elemental.items():
                    f.write('recorder Element -file {0}{1}_{2} -time -eleRange {3} {4}\n'.format(temp, key, k, elements, j))

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
                f.write('**\n')
                f.write('*NODE OUTPUT\n')
                f.write('**\n')
                f.write(', '.join([i.upper() for i in node_fields if i in fields]) + '\n')
                f.write('**\n')
                f.write('*ELEMENT OUTPUT\n')
                f.write('**\n')
                f.write(', '.join([i.upper() for i in element_fields if (i in fields and i != 'rbfor')]) + '\n')
                if 'rbfor' in fields:
                    f.write('*ELEMENT OUTPUT, REBAR\n')
                    f.write('RBFOR\n')
                f.write('**\n')
                f.write('*END STEP\n')

            elif software == 'sofistik':
                pass

    if footers[software]:
        f.write(footers[software])

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



# CTRL ITER V4 10
# CTRL CONC V4
# SYST PROB TH3 ITER 200 TOL 0.010 FMAX 1.1 NMAT YES
# REIQ LCR 4

# $ conventional steel reinforcement
# $ --------------------------------

# SREC 1 B 50[mm] H 149[mm] HO 1[mm] BO 50[mm] MNO 1 MRF 2 ASO 0.4[cm2] ASU 0.4[cm2]
# STEE 5 B 500A

# angle = rebar['angle'] 2nd layer is assumed 90 deg by default.
