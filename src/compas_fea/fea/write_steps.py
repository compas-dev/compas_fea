
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
    'sofistik': '+PROG ASE\n$\n',
    'ansys':    '',
}

footers = {
    'abaqus':   '',
    'opensees': '',
    'sofistik': 'END\n$\n$\n',
    'ansys':    '',
}

dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']
node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def write_input_steps(f, software, structure, steps, loads, displacements, sets, fields, ndof=6, properties={},
                      sections={}):

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
    properties : dic
        ElementProperties objects from structure.element_properties
    sections : dic
        Section objects from structure.sections.

    Returns
    -------
    None

    """

    c = comments[software]

    if software == 'sofistik':

        f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
        f.write('{0} ----------------------------------------------------------------------- Loads\n'.format(c))
        f.write('$\n')
        f.write('+PROG SOFILOAD\n')

        if isinstance(loads, str):
            loads = [loads]

        for k in sorted(loads):

            load = loads[k]
            load_index = load.index + 1
            axes = load.axes
            ltype = load.__name__
            com = load.components

            if ltype != 'GravityLoad':

                f.write('$\n')
                f.write('$ {0}\n'.format(k))
                f.write('$ ' + '-' * len(k) + '\n')
                f.write('$\n')
                f.write("LC {0} TITL '{1}'\n".format(load_index, k))

                if ltype in ['PointLoad', 'PointLoads']:

                    if ltype == 'PointLoad':

                        if isinstance(load.nodes, str):
                            nodes = sets[load.nodes]['selection']
                        elif isinstance(load.nodes, list):
                            nodes = load.nodes

                        pass
                        # for node in sorted(nodes, key=int):
                            # ni = node + 1
                            # f.write('    NODE NO {0} TYPE PX\n'.format(ni))
                        # for ci, dof in enumerate(dofs[:3], 1):
                            # if com[node][dof]:
                                # dl = com[node][dof] / 1000.
                                # f.write('P{0}{0} {1}\n'.format(dof.upper(), dl))

                    elif ltype == 'PointLoads':

                        for node, coms in com.items():
                            ni = node + 1
                            for ci, value in coms.items():
                                if ci in 'xyz':
                                    f.write('    NODE NO {0} TYPE P{1}{1} {2}\n'.format(ni, ci.upper(), value * 0.001))
                                else:
                                    f.write('    NODE NO {0} TYPE M{1} {2}\n'.format(ni, ci.upper(), value * 0.001))

                else:

                    elset = load.elements
                    set_index = sets[elset]['index'] + 1

                    if ltype == 'TributaryLoad':

                        for node in sorted(com, key=int):
                            ni = node + 1
                            f.write('    NODE NO {0} TYPE '.format(ni))
                            for ci, dof in enumerate(dofs[:3], 1):
                                if com[node][dof]:
                                    dl = com[node][dof] / 1000.
                                    f.write('P{0}{0} {1}\n'.format(dof.upper(), dl))

                    elif ltype == 'AreaLoad':

                        components = ''
                        for i in 'xyz':
                            if com[i]:
                                if axes == 'local':
                                    components += ' P{0} {1}'.format(i.upper(), 0.001 * com[i])
                                elif axes == 'global':
                                    components += ' P{0}{0} {1}'.format(i.upper(), 0.001 * com[i])
                        f.write('    QUAD GRP {0} TYPE{1}\n'.format(set_index, components))

        f.write('$\n')
        f.write('END\n')
        f.write('$\n')
        f.write('$\n')

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Steps\n'.format(c))
    f.write('{0}\n'.format(c))

    keys = list(structure.steps_order[1:])

    temp = '{0}{1}/'.format(structure.path, structure.name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    for key in keys:

        step       = steps[key]
        stype      = step.__name__
        state      = getattr(step, 'state', None)
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

            if headers[software]:
                f.write(headers[software])

            f.write('{0} {1}\n'.format(c, key))
            f.write('{0} '.format(c) + '-' * len(key) + '\n')
            f.write('{0}\n'.format(c))

            if software == 'abaqus':

                f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
                f.write('*{0}\n'.format(method.upper()))

                if stype == 'BucklingStep':
                    modes = step.modes
                    f.write('{0}, {1}, {2}, {3}\n'.format(modes, modes, 2 * modes, increments))

                f.write('**\n')

            elif software == 'opensees':

                f.write('timeSeries Constant {0} -factor 1.0\n'.format(step_index))
                f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'))
                f.write('#\n')

            elif software == 'sofistik':

                f.write("LC 1{0:0>2} TITL '{1}' FACT {2} DLZ 0.0\n".format(step_index, key, factor))

            # Loads

            if isinstance(step.loads, str):
                step.loads = [step.loads]

            for k in step.loads:

                load = loads[k]
                load_index = load.index + 1
                ltype = load.__name__
                com = load.components
                # axes = load.axes
                nset = load.nodes
                elset = load.elements

                if software != 'sofistik':
                    f.write('{0} {1}\n'.format(c, k))
                    f.write('{0} '.format(c) + '-' * len(k) + '\n')
                    f.write('{0}\n'.format(c))
                else:
                    if ltype != 'GravityLoad':
                        f.write('    LCC {0} $ {1}\n'.format(load_index, k))

                # Point load

                if ltype == 'PointLoad':

                    if software == 'opensees':

                        coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])
                        for node in sets[nset]['selection']:
                            f.write('load {0} {1}\n'.format(node + 1, coms))
                            f.write('#\n')

                    elif software == 'abaqus':

                        f.write('*CLOAD\n')
                        f.write('**\n')
                        for ci, dof in enumerate(dofs, 1):
                            if com[dof]:
                                f.write('{0}, {1}, {2}'.format(nset, ci, factor * com[dof]) + '\n')
                        f.write('**\n')

                # Pre-stress

                elif ltype in ['PrestressLoad']:

                    f.write('*INITIAL CONDITIONS, TYPE=STRESS\n')
                    f.write('{0}, '.format(elset))
                    if com['sxx']:
                        f.write('{0}\n'.format(com['sxx']))

                # Line load

                elif ltype == 'LineLoad':

                    if software == 'opensees':

                        pass

                        # if axes == 'global':
                        #     raise NotImplementedError

                        # elif axes == 'local':
                        #     elements = ' '.join([str(i + 1) for i in sets[elset]['selection']])
                        #     f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, -com['y'], -com['x']))

                    elif software == 'abaqus':

                        if axes == 'global':
                            for dof in dofs[:3]:
                                if com[dof]:
                                    f.write('{0}, P{1}, {2}'.format(elset, dof.upper(), factor * com[dof]) + '\n')

                        elif axes == 'local':
                            if com['x']:
                                f.write('{0}, P1, {1}'.format(elset, factor * com['x']) + '\n')
                            if com['y']:
                                f.write('{0}, P2, {1}'.format(elset, factor * com['y']) + '\n')

                # Area load

                elif ltype == 'AreaLoad':

                    if software == 'opensees':

                        pass

                    elif software == 'abaqus':  # only based on normal so far

                        # if axes == 'global':
                        #     raise NotImplementedError

                        # elif axes == 'local':
                        # x COMPONENT
                        # y COMPONENT
                        f.write('*DLOAD\n')
                        f.write('**\n')
                        if com['z']:
                            f.write('{0}, P, {1}'.format(elset, factor * com['z']) + '\n')

                # Body load

                elif ltype == 'BodyLoad':

                    raise NotImplementedError

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

            # Displacements

            for k in step.displacements:

                displacement = displacements[k]
                com = displacement.components
                nset = displacement.nodes
                nnodes = sorted(structure.sets[nset]['selection'], key=int)

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

                    # for ci, dof in enumerate(dofs[:ndof], 1):
                    #     if com[dof] is not None:
                    #         for node in nnodes:
                    #             f.write('sp {0} {1} {2}\n'.format(node + 1, ci, com[dof]))
                    pass

                elif software == 'sofistik':

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
                if 'spf' in fields:
                    elemental['element_spf.out'] = 'basicForces'

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
                if 'spf' in fields:
                    fields['ctf'] = 'all'
                    del fields['spf']

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

        f.write('{0}\n'.format(c))
        f.write('{0}\n'.format(c))

        if footers[software]:
            f.write(footers[software])

        has_rebar = False
        for kk in sorted(properties):
            property = properties[kk]
            if property.reinforcement:
                has_rebar = True

        if has_rebar:
            if software == 'sofistik':

                f.write('+PROG BEMESS\n')
                f.write('HEAD {0}\n'.format(state.upper()))
                f.write('$\n')
                f.write('CTRL WARN 471 $ Element thickness too thin and not allowed for a design.\n')
                f.write('CTRL WARN 496 $ Possible non-constant longitudinal reinforcement.\n')
                f.write('CTRL WARN 254 $ Vertical shear reinforcement not allowed for slab thickness smaller 20 cm.\n')
                f.write('CTRL PFAI 2\n')
                if state == 'sls':
                    f.write('CTRL SLS\n')
                    f.write('CRAC WK PARA\n')
                else:
                    f.write('CTRL ULTI\n')
                f.write('CTRL LCR {0}\n'.format(step_index))
                f.write('LC 1{0:0>2}\n'.format(step_index))

                f.write('$\n')
                f.write('$\n')
                f.write('END\n')
                f.write('$\n')
                f.write('$\n')

                f.write('+PROG ASE\n')
                f.write('$\n')
                f.write('CTRL SOLV 1\n')
                f.write('CTRL CONC\n')
                f.write('$CREP NCRE 20\n')

                if state == 'sls':
                    f.write('NSTR KMOD S1 KSV SLD\n')
                elif state == 'uls':
                    f.write('NSTR KMOD S1 KSV ULD\n')
                if nlgeom == 'YES':
                    f.write('$\n')
                    f.write('SYST PROB TH3 ITER {0} TOL {1} NMAT YES\n'.format(increments, tolerance))

                f.write('REIQ LCR {0}\n'.format(step_index))
                f.write('$\n')

                f.write("LC 2{0:0>2} TITL '{1}'".format(step_index, key))
                DLX, DLY, DLZ = 0, 0, 0
                for key, load in loads.items():
                    if load.__name__ in ['GravityLoad']:
                        com = load.components
                        gx = com['x'] if com['x'] else 0
                        gy = com['y'] if com['y'] else 0
                        gz = com['z'] if com['z'] else 0
                        DLX = gx
                        DLY = gy
                        DLZ = gz
                f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX * factor, DLY * factor, DLZ * factor))
                f.write('    LCC 1{0:0>2}\n'.format(step_index))

                f.write('$\n')
                f.write('$\n')
                f.write('END\n')
                f.write('$\n')
                f.write('$\n')


# Thermal

# try:
#     duration = step.duration
# except:
#     duration = 1
#     temperatures = steps[key].temperatures
#     if temperatures:
#         file = misc[temperatures].file
#         einc = str(misc[temperatures].einc)
#         f.write('**\n')
#         f.write('*TEMPERATURE, FILE={0}, BSTEP=1, BINC=1, ESTEP=1, EINC={1}, INTERPOLATE\n'.format(file, einc))

# elif stype == 'HeatStep':

#     temp0 = step.temp0
#     duration = step.duration
#     deltmx = steps[key].deltmx
#     interaction = interactions[step.interaction]
#     amplitude = interaction.amplitude
#     interface = interaction.interface
#     sink_t = interaction.sink_t
#     film_c = interaction.film_c
#     ambient_t = interaction.ambient_t
#     emissivity = interaction.emissivity

#     # Initial T

#     f.write('*INITIAL CONDITIONS, TYPE=TEMPERATURE\n')
#     f.write('NSET_ALL, {0}\n'.format(temp0))
#     f.write('**\n')

#     # Interface

#     f.write('*STEP, NAME={0}, INC={1}\n'.format(sname, increments))
#     f.write('*{0}, END=PERIOD, DELTMX={1}\n'.format(method, deltmx))
#     f.write('1, {0}, 5.4e-05, {0}\n'.format(duration))
#     f.write('**\n')
#     f.write('*SFILM, AMPLITUDE={0}\n'.format(amplitude))
#     f.write('{0}, F, {1}, {2}\n'.format(interface, sink_t, film_c))
#     f.write('**\n')
#     f.write('*SRADIATE, AMPLITUDE={0}\n'.format(amplitude))
#     f.write('{0}, R, {1}, {2}\n'.format(interface, ambient_t, emissivity))

#     # fieldOutputs

#     f.write('**\n')
#     f.write('** OUTPUT\n')
#     f.write('** ------\n')
#     f.write('*OUTPUT, FIELD\n')
#     f.write('**\n')
#     f.write('*NODE OUTPUT\n')
#     f.write('NT\n')
#     f.write('**\n')
#     f.write('*END STEP\n')
