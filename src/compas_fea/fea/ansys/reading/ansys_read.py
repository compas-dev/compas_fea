import os
from compas.geometry import length_vector


def get_nodes_elements_from_result_files(path):
    try:
        node_file    = open(os.path.join(path, 'nodes.txt'), 'r')
    except(Exception):
        node_file = None
    try:
        elementFile    = open(os.path.join(path, 'elements.txt'), 'r')
    except(Exception):
        elementFile = None

    # elem_type_dict = {1: 'ShellElement', 2: 'ShellElement', 3: 'BeamElement', 4: 'TieElement', 5: 'SolidElement'}
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

            if len(topology) == 2:
                elem_type = 'TieElement'
            else:
                elem_type = 'ShellElement'
            elements[i] = {'nodes': topology, 'sec': sec_index,
                           'mat': mat_index, 'type': elem_type}

    return nodes, elements


def _get_harmonic_data_from_result_files(path): #  this function works with multiple freqs per step (the old way?)
    harmonic_path = os.path.join(path, 'harmonic_out')
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

    nkeys = [int(float(n.split('_')[2].split('.')[0])) - 1 for n in real_names]

    for i, f in enumerate(real_names):
        f = open(os.path.join(harmonic_path, f), 'r')
        dreal = f.readlines()
        real_files.append(dreal)
        f.close()

    for i, f in enumerate(imag_names):
        f = open(os.path.join(harmonic_path, f), 'r')
        dimag = f.readlines()
        imag_files.append(dimag)
        f.close()

    harmonic_disp = {}
    if real_files:
        for i in range(len(real_files)):
            dreal = real_files[i]
            dimag = imag_files[i]
            nkey = nkeys[i]

            harmonic_disp[nkey] = {}
            for j in range(len(dreal)):
                real_string = dreal[j].split(',')
                imag_string = dimag[j].split(',')
                f = int(float(real_string[0]))
                del real_string[0]
                del imag_string[0]
                real = map(float, real_string)
                imag = map(float, imag_string)
                harmonic_disp[nkey][f] = {'real': {'x': real[0], 'y': real[1], 'z': real[2]},
                                          'imag': {'x': imag[0], 'y': imag[1], 'z': imag[2]}}

    freq_list = sorted(harmonic_disp[nkey].keys(), key=int)
    freq_list = [int(fr) for fr in freq_list]
    return harmonic_disp, freq_list


def get_harmonic_data_from_result_files(structure, path, step):

    freq = structure.steps[step].freq_list[0]
    harmonic_path = os.path.join(path, 'harmonic_out')
    filename  = 'harmonic_disp_real_{0}_Hz.txt'.format(freq)
    filename_ = 'harmonic_disp_imag_{0}_Hz.txt'.format(freq)

    fh = open(os.path.join(harmonic_path, filename), 'r')
    dreal = fh.readlines()
    fh.close()

    fh = open(os.path.join(harmonic_path, filename_), 'r')
    dimag = fh.readlines()
    fh.close()

    harmonic_disp = {}
    for j in range(len(dreal)):
        real_string = dreal[j].split(',')
        imag_string = dimag[j].split(',')
        nkey = int(float(real_string[0]) - 1)
        del real_string[0]
        del imag_string[0]
        harmonic_disp[nkey] = {}
        real = map(float, real_string)
        imag = map(float, imag_string)
        harmonic_disp[nkey][freq] = {'real': {'x': real[0], 'y': real[1], 'z': real[2]},
                                     'imag': {'x': imag[0], 'y': imag[1], 'z': imag[2]}}

    return harmonic_disp, structure.steps[step].freq_list


def get_modal_shapes_from_result_files(out_path):
    modal_path = os.path.join(out_path, 'modal_out')
    try:
        files = os.listdir(modal_path)
    except(Exception):
        print ('Result files not found')
        return None, None
    filenames = []
    for f in files:
        if f.startswith('modal_shape_'):
            filenames.append(f)
    modal_files = []
    for i in range(len(filenames)):
        f = 'modal_shape_' + str(i + 1) + '.txt'
        modal_files.append(open(os.path.join(modal_path, f), 'r'))

    modes_dict = {}
    for i, f in enumerate(modal_files):
        modes_dict['ux' + str(i)] = {}
        modes_dict['uy' + str(i)] = {}
        modes_dict['uz' + str(i)] = {}
        modes_dict['um' + str(i)] = {}
        mode = f.readlines()
        for j in range(len(mode)):
            string = mode[j].split(',')
            a = map(float, string)
            nkey = int(a[0]) - 1
            modes_dict['ux' + str(i)][nkey] = a[1]
            modes_dict['uy' + str(i)][nkey] = a[2]
            modes_dict['uz' + str(i)][nkey] = a[3]
            modes_dict['um' + str(i)][nkey] = length_vector((a[1], a[2], a[3]))
        f.close()

    return modes_dict


def get_modal_freq_from_result_files(out_path):
    print(out_path)
    modal_path = os.path.join(out_path, 'modal_out')
    modal_freq_file = open(os.path.join(modal_path, 'modal_freq.txt'), 'r')
    if modal_freq_file:
        modal_freqs = {}
        freqs = modal_freq_file.readlines()
        for freq in freqs:
            string = freq.split(',')
            modal_freqs[int(float(string[0])) - 1] = float(string[1])
    else:
        modal_freqs = None

    return modal_freqs


def get_displacements_from_result_files(out_path, step):
    filename = step + '_displacements.txt'

    try:
        dfile = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None
    displacements = dfile.readlines()
    disp_dict = {}
    for i in range(len(displacements)):
        dstring = displacements[i].split(',')
        disp = map(float, dstring)
        key = int(disp[0]) - 1
        disp_dict[key] = {'ux': disp[1], 'uy': disp[2], 'uz': disp[3]}

    return disp_dict


def get_nodal_stresses_from_result_files(out_path, step):
    filename = step + '_nodal_stresses.txt'
    try:
        sfile   = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None

    s = sfile.readlines()
    stress_dict = {}
    for i in range(len(s)):
        s_string = s[i].split(',')
        stress = map(float, s_string)
        key = int(stress[0]) - 1
        stress_dict[key] = {'sxt': stress[4], 'syt': stress[5], 'szt': stress[6],
                            'sxb': stress[1], 'syb': stress[2], 'szb': stress[3]}
    return stress_dict


def get_principal_stresses_from_result_files(out_path, step):
    filename = step + '_principal_stresses.txt'
    try:
        psfile   = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None

    ps = psfile.readlines()
    p_stress_dict = {}
    for i in range(len(ps)):
        psstring = ps[i].split(',')
        p_stress = map(float, psstring)
        key = int(p_stress[0]) - 1
        p_stress_dict[key] = {'ps1t': p_stress[3], 'ps2t': p_stress[4], 'ps3t': p_stress[5],
                              'ps1b': p_stress[0], 'ps2b': p_stress[1], 'ps3b': p_stress[2]}
    return p_stress_dict


def get_shear_stresses_from_result_files(out_path, step):

    filename = step + '_shear_stresses.txt'
    try:
        psfile = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None

    ss = psfile.readlines()
    ss_dict = {}
    for i in range(len(ss)):
        ss_string = ss[i].split(',')
        ss_stress = map(float, ss_string)
        key = int(ss_stress[0]) - 1
        ss_dict[key] = {'sxyt': ss_stress[3], 'syzt': ss_stress[4], 'sxzt': ss_stress[5],
                        'sxyb': ss_stress[0], 'syzb': ss_stress[1], 'sxzb': ss_stress[2]}
    return ss_dict


def get_principal_strains_from_result_files(out_path, step):
    filename = step + '_principal_strains.txt'
    try:
        efile   = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None
    pe = efile.readlines()
    pe_dict = {}
    for i in range(len(pe)):
        estring = pe[i].split(',')
        p_strain = map(float, estring)
        key = int(p_strain[0]) - 1
        pe_dict[key] = {'e1t': p_strain[4], 'e2t': p_strain[5], 'e3t': p_strain[6],
                        'e1b': p_strain[1], 'e2b': p_strain[2], 'e3b': p_strain[3]}
    return pe_dict


def get_reactions_from_result_files(out_path, step):
    filename = step + '_reactions.txt'
    try:
        rfile   = open(os.path.join(out_path, filename), 'r')
    except(Exception):
        return None
    r = rfile.readlines()
    react_dict = {}
    for i in range(len(r)):
        r_string = r[i].split(',')
        reaction = map(float, r_string)
        key = int(reaction[0]) - 1
        if all(v == 0.0 for v in reaction) is False:
            react_dict[key] = {'rxx': reaction[3], 'ryy': reaction[4], 'rzz': reaction[5],
                               'rx': reaction[0], 'ry': reaction[1], 'rz': reaction[2]}
    return react_dict


if __name__ == '__main__':
    pass
