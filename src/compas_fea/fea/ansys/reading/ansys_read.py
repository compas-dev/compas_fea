import os


def get_nodes_elements_from_result_files(path):
    try:
        node_file    = open(path + 'output/nodes.txt', 'r')
    except:
        node_file = None
    try:
        elementFile    = open(path + 'output/elements.txt', 'r')
    except:
        elementFile = None

    elem_type_dict = {1: 'shell8', 2: 'shell4', 3: 'beam', 4: 'tie', 5: 'solid8'}
    nodes = {}
    elements = {}
    if node_file and elementFile:
        node_lines = node_file.readlines()
        elements_lines = elementFile.readlines()

        for i in range(len(node_lines)):
            node_string = node_lines[i].split(',')
            nkey = int(float(node_string[0])) - 1
            nodes[nkey] = {'x': float(node_string[1]),
                           'y': float(node_string[2]),
                           'z': float(node_string[3])}

        for i in range(len(elements_lines)):
            topology, attr = elements_lines[i].split(',')
            topology = topology.split()
            attr = attr.split()
            topology = map(float, topology)
            topology[:] = [int(x - 1) for x in topology if x != 0]
            attr = map(float, attr)
            elem_type, mat_index, sec_index = map(int, attr)
            elem_type = elem_type_dict[elem_type]
            elements[str(i)] = {'topology': topology, 'sec': sec_index,
                                'mat': mat_index, 'elem_type': elem_type}

    return nodes, elements


def get_harmonic_data_from_result_files(path):
    harmonic_path = path + 'output/harmonic_out'
    files = os.listdir(harmonic_path)

    real_files = []
    imag_files = []
    real_names = []
    imag_names = []
    for f in files:
        if f.startswith("node_real"):
            real_names.append(f)
        elif f.startswith("node_imag"):
            imag_names.append(f)

    for i, f in enumerate(real_names):
        f = 'node_real_' + str(i + 1) + '.txt'
        f = open(harmonic_path + '/' + f, 'r')
        dreal = f.readlines()
        real_files.append(dreal)
        f.close()

    for i, f in enumerate(imag_names):
        f = 'node_imag_' + str(i + 1) + '.txt'
        f = open(harmonic_path + '/' + f, 'r')
        dimag = f.readlines()
        imag_files.append(dimag)
        f.close()

    harmonic_disp = {}
    if real_files:
        for i in range(len(real_files)):
            dreal = real_files[i]
            dimag = imag_files[i]

            harmonic_disp[i] = {}
            for j in range(len(dreal)):
                real_string = dreal[j].split(',')
                imag_string = dimag[j].split(',')
                f = int(float(real_string[0]))
                del real_string[0]
                del imag_string[0]
                real = map(float, real_string)
                imag = map(float, imag_string)
                harmonic_disp[i][f] = {'real': {'x': real[0], 'y': real[1], 'z': real[2]},
                                                 'imag': {'x': imag[0], 'y': imag[1], 'z': imag[2]}}

    freq_list = sorted(harmonic_disp[i].keys(), key=int)
    freq_list = [int(fr) for fr in freq_list]
    return harmonic_disp, freq_list


def get_modal_data_from_result_files(path):
    modal_path = path + 'output/modal_out/'
    try:
        files = os.listdir(modal_path)
    except:
        print ('Result files not found')
        return None, None
    filenames = []
    for f in files:
        if f.startswith("modal_shape_"):
            filenames.append(f)
    modal_files = []
    for i in range(len(filenames)):
        f = 'modal_shape_' + str(i + 1) + '.txt'
        modal_files.append(open(modal_path + '/' + f, 'r'))

    if modal_files:
        modes_dict = {}
        for i, f in enumerate(modal_files):
            mode = f.readlines()
            modes_dict[i] = {}
            for j in range(len(mode)):
                string = mode[j].split(',')
                del string[0]
                a = map(float, string)
                modes_dict[i][j] = {'x': a[0], 'y': a[1], 'z': a[2]}
            f.close()
        # num_modes = len(modal_files)
        # modal_analysis = True
    else:
        modes_dict = None
        # num_modes  = None
        # modal_analysis = None

    modal_freq_file = open(modal_path + 'modal_freq.txt', 'r')

    if modal_freq_file:
        modal_freqs = {}
        freqs = modal_freq_file.readlines()
        for freq in freqs:
            string = freq.split(',')
            modal_freqs[int(float(string[0])) - 1] = float(string[1])
    else:
        modal_freqs = None

    # data = {'modal_shapes': modes_dict, 'num_modes': num_modes,
    #         'modal_analysis': modal_analysis, 'modal_freqs': modal_freqs}
    return modes_dict, modal_freqs


def get_displacements_from_result_files(path):
    try:
        displacements_file = open(path + 'output/displacements.txt', 'r')
    except:
        displacements_file = None
    if displacements_file:
        displacements = displacements_file.readlines()

        disp_dict = {}
        for i in range(len(displacements)):
            dispString = displacements[i].split(',')
            del dispString[0]
            displacement = map(float, dispString)
            disp_dict[str(i)] = {'x': displacement[0], 'y': displacement[1], 'z': displacement[2]}
    else:
        disp_dict = None

    return disp_dict


def get_nodal_stresses_from_result_files(path):
    try:
        stresses_file   = open(path + 'output/nodal_stresses_.txt', 'r')
    except:
        stresses_file = None

    if stresses_file:
        stresses = stresses_file.readlines()

        stress_dict = {}
        for i in range(len(stresses)):
            stressString = stresses[i].split(',')
            del stressString[0]
            stress = []
            for string in stressString:
                try:
                    s = float(string)
                except:
                    s = None
                stress.append(s)
            stress_dict[str(i)] = {'top': {'x': stress[3], 'y': stress[4], 'z': stress[5]},
                                   'bot': {'x': stress[0], 'y': stress[1], 'z': stress[2]}}
    else:
        stress_dict = None
    return stress_dict


def get_principal_streses(path):
    try:
        p_stresses_file   = open(path + 'output/principal_stresses_.txt', 'r')
    except:
        p_stresses_file = None

    if p_stresses_file:
        p_stresses = p_stresses_file.readlines()

        p_stress_dict = {}
        for i in range(len(p_stresses)):
            p_stress_string = p_stresses[i].split(',')
            del p_stress_string[0]
            p_stress = []
            for string in p_stress_string:
                try:
                    s = float(string)
                except:
                    s = None
                p_stress.append(s)
            p_stress_dict[str(i)] = {'top': {'1': p_stress[3], '2': p_stress[4], '3': p_stress[5]},
                                     'bot': {'1': p_stress[0], '2': p_stress[1], '3': p_stress[2]}}
    else:
        p_stress_dict = None
    return p_stress_dict


def get_shear_stresses_from_result_files(path):
    try:
        shear_stresses_file   = open(path + 'output/shear_stresses_.txt', 'r')
    except:
        shear_stresses_file = None

    if shear_stresses_file:
        shear_stresses = shear_stresses_file.readlines()

        shear_stress_dict = {}
        for i in range(len(shear_stresses)):
            shear_stress_string = shear_stresses[i].split(',')
            del shear_stress_string[0]
            shear_stress = []
            for string in shear_stress_string:
                try:
                    s = float(string)
                except:
                    s = None
                shear_stress.append(s)
            shear_stress_dict[str(i)] = {'top': {'xy': shear_stress[3], 'yz': shear_stress[4], 'xz': shear_stress[5]},
                                         'bot': {'xy': shear_stress[0], 'yz': shear_stress[1], 'xz': shear_stress[2]}}
    else:
        shear_stress_dict = None
    return shear_stress_dict


def get_principal_strains_from_result_files(path):
    try:
        p_strains_file   = open(path + 'output/principal_strains.txt', 'r')
    except:
        p_strains_file = None

    if p_strains_file:
        p_strains = p_strains_file.readlines()

        p_strain_dict = {}
        for i in range(len(p_strains)):
            p_strainstring = p_strains[i].split(',')
            del p_strainstring[0]
            p_strain = []
            for string in p_strainstring:
                try:
                    s = float(string)
                except:
                    s = None
                p_strain.append(s)
            p_strain_dict[str(i)] = {'top': {'1': p_strain[3], '2': p_strain[4], '3': p_strain[5]},
                                     'bot': {'1': p_strain[0], '2': p_strain[1], '3': p_strain[2]}}
    else:
        p_strain_dict = None
    return p_strain_dict


def get_reactions_from_result_files(path):

    try:
        reactions_file   = open(path + 'output/reactions.txt', 'r')
    except:
        reactions_file = None

    if reactions_file:
        reactions = reactions_file.readlines()

        react_dict = {}
        for i in range(len(reactions)):
            react_string = reactions[i].split(',')
            del react_string[0]
            reaction = []
            for string in react_string:
                try:
                    s = float(string)
                except:
                    s = None
                reaction.append(s)
            if all(v == 0.0 for v in reaction) is False:
                react_dict[str(i)] = {'m': {'x': reaction[3], 'y': reaction[4], 'z': reaction[5]},
                                      'f': {'x': reaction[0], 'y': reaction[1], 'z': reaction[2]}}
    else:
        react_dict = None

    return react_dict


if __name__ == '__main__':
    path = '/Users/mtomas/Desktop/ansys_test/'
    nodes, elements = get_nodes_elements_from_result_files(path)
    disp = get_displacements_from_result_files(path)
    stress = get_nodal_stresses_from_result_files(path)
    pstress = get_principal_streses(path)
    shear = get_shear_stresses_from_result_files(path)
    pstrain = get_principal_strains_from_result_files(path)
    react = get_reactions_from_result_files(path)
    harmonic_disp, freq_list = get_harmonic_data_from_result_files(path)
    modes_dict, modal_freqs = get_modal_data_from_result_files(path)

    print react
