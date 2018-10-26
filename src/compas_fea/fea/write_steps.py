
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

dofs = ['x', 'y', 'z', 'xx', 'yy', 'zz']


def write_input_steps(f, software, structure, steps, loads, displacements, sets, fields, ndof=6, properties={}):

    """ Writes the Steps information to the input file.

    Parameters
    ----------
    f : obj
        The open file object for the input file.
    software : str
        Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
    structure : obj
        The Structure object to read from.
    steps : dict
        Step objects from structure.steps.
    loads : dict
        Load objects from structure.loads.
    displacements : dict
        Displacement objects from structure.displacements.
    sets : dict
        Sets from structures.sets.
    fields : list
        Requested fields output.
    ndof : int
        Number of degrees-of-freedom per node (for OpenSees).
    properties : dict
        ElementProperties objects from structure.element_properties

    Returns
    -------
    None

    """

    c = comments[software]

    if software == 'sofistik':

        _write_sofistik_loads_displacements(f, sets, displacements, loads, steps, structure)

        f.write('END\n')
        f.write('$\n')
        f.write('$\n')

    f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
    f.write('{0} ----------------------------------------------------------------------- Steps\n'.format(c))
    f.write('{0}\n'.format(c))

    # Check temp folder

    temp = '{0}{1}/'.format(structure.path, structure.name)
    try:
        os.stat(temp)
    except:
        os.mkdir(temp)

    # Loop steps

    for key in structure.steps_order[1:]:

        step       = steps[key]
        stype      = step.__name__
        step_index = step.index
        state      = getattr(step, 'state', None)
        factor     = getattr(step, 'factor', 1)
        increments = getattr(step, 'increments', 100)
        tolerance  = getattr(step, 'tolerance', None)
        iterations = getattr(step, 'iterations', None)
        method     = getattr(step, 'type')
        # scopy      = getattr(step, 'step', None)
        modes      = getattr(step, 'modes', None)
        nlgeom = 'YES' if getattr(step, 'nlgeom', None) else 'NO'
        nlmat  = 'YES' if getattr(step, 'nlmat', None) else 'NO'


        # Write heading

        if stype in ['GeneralStep', 'BucklingStep', 'ModalStep']:

            f.write('{0} {1}\n'.format(c, key))
            f.write('{0} '.format(c) + '-' * len(key) + '\n')
            f.write('{0}\n'.format(c))

            if software == 'abaqus':

                if stype == 'ModalStep':

                    f.write('*STEP, NAME={0}\n'.format(key))
                    f.write('*FREQUENCY, EIGENSOLVER=LANCZOS, NORMALIZATION=DISPLACEMENT\n')
                    f.write('{0}\n'.format(modes))

                else:

                    perturbation = ', PERTURBATION' if stype == 'BucklingStep' else ''
                    f.write('*STEP, NLGEOM={0}, NAME={1}{2}, INC={3}\n'.format(nlgeom, key, perturbation, increments))
                    f.write('*{0}\n'.format(method.upper()))
                    f.write('**\n')

                    if stype == 'BucklingStep':
                        f.write('{0}, {1}, {2}, {3}\n'.format(modes, modes, 2 * modes, increments))

                f.write('**\n')

            elif software == 'opensees':

                f.write('timeSeries Constant {0} -factor 1.0\n'.format(step_index))
                f.write('pattern Plain {0} {0} -fact {1} {2}\n'.format(step_index, factor, '{'))
                f.write('#\n')

            elif software == 'sofistik':

                f.write('+PROG ASE\n')
                f.write('$\n')

                if stype != 'BucklingStep':
                    f.write("LC 1{0:0>2}00 TITL '{1}' DLZ 0.0\n".format(step_index, key))

                else:
                    pass
                    # scopy_index = steps[scopy].index
                    # f.write('HEAD BUCKLING LC {0}\n'.format(scopy))
                    # f.write('$\n')
                    # f.write('SYST PLC 2{0:0>2}00\n'.format(scopy_index))
                    # f.write('EIGE {0} ETYP BUCK LMIN AUTO LC 2{1:0>2}01\n'.format(modes, scopy_index))
                    # f.write('$\n')
                    # f.write('$\n')
                    # f.write('END\n')

            elif software == 'ansys':

                pass


            # Write loads

            if getattr(step, 'loads', None):

                if isinstance(step.loads, str):
                    step.loads = [step.loads]

                for k in step.loads:

                    load  = loads[k]
                    ltype = load.__name__
                    com   = getattr(load, 'components', None)
                    axes  = getattr(load, 'axes', None)
                    nodes = getattr(load, 'nodes', None)
                    fact  = factor.get(k, 1.0) if isinstance(factor, dict) else factor

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

                        # Point load

                        if ltype == 'PointLoad':
                            _write_point_load(f, software, com, nodes, ndof, sets, fact)

                        # Point loads

                        elif ltype == 'PointLoads':
                            _write_point_loads(f, software, com, fact)

                        # Pre-stress

                        elif ltype in ['PrestressLoad']:
                            _write_prestress_load(f, software, elset, com)

                        # Line load

                        elif ltype == 'LineLoad':
                            _write_line_load(f, software, axes, com, fact, elset, sets, structure)

                        # Area load

                        elif ltype == 'AreaLoad':
                            _write_area_load(f, software, com, axes, elset, sets, fact)

                        # Body load

                        elif ltype == 'BodyLoad':

                            raise NotImplementedError

                        # Gravity load

                        elif ltype == 'GravityLoad':
                            _write_gravity_load(f, software, load.g, com, elset, fact)

                        # Tributary load

                        elif ltype == 'TributaryLoad':
                            _write_tributary_load(f, software, com, fact)

                    else:

                        if ltype != 'GravityLoad':
                            f.write('    LCC {0} FACT {1} $ {2}\n'.format(load.index + 1, fact, k))


            # Write displacements

            for k in step.displacements:

                displacement = displacements[k]
                displacement_index = displacement.index + 1 + len(loads)
                com   = displacement.components
                nodes = displacement.nodes
                fact  = factor.get(k, 1.0) if isinstance(factor, dict) else factor

                if software != 'sofistik':

                    f.write('{0} {1}\n'.format(c, k))
                    f.write('{0} '.format(c) + '-' * len(k) + '\n')
                    f.write('{0}\n'.format(c))

                    _write_displacements(f, software, com, nodes, fact, sets, ndof)

                else:

                    if stype != 'BucklingStep':
                        f.write('    LCC {0} $ {1}\n'.format(displacement_index, k))


        # Output requests

        if software == 'abaqus':

            _write_abaqus_output(f, fields, structure)

        elif software == 'sofistik':

            _write_sofistik_output(f, stype, properties, state, step_index, key, nlgeom, increments, tolerance, nlmat,
                                   loads, factor, structure.materials)

        elif software == 'opensees':

            _write_opensees_output(f, fields, ndof, temp, key, structure, tolerance, iterations, increments)

        elif software == 'ansys':

            pass

        f.write('{0}\n'.format(c))
        f.write('{0}\n'.format(c))


def _write_point_loads(f, software, com, factor):

    if software == 'abaqus':

        f.write('*CLOAD\n')
        f.write('**\n')

        for node, coms in com.items():
            for ci, value in coms.items():
                index = dofs.index(ci) + 1
                f.write('{0}, {1}, {2}'.format(node + 1, index, value * factor) + '\n')

    elif software == 'sofistik':

        for node, coms in com.items():
            for ci, value in coms.items():
                if ci in 'xyz':
                    f.write('    NODE NO {0} TYPE P{1}{1} {2}[kN]\n'.format(node + 1, ci.upper(), value * 0.001))
                else:
                    f.write('    NODE NO {0} TYPE M{1} {2}[kNm]\n'.format(node + 1, ci.upper(), value * 0.001))

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
                for i in sets[node]['selection']:
                    ni = i + 1
                    for ci, value in com.items():
                        if value:
                            if ci in 'xyz':
                                f.write('    NODE NO {0} TYPE P{1}{1} {2}[kN]\n'.format(ni, ci.upper(), value * 0.001))
                            else:
                                f.write('    NODE NO {0} TYPE M{1} {2}[kN]\n'.format(ni, ci.upper(), value * 0.001))

            else:
                raise NotImplementedError

    elif software == 'opensees':

        coms = ' '.join([str(com[dof]) for dof in dofs[:ndof]])

        for node in nodes:

            if isinstance(node, str):
                for i in sets[node]['selection']:
                    f.write('load {0} {1}\n'.format(i + 1, coms))

            else:
                f.write('load {0} {1}\n'.format(node + 1, coms))

        f.write('#\n')

    elif software == 'opensees':

        pass


def _write_sofistik_loads_displacements(f, sets, displacements, loads, steps, structure):

    f.write('$ -----------------------------------------------------------------------------\n')
    f.write('$ ----------------------------------------------------------------------- Loads\n')
    f.write('$\n')
    f.write('+PROG SOFILOAD\n')

    for k in sorted(loads):

        load  = loads[k]
        ltype = load.__name__
        com   = getattr(load, 'components', None)
        axes  = getattr(load, 'axes', None)
        temp  = getattr(load, 'temperature', None)
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
            f.write("LC {0} TITL '{1}'\n".format(load.index + 1, k))

            if ltype == 'PointLoad':
                _write_point_load(f, 'sofistik', com, nodes, 6, sets, 1)

            elif ltype == 'PointLoads':
                _write_point_loads(f, 'sofistik', com, 1)

            elif ltype == 'LineLoad':
                _write_line_load(f, 'sofistik', axes, com, 1, elset, sets, structure)

            elif ltype == 'PrestressLoad':
                _write_prestress_load(f, 'sofistik', elset, com)

            elif ltype == 'TributaryLoad':
                _write_tributary_load(f, 'sofistik', com, 1)

            elif ltype == 'AreaLoad':
                _write_area_load(f, 'sofistik', com, axes, elset, sets, 1)

            elif ltype == 'ThermalLoad':
                _write_thermal_load(f, 'sofistik', elset, temp, sets,  1)

            f.write('$\n')

    for k in sorted(displacements):

        bcs = steps[structure.steps_order[0]].displacements
        if isinstance(bcs, str):
            bcs = [bcs]

        if k not in bcs:

            displacement = displacements[k]
            displacement_index = displacement.index + 1 + len(loads)
            com   = displacement.components
            nodes = displacement.nodes

            f.write('$ {0}\n'.format(k))
            f.write('$ ' + '-' * len(k) + '\n')
            f.write('$\n')
            f.write("LC {0} TITL '{1}'\n".format(displacement_index, k))

            _write_displacements(f, 'sofistik', com, nodes, 1, sets, 6)

            f.write('$\n')


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
                    for j in 'xyz':
                        if com[j]:
                            f.write('    BEAM {0} TYPE P{1}{1} {2}[kN/m]\n'.format(ni, j.upper(), com['x'] * 0.001))

                elif axes == 'local':
                    for j, jj in zip('xyz', 'zxy'):
                        if com[jj]:
                            f.write('    BEAM {0} TYPE P{1} {2}[kN/m]\n'.format(ni, j.upper(), com[jj] * 0.001))

        elif software == 'ansys':

            pass


def _write_area_load(f, software, com, axes, elset, sets, factor):

    if software == 'abaqus':

        for k in elset:

            if axes == 'global':

                raise NotImplementedError

            elif axes == 'local':
                # x COMPONENT
                # y COMPONENT
                f.write('*DLOAD\n')
                f.write('**\n')

                if com['z']:
                    f.write('{0}, P, {1}'.format(k, factor * com['z']) + '\n')

    elif software == 'opensees':

        pass

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

    gx = com.get('x', 0)
    gy = com.get('y', 0)
    gz = com.get('z', 0)

    if software == 'abaqus':

        for k in elset:

            f.write('*DLOAD\n')
            f.write('**\n')
            f.write('{0}, GRAV, {1}, {2}, {3}, {4}\n'.format(k, g * factor, gx, gy, gz))
            f.write('**\n')

    elif software == 'sofistik':

        pass

    elif software == 'opensees':

        f.write('# GravityLoad not yet implemented for OpenSees')

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

    elif software == 'sofistik':

        pass

    elif software == 'opensees':

        pass

    elif software == 'ansys':

        pass

    for node in sorted(com, key=int):
        ni = node + 1

        if software == 'abaqus':

            for ci, dof in enumerate(dofs[:3], 1):
                if com[node][dof]:
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

            set_index = sets[k]['index'] + 1
            f.write('    QUAD GRP {0} TYPE {1} {2}\n'.format(set_index, 'DTXY', temperature))

        elif software == 'opensees':

                pass

        elif software == 'ansys':

            pass


def _write_opensees_output(f, fields, ndof, temp, key, structure, tolerance, iterations, increments):

    f.write('}\n')

    # Node recorders

    output = {}

    if 'u' in fields:
        output['u.out'] = '1 2 3 disp'

    if 'rf' in fields:
        output['rf.out'] = '1 2 3 reaction'

    if ndof == 6:

        if 'ur' in fields:
            output['ur.out'] = '4 5 6 disp'

        if 'rm' in fields:
            output['rm.out'] = '4 5 6 reaction'

    f.write('#\n')
    f.write('# Node recorders\n')
    f.write('# --------------\n')
    f.write('#\n')

    prefix = 'recorder Node -file {0}{1}_'.format(temp, key)
    for k, j in output.items():
        f.write('{0}{1} -time -nodeRange {2} -dof {3}\n'.format(prefix, k, '1 {0}'.format(structure.node_count()), j))


    # Sort elements

    truss_elements = ''
    truss_ekeys    = []
    # beam_elements = ''
    # spring_elements = ''
    # beam_numbers = []
    # spring_numbers = []

    for ekey, element in structure.elements.items():
        etype = element.__name__

        if etype in ['TrussElement', 'StrutElement', 'TieElement']:
            truss_elements += '{0} '.format(ekey + 1)
            truss_ekeys.append(ekey)

    #     elif etype in ['BeamElement']:
    #         beam_elements += '{0} '.format(ekey + 1)
    #         beam_numbers.append(ekey)

    #     elif etype in ['SpringElement']:
    #         spring_elements += '{0} '.format(ekey + 1)
    #         spring_numbers.append(ekey)


    # Element recorders

    f.write('#\n')
    f.write('# Element recorders\n')
    f.write('# -----------------\n')

    prefix = 'recorder Element -file {0}{1}_'.format(temp, key)

    if 'sf' in fields:

        if truss_elements:
            f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, 'sf_truss.out', truss_elements, 'axialForce'))

    #     if beam_elements:
    #         k = 'element_beam_sf.out'
    #         j = 'force'
    #         f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, k, beam_elements, j))

    # if 'spf' in fields:

    #     if spring_elements:
    #         k = 'element_spring_sf.out'
    #         j = 'basicForces'
    #         f.write('{0}{1} -time -ele {2}{3}\n'.format(prefix, k, spring_elements, j))


    # ekeys

    with open('{0}truss_ekeys.json'.format(temp), 'w') as fo:
        json.dump({'truss_ekeys': truss_ekeys}, fo)

    # with open('{0}beam_numbers.json'.format(temp), 'w') as fo:
    #     json.dump({'beam_numbers': beam_numbers}, fo)

    # with open('{0}spring_numbers.json'.format(temp), 'w') as fo:
    #     json.dump({'spring_numbers': spring_numbers}, fo)


    # Solver

    f.write('#\n')
    f.write('# Solver\n')
    f.write('# ------\n')
    f.write('#\n')

    # # f.write('constraints Plain\n')
    f.write('constraints Transformation\n')
    f.write('numberer RCM\n')
    f.write('system ProfileSPD\n')
    f.write('test NormUnbalance {0} {1} 5\n'.format(tolerance, iterations))
    f.write('algorithm NewtonLineSearch\n')
    f.write('integrator LoadControl {0}\n'.format(1./increments))
    f.write('analysis Static\n')
    f.write('analyze {0}\n'.format(increments))


def _write_abaqus_output(f, fields, structure):

    if isinstance(fields, list):
        fields = structure.fields_dict_from_list(fields)

    if 'spf' in fields:
        fields['ctf'] = 'all'
        del fields['spf']

    f.write('**\n')
    f.write('*OUTPUT, FIELD\n')
    f.write('**\n')

    f.write('*NODE OUTPUT\n')
    f.write('**\n')
    f.write(', '.join([i.upper() for i in ['rf', 'rm', 'u', 'ur', 'cf', 'cm'] if i in fields]) + '\n')
    f.write('**\n')

    f.write('*ELEMENT OUTPUT\n')
    f.write('**\n')
    f.write(', '.join([i.upper() for i in ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'ctf']
                       if (i in fields and i != 'rbfor')]) + '\n')

    if 'rbfor' in fields:
        f.write('*ELEMENT OUTPUT, REBAR\n')
        f.write('RBFOR\n')

    f.write('**\n')
    f.write('*END STEP\n')


def _write_sofistik_output(f, stype, properties, state, step_index, key, nlgeom, increments, tolerance, nlmat, loads,
                           factor, materials):

    f.write('END\n$\n$\n')

    has_concrete = False
    for material in materials.values():
        if material.__name__ in ['Concrete', 'ConcreteSmearedCrack', 'ConcreteDamagedPlasticity']:
            has_concrete = True

    if stype != 'BucklingStep':

        # Rebar

        has_rebar = False
        for property in properties.values():
            if property.reinforcement:
                has_rebar = True
                break

        if has_rebar:

            f.write('+PROG BEMESS\n')
            f.write("HEAD REBAR {0} LC 1{1:0>2}00\n".format(state.upper(), step_index))
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
            f.write('LC 1{0:0>2}00\n'.format(step_index))
            f.write('$\n')
            f.write('$\n')
            f.write('END\n')
            f.write('$\n')
            f.write('$\n')

        # Primary analysis

        f.write('+PROG ASE\n')
        f.write("HEAD SOLVE {0} LC 2{1:0>2}00 {2}\n".format(state.upper(), step_index, key))
        f.write('$\n')
        f.write('CTRL SOLV 1\n')

        if has_concrete:
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

        if has_concrete:
            f.write('REIQ LCR {0}\n'.format(step_index))
        f.write('$\n')

        DLX, DLY, DLZ = 0, 0, 0
        for load in loads.values():
            if load.__name__ == 'GravityLoad':
                com = load.components
                DLX = com.get('x', 0)
                DLY = com.get('y', 0)
                DLZ = com.get('z', 0)
                break

        if isinstance(factor, dict):
            fact = factor.get('g', 1.0)
        else:
            fact = factor

        f.write('$\n')
        f.write("LC 2{0:0>2}00 TITL '{1}'".format(step_index, key))
        f.write(' DLX {0} DLY {1} DLZ {2}\n'.format(DLX * fact, DLY * fact, DLZ * fact))
        f.write('    LCC 1{0:0>2}00 PLC YES\n'.format(step_index))

        f.write('$\n')
        f.write('END\n')
        f.write('$\n')
        f.write('$\n')

        # Creep

        if has_concrete:

            f.write('+PROG ASE\n')
            f.write("HEAD CREEP {0} LC 3{1:0>2}00 {2}\n".format(state.upper(), step_index, key))
            f.write('$\n')
            f.write('CTRL SOLV 1\n')
            f.write('CTRL CONC\n')
            f.write('CREP NCRE 5\n')
            if nlgeom == 'YES':
                f.write('SYST PROB TH3 ITER {0} TOL {1} NMAT {2} PLC 2{3:0>2}00\n'.format(
                        increments, tolerance, nlmat, step_index))
            f.write('GRP ALL FACS 1.00 PHI 1.00 PHIF 0 EPS -0.0005\n')
            f.write('REIQ LCR {0}\n'.format(step_index))
            f.write('$\n')

            DLX, DLY, DLZ = 0, 0, 0
            for load in loads.values():
                if load.__name__ == 'GravityLoad':
                    com = load.components
                    DLX = com.get('x', 0)
                    DLY = com.get('y', 0)
                    DLZ = com.get('z', 0)
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
