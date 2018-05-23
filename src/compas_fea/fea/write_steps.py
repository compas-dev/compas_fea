
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json


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

dofs           = ['x', 'y', 'z', 'xx', 'yy', 'zz']
node_fields    = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']


def _write_point_loads(f, software, com, factor):

    if software == 'abaqus':

        f.write('*CLOAD\n')
        f.write('**\n')

        for node, coms in com.items():
            ni = node + 1
            for ci, value in coms.items():
                index = dofs.index(ci) + 1
                f.write('{0}, {1}, {2}'.format(ni, index, value * factor) + '\n')

    elif software == 'sofistik':

        for node, coms in com.items():
            ni = node + 1
            for ci, value in coms.items():
                if ci in 'xyz':
                    f.write('    NODE NO {0} TYPE P{1}{1} {2}[kN]\n'.format(ni, ci.upper(), value * 0.001))
                else:
                    f.write('    NODE NO {0} TYPE M{1} {2}[kNm]\n'.format(ni, ci.upper(), value * 0.001))

    elif software == 'opensees':

        pass
    elif software == 'ansys':

        pass


def _write_point_load(f, software, com, nodes, ndof, sets, factor):

    if software == 'abaqus':

        f.write('*CLOAD\n')
        f.write('**\n')
        for node in nodes:
            if isinstance(node, str):
                ni = node
            else:
                ni = node + 1
            for ci, dof in enumerate(dofs, 1):
                if com[dof]:
                    f.write('{0}, {1}, {2}'.format(ni, ci, com[dof] * factor) + '\n')
        f.write('**\n')

    elif software == 'sofistik':

        for node in nodes:
            if isinstance(node, str):
                selection = sets[node]['selection']
                for i in selection:
                    ni = i + 1
                    for ci, value in com.items():
                        if value:
                            if ci in 'xyz':
                                f.write('    NODE NO {0} TYPE P{1}{1} {2}\n'.format(ni, ci.upper(), value * 0.001))
                            else:
                                f.write('    NODE NO {0} TYPE M{1} {2}\n'.format(ni, ci.upper(), value * 0.001))
            else:
                pass

    elif software == 'opensees':

        coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])
        for node in nodes:
            if isinstance(node, str):
                selection = sets[node]['selection']
                for i in selection:
                    ni = i + 1
                    f.write('load {0} {1}\n'.format(ni, coms))
            else:
                ni = node + 1
                f.write('load {0} {1}\n'.format(ni, coms))
        f.write('#\n')

    elif software == 'opensees':

        pass


def _write_line_load(f, software, axes, com, factor, elset, sets, structure):

    for k in elset:

        if software == 'abaqus':

            f.write('*DLOAD\n')
            f.write('**\n')

            if axes == 'global':
                for dof in dofs[:3]:
                    if com[dof]:
                        f.write('{0}, P{1}, {2}'.format(k, dof.upper(), factor * com[dof]) + '\n')

            elif axes == 'local':
                if com['x']:
                    f.write('{0}, P1, {1}'.format(k, factor * com['x']) + '\n')
                if com['y']:
                    f.write('{0}, P2, {1}'.format(k, factor * com['y']) + '\n')

        elif software == 'opensees':

            if axes == 'global':
                raise NotImplementedError

            elif axes == 'local':
                elements = ' '.join([str(i + 1) for i in sets[k]['selection']])
                f.write('eleLoad -ele {0} -type -beamUniform {1} {2}\n'.format(elements, -com['y'], -com['x']))

        elif software == 'sofistik':

            for i in sets[k]['selection']:
                ni = structure.sofistik_mapping[i]
                if axes == 'global':
                    if com['x']:
                        f.write('    BEAM {0} TYPE PXX {1}[kN/m]\n'.format(ni, com['x'] * 0.001))
                    if com['y']:
                        f.write('    BEAM {0} TYPE PYY {1}[kN/m]\n'.format(ni, com['y'] * 0.001))
                    if com['z']:
                        f.write('    BEAM {0} TYPE PZZ {1}[kN/m]\n'.format(ni, com['z'] * 0.001))
                elif axes == 'local':
                    if com['z']:
                        f.write('    BEAM {0} TYPE PX {1}[kN/m]\n'.format(ni, com['z'] * 0.001))
                    if com['x']:
                        f.write('    BEAM {0} TYPE PY {1}[kN/m]\n'.format(ni, com['x'] * 0.001))
                    if com['y']:
                        f.write('    BEAM {0} TYPE PZ {1}[kN/m]\n'.format(ni, com['y'] * 0.001))

        elif software == 'ansys':

            pass


def _write_area_load(f, software, com, axes, elset, sets, factor):

    if software == 'opensees':

        pass

    elif software == 'abaqus':

        if axes == 'global':
            raise NotImplementedError

        elif axes == 'local':
            # x COMPONENT
            # y COMPONENT
            f.write('*DLOAD\n')
            f.write('**\n')
            if com['z']:
                f.write('{0}, P, {1}'.format(elset, factor * com['z']) + '\n')

    elif software == 'sofistik':

        components = ''
        for i in 'xyz':
            if com[i]:
                if axes == 'local':
                    components += ' P{0} {1}[kN/m2]'.format(i.upper(), 0.001 * com[i])
                elif axes == 'global':
                    components += ' P{0}{0} {1}[kN/m2]'.format(i.upper(), 0.001 * com[i])
        for k in elset:
            set_index = sets[k]['index'] + 1
            f.write('    QUAD GRP {0} TYPE{1}\n'.format(set_index, components))

    elif software == 'ansys':

        pass


def _write_gravity_load(f, software, g, com, elset, factor):

    gx = com['x'] if com['x'] else 0
    gy = com['y'] if com['y'] else 0
    gz = com['z'] if com['z'] else 0

    if software == 'abaqus':

        for k in elset:
            f.write('*DLOAD\n')
            f.write('**\n')
            f.write('{0}, GRAV, {1}, {2}, {3}, {4}\n'.format(k, g * factor, gx, gy, gz))
            f.write('**\n')

    elif software == 'sofistik':

        pass

    elif software == 'opensees':

        pass

    elif software == 'ansys':

        pass


def _write_displacements(f, software, com, nset, factor, sets, ndof):

    if software == 'abaqus':

        f.write('*BOUNDARY\n')
        f.write('**\n')
        for ci, dof in enumerate(dofs, 1):
            if com[dof] is not None:
                f.write('{0}, {1}, {1}, {2}\n'.format(nset, ci, com[dof] * factor))

    elif software == 'opensees':

        for ci, dof in enumerate(dofs[:ndof], 1):
            if com[dof] is not None:
                for node in sets[nset]['selection']:
                    f.write('sp {0} {1} {2}\n'.format(node + 1, ci, com[dof]))

    elif software == 'sofistik':

        for i in sets[nset]['selection']:
            ni = i + 1
            if com['x'] is not None:
                f.write('    NODE {0} TYPE WXX {1}[mm]\n'.format(ni, com['x'] * 1000))
            if com['y'] is not None:
                f.write('    NODE {0} TYPE WYY {1}[mm]\n'.format(ni, com['y'] * 1000))
            if com['z'] is not None:
                f.write('    NODE {0} TYPE WZZ {1}[mm]\n'.format(ni, com['z'] * 1000))
            if com['xx'] is not None:
                f.write('    NODE {0} TYPE DXX {1}\n'.format(ni, com['xx'] * 1000))
            if com['yy'] is not None:
                f.write('    NODE {0} TYPE DYY {1}\n'.format(ni, com['yy'] * 1000))
            if com['zz'] is not None:
                f.write('    NODE {0} TYPE DZZ {1}\n'.format(ni, com['zz'] * 1000))


def _write_tributary_load(f, software, com, factor):

    if software == 'abaqus':
        f.write('*CLOAD\n')
        f.write('**\n')

    for node in sorted(com, key=int):
        ni = node + 1

        if software == 'abaqus':

            for ci, dof in enumerate(dofs[:3], 1):
                if com[node][dof]:
                    ni = node + 1
                    dl = com[node][dof] * factor
                    f.write('{0}, {1}, {2}\n'.format(ni, ci, dl))

        elif software == 'sofistik':

            f.write('    NODE NO {0} TYPE '.format(ni))
            for ci, dof in enumerate(dofs[:3], 1):
                if com[node][dof]:
                    dl = com[node][dof] / 1000.
                    f.write('P{0}{0}[kN] {1}\n'.format(dof.upper(), dl))

        elif software == 'opensees':

            pass

        elif software == 'ansys':

            pass


def _write_prestress_load(f, software, elset, com):

    for k in elset:

        if software == 'abaqus':

            f.write('*INITIAL CONDITIONS, TYPE=STRESS\n')
            f.write('{0}, '.format(k))
            if com['sxx']:
                f.write('{0}\n'.format(com['sxx']))

        elif software == 'sofistik':

            pass

        elif software == 'opensees':

                pass

        elif software == 'ansys':

            pass


def _write_thermal_load(f, software, elset, temperature, sets, factor):

    for k in elset:

        if software == 'abaqus':

            pass

        elif software == 'sofistik':

            for k in elset:
                set_index = sets[k]['index'] + 1
                f.write('    QUAD GRP {0} TYPE {1} {2}\n'.format(set_index, 'DTXY', temperature))

        elif software == 'opensees':

                pass

        elif software == 'ansys':

            pass


def write_input_steps(f, software, structure, steps, loads, displacements, sets, fields, ndof=6, properties={}):

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
        Sets from structures.sets.
    fields : list
        Requested fields output.
    ndof : int
        Number of degrees-of-freedom per node.
    properties : dic
        ElementProperties objects from structure.element_properties

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

        for k in sorted(loads):

            load = loads[k]
            load_index = load.index + 1
            ltype = load.__name__
            com = getattr(load, 'components', None)
            axes = getattr(load, 'axes', None)
            temperature = getattr(load, 'temperature', None)
            nodes = getattr(load, 'nodes', None)
            elset = getattr(load, 'elements', None)

            if isinstance(nodes, str):
                nodes = [nodes]

            if isinstance(elset, str):
                elset = [elset]

            if ltype != 'GravityLoad':

                f.write('$\n')
                f.write('$ {0}\n'.format(k))
                f.write('$ ' + '-' * len(k) + '\n')
                f.write('$\n')
                f.write("LC {0} TITL '{1}'\n".format(load_index, k))

                if ltype == 'PointLoad':
                    _write_point_load(f, software, com, nodes, ndof, sets, 1)

                elif ltype == 'PointLoads':
                    _write_point_loads(f, software, com, 1)

                elif ltype == 'LineLoad':
                    _write_line_load(f, software, axes, com, 1, elset, sets, structure)

                elif ltype == 'PrestressLoad':
                    _write_prestress_load(f, software, elset, com)

                elif ltype == 'TributaryLoad':
                    _write_tributary_load(f, software, com, 1)

                elif ltype == 'AreaLoad':
                    _write_area_load(f, software, com, axes, elset, sets, 1)

                elif ltype == 'ThermalLoad':
                    _write_thermal_load(f, software, elset, temperature, sets,  1)

                f.write('$\n')

        for k in sorted(displacements):

            bc_disps = steps[structure.steps_order[0]].displacements
            if isinstance(bc_disps, str):
                bc_disps = [bc_disps]

            if k not in bc_disps:

                displacement = displacements[k]
                displacement_index = displacement.index + 1 + len(structure.loads)
                com = displacement.components
                nset = displacement.nodes

                f.write('{0} {1}\n'.format(c, k))
                f.write('{0} '.format(c) + '-' * len(k) + '\n')
                f.write('$\n')
                f.write("LC {0} TITL '{1}'\n".format(displacement_index, k))

                _write_displacements(f, software, com, nset, 1, sets, ndof)

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
        step_index = step.index
        state      = getattr(step, 'state', None)
        factor     = getattr(step, 'factor', 1)
        increments = getattr(step, 'increments', None)
        tolerance  = getattr(step, 'tolerance', None)
        iterations = getattr(step, 'iterations', None)
        method     = getattr(step, 'type', None)
        scopy      = getattr(step, 'step', None)
        modes      = getattr(step, 'modes', None)
        nlgeom = 'YES' if getattr(step, 'nlgeom', None) else 'NO'
        nlmat = 'YES' if getattr(step, 'nlmat', None) else 'NO'

        if isinstance(step.loads, str):
            step.loads = [step.loads]

        # Mechanical

        if stype in ['GeneralStep', 'BucklingStep']:

            if headers[software]:
                f.write(headers[software])

            f.write('{0} {1}\n'.format(c, key))
            f.write('{0} '.format(c) + '-' * len(key) + '\n')
            f.write('{0}\n'.format(c))

            if software == 'abaqus':

                perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''
                f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
                f.write('*{0}\n'.format(method.upper()))
                # f.write(', {0}\n'.format(factor))
                f.write('**\n')

                if stype == 'BucklingStep':
                    f.write('{0}, {1}, {2}, {3}\n'.format(modes, modes, 2 * modes, increments))

                f.write('**\n')

            elif software == 'opensees':

                f.write('timeSeries Constant {0} -factor 1.0\n'.format(step_index))
                f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'))
                f.write('#\n')

            elif software == 'sofistik':

                if stype != 'BucklingStep':
                    f.write("LC 1{0:0>2}00 TITL '{1}' DLZ 0.0\n".format(step_index, key))
                else:
                    scopy_index = steps[scopy].index
                    f.write('HEAD BUCKLING LC {0}\n'.format(scopy))
                    f.write('$\n')
                    f.write('SYST PLC 2{0:0>2}0\n'.format(scopy_index))
                    f.write('EIGE {0} ETYP BUCK LMIN AUTO LC 2{1:0>2}1\n'.format(modes, scopy_index))
                    f.write('$\n')
                    f.write('$\n')
                    f.write('END\n')

            # Loads

            for k in step.loads:

                load = loads[k]
                load_index = load.index + 1
                ltype = load.__name__
                com = getattr(load, 'components', None)
                axes = getattr(load, 'axes', None)
                nodes = getattr(load, 'nodes', None)

                if isinstance(factor, dict):
                    fact = factor.get(k, 1.0)
                else:
                    fact = factor

                if isinstance(nodes, str):
                    nodes = [nodes]

                if isinstance(load.elements, str):
                    elset = [load.elements]
                else:
                    elset = load.elements

                if software != 'sofistik':
                    f.write('{0} {1}\n'.format(c, k))
                    f.write('{0} '.format(c) + '-' * len(k) + '\n')
                    f.write('{0}\n'.format(c))
                else:
                    if ltype != 'GravityLoad':
                        f.write('    LCC {0} FACT {1} $ {2}\n'.format(load_index, fact, k))

                # Point load

                if ltype == 'PointLoad':
                    if software != 'sofistik':
                        _write_point_load(f, software, com, nodes, ndof, sets, fact)

                # Point loads

                elif ltype == 'PointLoads':
                    if software != 'sofistik':
                        _write_point_loads(f, software, com, fact)

                # # Pre-stress

                elif ltype in ['PrestressLoad']:
                    if software != 'sofistik':
                        _write_prestress_load(f, software, elset, com)

                # Line load

                elif ltype == 'LineLoad':
                    if software != 'sofistik':
                        _write_line_load(f, software, axes, com, fact, elset, sets, structure)

                # Area load

                elif ltype == 'AreaLoad':
                    if software != 'sofistik':
                        _write_area_load(f, software, com, axes, elset, sets, fact)

                # Body load

                elif ltype == 'BodyLoad':

                    raise NotImplementedError

                # Gravity load

                elif ltype == 'GravityLoad':
                    if software != 'sofistik':
                        _write_gravity_load(f, software, load.g, com, elset, fact)

                # Tributary load

                elif ltype == 'TributaryLoad':
                    if software != 'sofistik':
                        _write_tributary_load(f, software, com, fact)

            # Displacements

            for k in step.displacements:

                if isinstance(factor, dict):
                    fact = factor.get(k, 1.0)
                else:
                    fact = factor

                displacement = displacements[k]
                displacement_index = displacement.index + 1 + len(structure.loads)
                com = displacement.components
                nset = displacement.nodes

                if software != 'sofistik':
                    f.write('{0} {1}\n'.format(c, k))
                    f.write('{0} '.format(c) + '-' * len(k) + '\n')
                    f.write('{0}\n'.format(c))
                    _write_displacements(f, software, com, nset, fact, sets, ndof)

                else:
                    if stype != 'BucklingStep':
                        f.write('    LCC {0} $ {1}\n'.format(displacement_index, k))

            # Output

            if middle[software]:
                f.write(middle[software])

            if software == 'opensees':

                nodal = {}
                node_range = '1 {0}'.format(structure.node_count())

                if 'u' in fields:
                    nodal['node_u.out'] = '1 2 3 disp'
                if 'rf' in fields:
                    nodal['node_rf.out'] = '1 2 3 reaction'
                if ndof == 6:
                    if 'ur' in fields:
                        nodal['node_ur.out'] = '4 5 6 disp'
                    if 'rm' in fields:
                        nodal['node_rm.out'] = '4 5 6 reaction'

                prefix = 'recorder Node -file {0}{1}_'.format(temp, key)
                for k, j in nodal.items():
                    f.write('{0}{1} -time -nodeRange {2} -dof {3}\n'.format(prefix, k, node_range, j))

                truss_elements = ''
                beam_elements = ''
                spring_elements = ''
                truss_numbers = []
                beam_numbers = []
                spring_numbers = []

                for ekey, element in structure.elements.items():
                    etype = element.__name__

                    if etype in ['TrussElement', 'StrutElement', 'TieElement']:
                        truss_elements += '{0} '.format(ekey + 1)
                        truss_numbers.append(ekey)

                    elif etype in ['BeamElement']:
                        beam_elements += '{0} '.format(ekey + 1)
                        beam_numbers.append(ekey)

                    elif etype in ['SpringElement']:
                        spring_elements += '{0} '.format(ekey + 1)
                        spring_numbers.append(ekey)

                prefix = 'recorder Element -file {0}{1}_'.format(temp, key)

                if 'sf' in fields:

                    if truss_elements:
                        k = 'element_truss_sf.out'
                        j = 'axialForce'
                        f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, k, truss_elements, j))

                    if beam_elements:
                        k = 'element_beam_sf.out'
                        j = 'force'
                        f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, k, beam_elements, j))

                if 'spf' in fields:

                    if spring_elements:
                        k = 'element_spring_sf.out'
                        j = 'basicForces'
                        f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, k, spring_elements, j))

                with open('{0}truss_numbers.json'.format(temp), 'w') as fo:
                    json.dump({'truss_numbers': truss_numbers}, fo)

                with open('{0}beam_numbers.json'.format(temp), 'w') as fo:
                    json.dump({'beam_numbers': beam_numbers}, fo)

                with open('{0}spring_numbers.json'.format(temp), 'w') as fo:
                    json.dump({'spring_numbers': spring_numbers}, fo)

                f.write('#\n')
                # f.write('constraints Plain\n')
                f.write('constraints Transformation\n')
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

            elif software == 'ansys':

                pass

        f.write('{0}\n'.format(c))
        f.write('{0}\n'.format(c))

        if footers[software]:
            f.write(footers[software])

        if software == 'sofistik':

            if stype != 'BucklingStep':

                is_rebar = False
                for property in properties.values():
                    if property.reinforcement:
                        is_rebar = True

                if is_rebar:

                    f.write('+PROG BEMESS\n')
                    f.write("HEAD REBAR {0} LC 1{1:0>2}00\n".format(state.upper(), step_index))
                    f.write('$\n')
                    f.write('CTRL WARN 471 $ Element thickness too thin and not allowed for a design.\n')
                    # f.write('CTRL WARN 496 $ Possible non-constant longitudinal reinforcement.\n')
                    # f.write('CTRL WARN 254 $ Vertical shear reinforcement not allowed for slab thickness smaller 20 cm.\n')
                    f.write('CTRL PFAI 2\n')
                    if state == 'sls':
                        # f.write('CTRL SERV GALF 1.45\n')
                        f.write('CTRL SLS\n')
                        f.write('CRAC WK PARA\n')
                    else:
                        f.write('CTRL ULTI\n')
                    f.write('CTRL LCR {0}\n'.format(step_index))
                    f.write('LC 1{0:0>2}00\n'.format(step_index))  # can put many LC here LC301,302 etc
                    f.write('$\n')
                    f.write('$\n')
                    f.write('END\n')
                    f.write('$\n')
                    f.write('$\n')

                    # if state == 'uls':

                    #     f.write('+PROG BEMESS\n')
                    #     f.write("HEAD REBAR {0} LC 1{1:0>2}0 COMBINED\n".format(state.upper(), step_index))
                    #     f.write('$\n')
                    #     f.write('CTRL WARN 471 $ Element thickness too thin and not allowed for a design.\n')
                    #     f.write('CTRL PFAI 2\n')
                    #     f.write('CTRL LCRI {0}\n'.format(step_index))
                    #     f.write('CTRL LCR 1{0:0>2}\n'.format(step_index))
                    #     f.write('$\n')
                    #     f.write('$\n')
                    #     f.write('END\n')
                    #     f.write('$\n')
                    #     f.write('$\n')

                f.write('+PROG ASE\n')
                f.write("HEAD SOLVE {0} LC 2{1:0>2}00 {2}\n".format(state.upper(), step_index, key))
                f.write('$\n')
                f.write('CTRL SOLV 1\n')
                f.write('CTRL CONC\n')

                if state == 'sls':
                    pass
                    # f.write('NSTR KMOD S1 KSV SLD\n')
                elif state == 'uls':
                    # f.write('NSTR KMOD S1 KSV ULD\n')
                    f.write('ULTI 30 FAK1 0.1 DFAK 0.1 PRO 1.5 FAKE 1.5\n')
                if nlgeom == 'YES':
                    f.write('SYST PROB TH3 ITER {0} TOL {1} NMAT {2}\n'.format(increments, tolerance, nlmat))
                    # f.write('SYST PROB TH3 ITER {0} TOL {1} NMAT {2} PLC 1{3:0>2}00\n'.format(increments, tolerance, nlmat, step_index))

                # if state == 'uls':
                    # f.write('REIQ LCR 1{0:0>2}\n'.format(step_index))
                # else:
                    # f.write('REIQ LCR {0}\n'.format(step_index))

                f.write('REIQ LCR {0}\n'.format(step_index))
                f.write('$\n')

                DLX, DLY, DLZ = 0, 0, 0
                for load in loads.values():
                    if load.__name__ == 'GravityLoad':
                        com = load.components
                        DLX = com['x'] if com['x'] else 0
                        DLY = com['y'] if com['y'] else 0
                        DLZ = com['z'] if com['z'] else 0
                        break

                if isinstance(factor, dict):
                    fact = factor.get('g', 1.0)
                else:
                    fact = factor

                f.write('$\n')
                f.write("LC 2{0:0>2}00 TITL '{1}'".format(step_index, key))
                f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX * fact, DLY * fact, DLZ * fact))
                f.write('    LCC 1{0:0>2}00\n'.format(step_index))

                f.write('$\n')
                f.write('END\n')
                f.write('$\n')
                f.write('$\n')

                f.write('+PROG ASE\n')
                f.write("HEAD CREEP {0} LC 3{1:0>2}00 {2}\n".format(state.upper(), step_index, key))
                f.write('$\n')
                f.write('CTRL SOLV 1\n')
                f.write('CTRL CONC\n')
                f.write('CREP NCRE 10\n')

                if nlgeom == 'YES':
                    f.write('SYST PROB TH3 ITER {0} TOL {1} NMAT {2} PLC 2{3:0>2}00\n'.format(increments, tolerance, nlmat, step_index))
                f.write('GRP ALL FACS 1.00 PHI 1.00 PHIF 0 EPS -0.0005\n')

                f.write('REIQ LCR {0}\n'.format(step_index))
                f.write('$\n')

                DLX, DLY, DLZ = 0, 0, 0
                for load in loads.values():
                    if load.__name__ == 'GravityLoad':
                        com = load.components
                        DLX = com['x'] if com['x'] else 0
                        DLY = com['y'] if com['y'] else 0
                        DLZ = com['z'] if com['z'] else 0
                        break

                f.write('$\n')
                f.write("LC 3{0:0>2}00 TITL '{1} CREEP'".format(step_index, key))
                f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX * fact, DLY * fact, DLZ * fact))
                f.write('    LCC 2{0:0>2}00 PLC YES\n'.format(step_index))

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
