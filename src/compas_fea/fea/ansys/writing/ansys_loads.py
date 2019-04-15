import os


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def add_load_to_ploads(structure, pload, load, factor):
    nodes = load.nodes

    if type(nodes) == str:
        nkeys = structure.sets[nodes].selection
    elif type(nodes) == list:
        nkeys = nodes
    for nkey in nkeys:
        if nkey not in pload.keys():
            pload[nkey] = {'x': 0, 'y': 0, 'z': 0, 'xx': 0, 'yy': 0, 'zz': 0}
        if load.__name__ == 'TributaryLoad':
            components = load.components[nkey]
        else:
            components = load.components

        for ckey in components:
            value = components[ckey]
            if value != 0:
                pload[nkey][ckey] += value * factor
    return pload


def write_loads(structure, output_path, filename, loads, factor):
    # TODO: Implement all load types
    pload = {}
    if loads:
        if type(loads) != list:
            loads = [loads]

        for index, lkey in enumerate(loads):
            load = structure.loads[lkey]
            if load.__name__ == 'GravityLoad':
                gravity = load.g
                write_gravity_loading(structure, output_path, filename, gravity, factor)
            elif load.__name__ == 'PointLoad' or load.__name__ == 'HarmonicPointLoad':
                # write_apply_nodal_load(structure, output_path, filename, lkey, factor)
                pload = add_load_to_ploads(structure, pload, load, factor)
            elif load.__name__ == 'TributaryLoad':
                # write_appply_tributary_load(structure, output_path, filename, lkey, factor)
                pload = add_load_to_ploads(structure, pload, load, factor)
            elif load.__name__ == 'HarmonicPressureLoad':
                write_apply_harmonic_pressure_load(structure, output_path, filename, lkey, factor, index)
            elif load.__name__ == 'AcousticDiffuseFieldLoad':
                write_apply_acoustic_diffuse_field_load(structure, output_path, filename, lkey, index)
            else:
                raise ValueError(load.__name__ + ' Type of load is not yet implemented for Ansys')
        write_combined_point_loads(pload, output_path, filename)


def write_combined_point_loads(pload, output_path, filename):
    cFile = open(os.path.join(output_path, filename), 'a')
    # cFile.write('/PREP7 \n')
    axis_dict = {'x': 'X', 'y': 'Y', 'z': 'Z', 'xx': 'MX', 'yy': 'MY', 'zz': 'MZ'}

    nkeys = sorted(pload.keys(), key=int)
    for nkey in nkeys:
        components = pload[nkey]
        node = int(nkey) + 1
        for ckey in components:
            value = components[ckey]
            if value != 0:
                forceString = 'F' + axis_dict[ckey]
                string = 'F,' + str(node) + ',' + forceString + ',' + str(value) + '\n'
                cFile.write(string)

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_appply_tributary_load(structure, output_path, filename, lkey, factor):
    cFile = open(os.path.join(output_path, filename), 'a')
    nkeys = structure.loads[lkey].components
    axis_dict = {'x': 'X', 'y': 'Y', 'z': 'Z', 'xx': 'MX', 'yy': 'MY', 'zz': 'MZ'}
    for nkey in nkeys:
        components = structure.loads[lkey].components[nkey]
        node = int(nkey) + 1
        for ckey in components:
            value = components[ckey]
            if value != 0:
                value *= factor
                forceString = 'F' + axis_dict[ckey]
                string = 'F,' + str(node) + ',' + forceString + ',' + str(value) + '\n'
                cFile.write(string)

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_apply_nodal_load(structure, output_path, filename, lkey, factor):
    cFile = open(os.path.join(output_path, filename), 'a')
    axis_dict = {'x': 'X', 'y': 'Y', 'z': 'Z', 'xx': 'MX', 'yy': 'MY', 'zz': 'MZ'}

    nodes = structure.loads[lkey].nodes
    if type(nodes) == str:
        nkeys = structure.sets[nodes]['selection']
    elif type(nodes) == list:
        nkeys = nodes
    for nkey in nkeys:
        components = structure.loads[lkey].components
        node = int(nkey) + 1
        for ckey in components:
            value = components[ckey]
            if value != 0:
                value *= factor
                forceString = 'F' + axis_dict[ckey]
                string = 'F,' + str(node) + ',' + forceString + ',' + str(value) + '\n'
                cFile.write(string)

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_gravity_loading(structure, output_path, filename, gravity, factor):
    cFile = open(os.path.join(output_path, filename), 'a')
    gravity = abs(gravity) * factor
    cFile.write('ACEL,0,0,' + str(gravity) + ',\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_apply_harmonic_pressure_load(structure, output_path, filename, lkey, factor, index):
    load_elements = structure.loads[lkey].elements
    if type(load_elements) != list:
        load_elements = [load_elements]
    elements = []
    for element in load_elements:
        if type(element) == str:
            elements.extend(structure.sets[element]['selection'])
            add = structure.element_count()
        else:
            elements.append(element)
            add = 0

    pressure = structure.loads[lkey].components['pressure']
    phase = structure.loads[lkey].components['phase']

    cFile = open(os.path.join(output_path, filename), 'a')
    string = 'SFE, {0}, {1}, PRES, {2}, {3} \n'
    for ekey in elements:
        ekey += add
        string_ = string.format(ekey + 1, '', 1, pressure)
        cFile.write(string_)
        if phase:
            string_ = string.format(ekey + 1, '', 2, phase)
            cFile.write(string_)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_apply_acoustic_diffuse_field_load(structure, output_path, filename, lkey, index):

    denst = structure.loads[lkey].components['air_density']
    speed = structure.loads[lkey].components['sound_speed']
    angle = structure.loads[lkey].components['max_inc_angle']
    string = 'DFSWAVE, 0, , ,{0}, {1}, {2}, ,ALL'.format(denst, speed, angle)
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
